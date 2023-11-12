import asyncio
import os
from uuid import uuid4

from agents.agent_container import (
    AgentContainer,
    AriesAgent,
    arg_parser,
    create_agent_with_args,
)
from support.utils import log_json, log_msg, log_status  # noqa:E402


class VerifierAgent(AriesAgent):
    """
    This agent will be a credential issuer from the maintainer/manufacturer point of view.
    """

    def __init__(self, ident: str, http_port: int, admin_port: int, **kwargs):
        super().__init__(ident=ident, http_port=http_port, admin_port=admin_port, **kwargs)
        self.connection_id = None
        self._connection_ready = None
        # TODO define a dict to hold credential attributes based on cred_def_id
        self.cred_state = {}
        self.cred_attrs = {}

    async def handle_connections(self, message):
        print(self.ident, "handle_connections", message["state"], message["rfc23_state"])
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


async def send_message(agent_container: AgentContainer):
    message = {"content": f"hello from {agent_container.ident}!"}
    await agent_container.admin_POST(
        path=f"/connections/{agent_container.agent.connection_id}/send-message",
        data=message,
    )


async def create_agent_container(args) -> AgentContainer:
    # First setup all the agent related stuff
    agent_container = await create_agent_with_args(args)
    agent_container.seed = "Autho_00000000000000000000000000"
    agent = VerifierAgent(
        "verifier.agent",
        agent_container.start_port,
        agent_container.start_port + 1,
        genesis_data=agent_container.genesis_txns,
        genesis_txn_list=agent_container.genesis_txn_list,
        no_auto=agent_container.no_auto,
        tails_server_base_url=agent_container.tails_server_base_url,
        revocation=agent_container.revocation,
        timing=agent_container.show_timing,
        multitenant=agent_container.multitenant,
        mediation=agent_container.mediation,
        wallet_type=agent_container.wallet_type,
        aip=agent_container.aip,
        endorser_role=agent_container.endorser_role,
        seed=agent_container.seed,
    )
    await agent_container.initialize(
        the_agent=agent,
    )
    return agent_container


async def main(args):
    # TODO: (aver) create prompt loop with credential to check for
    # TODO: (aver) refactor as every other agent
    agent_container = await create_agent_container(args)
    try:
        # TODO: find better way to post. It would make sense to create a unique/separate endpoint for
        # invitation requests, that then can be passed to the agent to be accepted.
        # Flow:
        #   1. Authority/Issuer creates invitation
        #   2. Targeted Agent receives and accepts

        # Take public DID for Node agent from a DATABASE

        # WARN: fixed seed for DIDs
        node_did = "did:sov:SYBqqHS7oYwthtCDNHi841"
        await agent_container.agent.send_invitation(node_did)

        # send test message
        response = await agent_container.admin_GET("/connections")
        log_json(response)
        agent_container.agent.connection_id = response["results"][0]["connection_id"]
        agent_container.agent._connection_ready = asyncio.Future()
        log_msg("Waiting for connection...")
        await agent_container.agent.detect_connection()

        # TODO: (aver) get schema attributes from central location
        # send proof request
        # schema_name = "controller id schema"
        schema_attributes = ["controller_id", "date", "status"]

        request_attributes = [
            {"name": n, "restrictions": [{"schema_name": "controller id schema"}]}
            for n in schema_attributes
        ]
        indy_proof_request = {
            "name": "Proof of controller id",
            "version": "1.0",
            "nonce": str(uuid4().int),
            "requested_attributes": {
                f"0_{req_atrb['name']}_uuid": req_atrb for req_atrb in request_attributes
            },
            "requested_predicates": {},
        }
        proof_request_web_request = {
            "connection_id": agent_container.agent.connection_id,
            "presentation_request": {"indy": indy_proof_request},
        }

        # Send request to agent and forward it to alice, based on connection_id
        await agent_container.admin_POST(
            "/present-proof-2.0/send-request", proof_request_web_request
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
