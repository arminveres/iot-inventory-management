import asyncio
import os
from datetime import date

import json
from agents.agent_container import (
    CRED_PREVIEW_TYPE,
    AgentContainer,
    AriesAgent,
    arg_parser,
    create_agent_with_args,
)
from support.agent import DEFAULT_INTERNAL_HOST
from support.database import OrionDB
from support.utils import log_json, log_msg, log_status


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

    async def handle_connections(self, message):
        # TODO: (aver) update for mutliple connections
        print(
            self.ident, "handle_connections", message["state"], message["rfc23_state"]
        )
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

        # TODO: (aver) add cred_def_i
        response = await self.db_client.query_key("db1", "Controller_1")
        response["cred_ex_id"] = cred_ex_id
        response["valid"] = True
        await self.db_client.record_key("db1", "Controller_1", response)

        self.cred_state[cred_ex_id] = state
        self.log(f"Credential: state = {state}, cred_ex_id = {cred_ex_id}")

        if state == "request-received":
            # TODO issue credentials based on offer preview in cred ex record
            if not message.get("auto_issue"):
                await self.admin_POST(
                    f"/issue-credential-2.0/records/{cred_ex_id}/issue",
                    {"comment": f"Issuing credential, exchange {cred_ex_id}"},
                )

    async def handle_present_proof_v2_0(self, message):
        state = message["state"]
        pres_ex_id = message["pres_ex_id"]
        self.log(f"Presentation: state = {state}, pres_ex_id = {pres_ex_id}")

        if state == "presentation-received":
            # TODO handle received presentations
            log_status("#27 Process the proof provided by X")
            log_status("#28 Check if proof is valid")
            proof = await self.admin_POST(
                f"/present-proof-2.0/records/{pres_ex_id}/verify-presentation"
            )
            self.log("Proof = ", proof["verified"])

            # if presentation is a degree schema (proof of education), check values received
            pres_req = message["by_format"]["pres_request"]["indy"]
            pres = message["by_format"]["pres"]["indy"]
            is_proof_of_education = pres_req["name"] == "Proof of Education"

            if not is_proof_of_education:
                # in case there are any other kinds of proofs received
                self.log("#28.1 Received ", pres_req["name"])
                return

            log_status("#28.1 Received proof of education, check claims")
            for referent, attr_spec in pres_req["requested_attributes"].items():
                if referent in pres["requested_proof"]["revealed_attrs"]:
                    self.log(
                        f"{attr_spec['name']}: "
                        f"{pres['requested_proof']['revealed_attrs'][referent]['raw']}"
                    )
                else:
                    self.log(f"{attr_spec['name']}: " "(attribute not revealed)")
            for id_spec in pres["identifiers"]:
                # just print out the schema/cred def id's of presented claims
                self.log(f"schema_id: {id_spec['schema_id']}")
                self.log(f"cred_def_id {id_spec['cred_def_id']}")
            # TODO placeholder for the next step

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
                                response["cred_ex_id"], None, reason
                            )

    async def revoke_credential(
        self, cred_ex_id: str, connection_id: str, revocation_reason: dict
    ):
        """
        Revoke a credentials and publish it.
        """
        response = await self.db_client.query_key("db1", "Controller_1")
        response["cred_ex_id"] = ""
        response["valid"] = False
        await self.db_client.record_key("db1", "Controller_1", response)

        # FIXME: (aver) remove hard coded connection_id and retrieve or store in database
        await self.admin_POST(
            "/revocation/revoke",
            {
                "cred_ex_id": cred_ex_id,
                "publish": True,
                "connection_id": self.connection_id,
                "comment": json.dumps(revocation_reason),
            },
            # {"cred_ex_id": cred_ex_id, "publish": True, "connection_id": connection_id},
        )


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


async def main(args):
    agent_container = await create_agent_container(args)

    try:
        # =========================================================================================
        # Set up schema and initialize
        # =========================================================================================

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

        # WARN: fixed seed for DIDs
        node_did = "did:sov:SYBqqHS7oYwthtCDNHi841"
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

        # conn_id = response["results"][0]["connection_id"]
        agent_container.agent._connection_ready = asyncio.Future()
        log_msg("Waiting for connection...")
        await agent_container.agent.detect_connection()

        log_status("#13 Issue credential offer to X")
        # TODO credential offers
        # WARN: this could be better handled for general usecases, here it is just for Alice
        agent_container.agent.cred_attrs[
            agent_container.cred_def_id
        ] = controller_1_cred
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
        await agent_container.admin_POST(
            "/issue-credential-2.0/send-offer", offer_request
        )

        # =========================================================================================
        # Event Loop
        # =========================================================================================
        # This event loop is needed so that coroutines still can be run in the background, as well
        # as webhooks received.
        # Alternatively something like `asyncio.Event` could be used and be waited upon
        while True:
            await send_message(agent_container)
            await asyncio.sleep(1)

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
        os._exit(1)
