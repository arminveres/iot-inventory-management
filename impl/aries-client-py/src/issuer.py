import asyncio
import json
import os
from datetime import date
from uuid import uuid4

from agent_container import (
    CRED_PREVIEW_TYPE,
    AgentContainer,
    AriesAgent,
    arg_parser,
    create_agent_with_args,
)
from support.agent import DEFAULT_INTERNAL_HOST
from support.database import sign_transaction
from support.utils import log_json, log_msg, log_status, run_executable  # noqa:E402


# TODO: (aver) What about making this an administrative instance of the maintainer environment?
# could serve as
class IssuerAgent(AriesAgent):
    """
    This agent will be a credential issuer from the maintainer/manufacturer point of view.
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
        self.orion_db_url = orion_db_url
        self._db_user_id = "admin"
        self._db_privatekey = "crypto/admin/admin.key"

        self.connection_id = None
        self._connection_ready = None
        # TODO define a dict to hold credential attributes based on cred_def_id
        self.cred_state = {}
        self.cred_attrs = {}

    async def handle_connections(self, message):
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

    async def create_database(self, database_name: str):
        """
        TODO: (aver) create database with orion
        """
        payload = {
            "user_id": self._db_user_id,
            "tx_id": str(uuid4()),
            "create_dbs": [database_name],
        }
        signature = sign_transaction(payload, self._db_privatekey)
        data = {"payload": payload, "signature": signature}
        response = await self.client_session.post(
            url=f"{self.orion_db_url}/db/tx", json=data, headers={"TxTimeout": "2s"}
        )
        response = await response.json()
        log_json(response)


async def send_message(agent: AriesAgent):
    message = {"content": f"hello from {agent.ident}!"}
    await agent.admin_POST(
        path=f"/connections/{agent.agent.connection_id}/send-message", data=message
    )


async def create_agent_container(args) -> AgentContainer:
    # First setup all the agent related stuff
    node_agent = await create_agent_with_args(args, ident="issuer_node")
    node_agent.seed = "Autho_00000000000000000000000000"
    agent = IssuerAgent(
        "issuer.agent",
        node_agent.start_port,
        node_agent.start_port + 1,
        genesis_data=node_agent.genesis_txns,
        genesis_txn_list=node_agent.genesis_txn_list,
        no_auto=node_agent.no_auto,
        tails_server_base_url=node_agent.tails_server_base_url,
        revocation=node_agent.revocation,
        timing=node_agent.show_timing,
        multitenant=node_agent.multitenant,
        mediation=node_agent.mediation,
        wallet_type=node_agent.wallet_type,
        aip=node_agent.aip,
        endorser_role=node_agent.endorser_role,
        seed=node_agent.seed,
    )
    await node_agent.initialize(
        the_agent=agent,
    )
    return node_agent


async def main(args):
    try:
        # =========================================================================================
        # Set up schema and initialize
        # =========================================================================================

        node_agent = await create_agent_container(args)

        await node_agent.agent.create_database("db1")

        exit(0)
        schema_name = "controller id schema"
        schema_attributes = ["controller_id", "date", "status"]
        version = "0.0.1"

        node_agent.cred_def_id = await node_agent.create_schema_and_cred_def(
            schema_name, schema_attributes, version
        )

        # TODO: find better way to post. It would make sense to create a unique/separate endpoint for
        # invitation requests, that then can be passed to the agent to be accepted.
        # Flow:
        #   1. Authority/Issuer creates invitation
        #   2. Targeted Agent receives and accepts

        # Take public DID from a DATABASE

        # WARN: fixed seed for DIDs
        node_did = "did:sov:SYBqqHS7oYwthtCDNHi841"
        await node_agent.agent.send_invitation(node_did)

        # send test message
        response = await node_agent.admin_GET("/connections")
        log_json(response)
        conn_id = response["results"][0]["connection_id"]
        node_agent.agent._connection_ready = asyncio.Future()
        log_msg("Waiting for connection...")
        await node_agent.agent.detect_connection()

        log_status("#13 Issue credential offer to X")
        # TODO credential offers
        # WARN: this could be better handled for general usecases, here it is just for Alice
        node_agent.agent.cred_attrs[node_agent.cred_def_id] = {
            "controller_id": "node0001",
            "date": date.isoformat(date.today()),
            "status": "valid",
        }
        cred_preview = {
            "@type": CRED_PREVIEW_TYPE,
            "attributes": [
                {"name": n, "value": v}
                for (n, v) in node_agent.agent.cred_attrs[
                    node_agent.cred_def_id
                ].items()
            ],
        }
        offer_request = {
            "connection_id": conn_id,
            "comment": f"Offer on cred def id {node_agent.cred_def_id}",
            "credential_preview": cred_preview,
            "filter": {"indy": {"cred_def_id": node_agent.cred_def_id}},
        }
        await node_agent.admin_POST("/issue-credential-2.0/send-offer", offer_request)

        # =========================================================================================
        # Event Loop
        # =========================================================================================
        # This event loop is needed so that coroutines still can be run in the background, as well
        # as webhooks received.
        # Alternatively something like `asyncio.Event` could be used and be waited upon
        while True:
            await send_message(node_agent)
            await asyncio.sleep(1)

    finally:
        # Shut down the agent gracefully
        await node_agent.terminate()


if __name__ == "__main__":
    parser = arg_parser(ident="issuer_node")
    args = parser.parse_args()

    # execute main
    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        os._exit(1)
