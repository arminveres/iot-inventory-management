import asyncio
import json
import os
import sys
from datetime import date

from agents.agent_container import (
    CRED_PREVIEW_TYPE,
    AgentContainer,
    AriesAgent,
    arg_parser,
    create_agent_with_args,
)
from support.agent import DEFAULT_INTERNAL_HOST
from support.database import OrionDB
from support.utils import log_json, log_msg, log_status, prompt, prompt_loop


# TODO: (aver) possibly separate databaes instance to own class
class IssuerAgent(AriesAgent):
    """
    This agent will be a credential issuer from the maintainer/manufacturer point of view.
    It also works as a database administrator, being able to create new users and keys, with
    complete control over Access Control
    """

    def __init__(
        self,
        ident: str,
        http_port: int,
        admin_port: int,
        orion_db_url=f"http://{DEFAULT_INTERNAL_HOST}:6001",
        **kwargs,
    ):
        super().__init__(
            ident=ident, http_port=http_port, admin_port=admin_port, **kwargs
        )

        # TODO: (aver) find a better way to manage keys
        self.db_username = "admin"  # ident

        self.db_client = OrionDB(
            orion_db_url=orion_db_url,
            username=self.db_username,
            client_session=self.client_session,
        )

        # TODO: (aver) remove hardcoded self.connection_id
        self.connection_id = None
        self._connection_ready = None
        # TODO define a dict to hold credential attributes based on cred_def_id
        self.cred_state = {}
        self.cred_attrs = {}

    # =============================================================================================
    # Properties, getters and setters
    # =============================================================================================
    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()

    def reset_connection(self):
        """
        Temporary function to reset connections in order to allow for multiple connections to be
        made.
        """
        self._connection_ready = None
        self.connection_id = None

    # =============================================================================================
    # Webhook handler implementations
    # =============================================================================================
    async def handle_connections(self, message):
        conn_id = message["connection_id"]

        if (not self.connection_id) and message["rfc23_state"] == "invitation-sent":
            print(self.ident, "set connection id", conn_id)
            self.connection_id = conn_id

        if (
            message["connection_id"] == self.connection_id
            and message["rfc23_state"] == "completed"
            and (self._connection_ready and not self._connection_ready.done())
        ):
            self.log("Connected")
            self._connection_ready.set_result(True)

    async def handle_out_of_band(self, message):
        print("handle_out_of_band()")
        log_json(message)

    async def handle_issue_credential_v2_0(self, message):
        state = message["state"]
        cred_ex_id = message["cred_ex_id"]
        prev_state = self.cred_state.get(cred_ex_id)

        if prev_state == state:
            return  # ignore

        node_name = [
            i["value"]
            for i in message["cred_proposal"]["credential_preview"]["attributes"]
            if i["name"] == "controller_id"
        ][0]

        # TODO: (aver) remove hardcoded db-name
        response = await self.db_client.query_key("db1", node_name)

        if response is None:
            print(
                "\n\n\tsomething massively went wrong, if an existing db key is none!"
            )
            sys.exit(1)

        # update credentials
        response["cred_ex_id"] = cred_ex_id
        response["status"] = "valid"
        await self.db_client.record_key("db1", node_name, response)

        self.cred_state[cred_ex_id] = state
        self.log(f"Credential: state = {state}, cred_ex_id = {cred_ex_id}")

        if state == "request-received":
            # TODO issue credentials based on offer preview in cred ex record
            if not message.get("auto_issue"):
                await self.admin_POST(
                    f"/issue-credential-2.0/records/{cred_ex_id}/issue",
                    {"comment": f"Issuing credential, exchange {cred_ex_id}"},
                )

    async def handle_notify_vulnerability(self, message):
        """
        Handle vulnerabilities presented to the maintainer/admin/issuer
        """
        # FIXME: (aver) improve this 4 times nested loop !!!!
        log_msg("Received vulnearbility:")
        log_json(message)
        # Go through each vulnerability
        for vuln_notif in message:
            vuln_db_name = vuln_notif["db_name"]
            vulnerability = vuln_notif["vulnerability"]

            # mark devices to be revoked
            for device in self.db_client.db_keys[vuln_db_name]:
                response = await self.db_client.query_key(vuln_db_name, device)
                log_json(response)
                log_json(vulnerability)

                for component_key, component_value in response["components"].items():
                    for (
                        vuln_component_key,
                        vuln_component_value,
                    ) in vulnerability.items():
                        if not component_key == vuln_component_key:
                            continue
                        # find vulnerability that matches the marked one
                        if vuln_component_value.items() <= component_value.items():
                            log_msg(
                                f"Found existing vulnerability for device {device} with component \
                            {vuln_component_value}"
                            )
                            reason = {
                                "reason": "vulnerability",
                                "component": {vuln_component_key: vuln_component_value},
                            }
                            # TODO: (aver) use correct connection_id
                            await self.revoke_credential(
                                response["cred_ex_id"],
                                vuln_db_name,
                                device,
                                reason,
                            )

    # =============================================================================================
    # Additional methods
    # =============================================================================================
    async def revoke_credential(
        self,
        cred_ex_id: str,
        db_name: str,
        node_name: str,
        revocation_reason: dict,
    ):
        """
        Revoke a credentials and publish it.
        """
        response = await self.db_client.query_key(db_name, node_name)
        response["cred_ex_id"] = ""
        response["valid"] = False
        await self.db_client.record_key(db_name, node_name, response)

        # FIXME: (aver) remove hard coded connection_id and retrieve or store in database
        await self.admin_POST(
            "/revocation/revoke",
            {
                "cred_ex_id": cred_ex_id,
                "publish": True,
                "connection_id": self.db_client.db_keys[db_name][node_name][
                    "connection_id"
                ],
                "comment": json.dumps(revocation_reason),
            },
        )


# =================================================================================================
# Helper functions
# =================================================================================================
async def create_agent_container(args) -> AgentContainer:
    # First setup all the agent related stuff
    agent_container = await create_agent_with_args(args)
    agent_container.seed = "Autho_00000000000000000000000000"
    agent = IssuerAgent(
        ident=agent_container.ident,
        http_port=agent_container.start_port,
        admin_port=agent_container.start_port + 1,
        genesis_data=agent_container.genesis_txns,
        genesis_txn_list=agent_container.genesis_txn_list,
        no_auto=agent_container.no_auto,
        tails_server_base_url=agent_container.tails_server_base_url,
        revocation=agent_container.revocation,
        timing=agent_container.show_timing,
        multitenant=agent_container.multitenant,
        mediation=agent_container.mediation,
        wallet_name=agent_container.ident,
        # WARN: (aver) key is same as identity, which is insecure, watch out!
        wallet_key=agent_container.ident,
        wallet_type=agent_container.wallet_type,
        aip=agent_container.aip,
        endorser_role=agent_container.endorser_role,
        seed=agent_container.seed,
    )
    await agent_container.initialize(
        the_agent=agent,
    )
    return agent_container


async def send_message(agent_container: AriesAgent):
    message = {"content": f"hello from {agent_container.ident}!"}
    await agent_container.admin_POST(
        path=f"/connections/{agent_container.agent.connection_id}/send-message",
        data=message,
    )


async def checked_schema_cred_creation(
    agent_container: AgentContainer, schema_name, schema_attributes, schema_version
):
    try:
        # TODO: (aver) Improve handling of existing credentials, would need to go more into the
        # code. Although the whole code is so nested, I don't really see the possiblity for
        # it...
        agent_container.cred_def_id = await agent_container.create_schema_and_cred_def(
            schema_name, schema_attributes, schema_version
        )
    except Exception as e:
        # We check whether the exception is about the schema existing
        resp = str(e).find("exists")
        # if the exception was about something else, then we raise it againt
        if resp == -1:
            raise e
        # we need another way to get cred_def_id
        response = await agent_container.admin_GET(
            # "/credential-definitions/created/?issuer_did=did:sov:8BJ4EjbZM87wCasqjE1kt"
            "/credential-definitions/created"
        )
        log_json(response)
        agent_container.cred_def_id = response["credential_definition_ids"][0]


async def demo_setup(agent_container: AgentContainer):
    """
    Sets up pre_defined instance of the demo with fixed everything
    """
    # WARN: (aver) Only works with fixed seed for DIDs e.g., 'Node1_00000000000000000000000000'
    node_did = "did:sov:SYBqqHS7oYwthtCDNHi841"

    db_name = "db1"
    key_name = "Controller_1"
    await agent_container.agent.db_client.create_database(db_name)

    schema_name = "controller id schema"
    schema_attributes = ["controller_id", "date", "status"]
    schema_version = "0.0.1"

    # Currently the credential is of the same format as the entry to the database
    controller_1_cred = {
        "controller_id": "node0001",
        "date": date.isoformat(date.today()),
        "status": "valid",
    }

    # we extend the credential with components so that the auditor can register them
    db_entry = controller_1_cred.copy()
    db_entry["controller_did"] = node_did
    db_entry["components"] = {
        "software": {"python3": 3.9, "indy": 1.16, "shady_stuff": 0.9},
        "firmware": {},
        "hardware": {"asus-tinkerboard": 1.2},
    }
    # we create an auditor user, who then will mark software as vulnerable
    await agent_container.agent.db_client.create_user("auditor")

    await agent_container.agent.db_client.record_key(db_name, key_name, db_entry)

    await checked_schema_cred_creation(
        agent_container, schema_name, schema_attributes, schema_version
    )

    # TODO: find better way to post. It would make sense to create a unique/separate endpoint for
    # invitation requests, that then can be passed to the agent to be accepted.
    # Flow:
    #   1. Authority/Issuer creates invitation
    #   2. Targeted Agent receives and accepts

    # Take public DID from a DATABASE

    recipient_key = await agent_container.agent.send_invitation(node_did)
    # we set the recipient key for later identification
    agent_container.agent.db_client.db_keys[db_name][key_name][
        "recipient_key"
    ] = recipient_key

    # Set the connection id for each controller
    response = await agent_container.admin_GET("/connections")
    log_json(response)
    # TODO: (aver) remove hardcoded key_name and add logic for general key check
    # also remove hardcoded connection_id
    for conn in response["results"]:
        if conn["invitation_key"] == recipient_key:
            conn_id = conn["connection_id"]
            agent_container.agent.db_client.db_keys[db_name][key_name][
                "connection_id"
            ] = conn_id

    agent_container.agent._connection_ready = asyncio.Future()
    log_msg("Waiting for connection...")
    await agent_container.agent.detect_connection()

    log_status("#13 Issue credential offer to X")
    # TODO credential offers
    # WARN: this could be better handled for general usecases, here it is just for Alice
    agent_container.agent.cred_attrs[agent_container.cred_def_id] = controller_1_cred
    cred_preview = {
        "@type": CRED_PREVIEW_TYPE,
        "attributes": [
            {"name": n, "value": v}
            for (n, v) in agent_container.agent.cred_attrs[
                agent_container.cred_def_id
            ].items()
        ],
    }
    offer_request = {
        "connection_id": conn_id,
        "comment": f"Offer on cred def id {agent_container.cred_def_id}",
        "credential_preview": cred_preview,
        "filter": {"indy": {"cred_def_id": agent_container.cred_def_id}},
    }
    await agent_container.admin_POST("/issue-credential-2.0/send-offer", offer_request)


async def setup_database(agent_container: AgentContainer, db_name: str):
    """
    Setup the database, and register schema and credential on database
    """
    await agent_container.agent.db_client.create_database(db_name)

    schema_name = "controller id schema"
    schema_attributes = ["controller_id", "date", "status"]
    schema_version = "0.0.1"

    await checked_schema_cred_creation(
        agent_container, schema_name, schema_attributes, schema_version
    )
    log_msg(
        f"Setup database: '{db_name}' and schema '{schema_name}', '{schema_attributes}', {schema_version}"
    )
    # we create an auditor user, who then will mark software as vulnerable
    await agent_container.agent.db_client.create_user("auditor")
    log_status("Created auditor account")


async def onboard_node(
    agent_container: AgentContainer, domain: str, node_name: str, node_did: str
):
    """
    params:
        agent_container: AgentContainer,
        domain: str, database name, which also works as domain name
        node_name: str,
        node_did: str
    """
    # Currently the credential is of the same format as the entry to the database
    node_cred = {
        "controller_id": node_name,
        "date": date.isoformat(date.today()),
        "status": "valid",
    }

    # WARN: (aver) the did has to be amended with the method for the resolver to work
    node_did = "did:sov:" + node_did

    # we extend the credential with components so that the auditor can register them
    # NOTE: (aver) In an improved scenario, the config would be read in, instead of artificially
    # created
    db_entry = node_cred.copy()
    db_entry["controller_did"] = node_did
    db_entry["components"] = {
        "software": {"python3": 3.9, "indy": 1.16, "shady_stuff": 0.9},
        "firmware": {},
        "hardware": {"asus-tinkerboard": 1.2},
    }
    await agent_container.agent.db_client.record_key(domain, node_name, db_entry)

    recipient_key = await agent_container.agent.send_invitation(node_did)
    # we set the recipient key for later identification
    agent_container.agent.db_client.db_keys[domain][node_name][
        "recipient_key"
    ] = recipient_key

    agent_container.agent._connection_ready = asyncio.Future()
    log_msg("Waiting for connection...")
    await agent_container.agent.detect_connection()

    # Set the connection id for each controller
    response = await agent_container.admin_GET("/connections")
    log_json(response)
    # TODO: (aver) remove hardcoded key_name and add logic for general key check
    # also remove hardcoded connection_id
    for conn in response["results"]:
        if conn["invitation_key"] == recipient_key:
            conn_id = conn["connection_id"]
            agent_container.agent.db_client.db_keys[domain][node_name][
                "connection_id"
            ] = conn_id
            # remove recipient/invitation key
            agent_container.agent.db_client.db_keys[domain][node_name].pop(
                "recipient_key"
            )

    agent_container.agent.reset_connection()

    log_status(f"# Issuing credential offer to {node_name}")
    agent_container.agent.cred_attrs[agent_container.cred_def_id] = node_cred
    cred_preview = {
        "@type": CRED_PREVIEW_TYPE,
        "attributes": [
            {"name": n, "value": v}
            for (n, v) in agent_container.agent.cred_attrs[
                agent_container.cred_def_id
            ].items()
        ],
    }
    offer_request = {
        "connection_id": conn_id,
        "comment": f"Offer on cred def id {agent_container.cred_def_id}",
        "credential_preview": cred_preview,
        "filter": {"indy": {"cred_def_id": agent_container.cred_def_id}},
    }
    response = await agent_container.admin_POST(
        "/issue-credential-2.0/send-offer", offer_request
    )


async def load_from_database(db_name: str):
    # could create a local textfile to load in until the query all method works...
    pass


# =================================================================================================
# MAIN Function
# =================================================================================================
async def main(args):
    agent_container = await create_agent_container(args)
    db_name = "db1"

    try:
        # =========================================================================================
        # Event Loop
        # =========================================================================================
        # New prompt based event loop, events such as webhooks still run in the background.

        # Setup options and make them dicts, so that they can be changed at runtime
        options = {
            "setup_db": "  [1]: Setup Database, Schema and Credential\n",
            # "load": "  [3]: Load from database\n",
            "demo": "  [0]: Run demo by setting up databasa and schema, and using default DID\n",
            "exit": "  [x]: Exit\n",
        }

        def get_prompt():
            """
            Builds the prompt out of the options dictionary
            """
            options.update
            options_str = "Options:\n"
            for option in list(options.items()):
                options_str += option[1]
            options_str += "> "
            return options_str

        async for option in prompt_loop(get_prompt):
            if option is not None:
                option.strip()
            if option is None or option == "":
                log_msg("Please give an option")

            # run options
            if option == "1":
                if not options.get("setup_db"):
                    log_msg(f"invalid option, {option}")
                    continue

                await setup_database(agent_container, db_name)
                options.pop("setup_db")
                # add onboarding option
                options["onboard"] = "  [2]: Onboard node with public DID\n"
            elif option == "2":
                if not options.get("onboard"):
                    log_msg(f"invalid option, {option}")
                    continue

                node_name = (await prompt("Enter Node Name: ")).strip()
                node_did = (await prompt("Enter Node DID: ")).strip()
                await onboard_node(
                    agent_container,
                    domain=db_name,
                    node_did=node_did,
                    node_name=node_name,
                )
                # options.pop("onboard")

            # elif option == "3":
            #     pass
            elif option == "0":
                if not options.get("demo"):
                    log_msg(f"invalid option, {option}")
                    continue

                await demo_setup(agent_container)

            elif option == "x":  # shut off gracefully
                sys.exit(0)
    finally:
        # Shut down the agent gracefully
        await agent_container.terminate()


if __name__ == "__main__":
    parser = arg_parser()
    args = parser.parse_args()

    # execute main
    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        sys.exit(1)
