import asyncio
import json
import os

from agent_container import AriesAgent, arg_parser, create_agent_with_args
from support.utils import log_json  # noqa:E402


class AuthorityAgent(AriesAgent):
    """
    This agent will be a credential issuer from the maintainer/manufacturer point of view.
    """

    def __init__(self, ident: str, http_port: int, admin_port: int, **kwargs):
        super().__init__(
            ident=ident, http_port=http_port, admin_port=admin_port, **kwargs
        )
        self.connection_id = None
        self._connection_ready = None
        self.cred_state = {}
        # TODO define a dict to hold credential attributes
        # based on cred_def_id
        self.cred_attrs = {}

    async def handle_out_of_band(self, message):
        print("handle_out_of_band()")
        log_json(message)


async def main(args):
    # First setup all the agent related stuff
    node_agent = await create_agent_with_args(args, ident="authority_node")
    node_agent.seed = "Autho_00000000000000000000000000"
    try:
        agent = AuthorityAgent(
            "authority.agent",
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
        await node_agent.initialize(the_agent=agent)

        # response = await node_agent.generate_invitation(
        # reuse_connections=node_agent.reuse_connections
        # )
        response = await node_agent.admin_POST("/connections/create-invitation", {})
        print(json.dumps(response, indent=4))
        invite = response["invitation"]

        # TODO: find better way to post. It would make sense to create a unique/separate endpoint for
        # invitation requests, that then can be passed to the agent to be accepted.
        # Flow:
        #   1. Authority/Issuer creates invitation
        #   2. Targeted Agent receives and accepts

        # Take public DID from a DATABASE

        # WARN: fixed seed for DIDs
        node_did = "did:sov:SYBqqHS7oYwthtCDNHi841"

        # resolve did for did_document
        response = await node_agent.admin_GET(f"/resolver/resolve/{node_did}")
        print(json.dumps(response, indent=4))
        node_url = response["did_document"]["service"][0]["serviceEndpoint"]
        node_url = node_url[:-1] + "1"  # fix url to admin point, BAD fix
        print(node_url)

        response = await agent.client_session.post(
            url=f"{node_url}/connections/receive-invitation",
            json=invite,
        )

        resp = await response.json()
        log_json(resp)

        # send test message
        response = await node_agent.admin_GET("/connections")
        conn_id = response["results"][0]["connection_id"]

        # =========================================================================================
        # Event Loop
        # =========================================================================================
        # NOTE: (aver) What I found out, is that there needs to be an 'event loop' for the hooks to
        # be activated...
        while True:
            message = {"content": "hello there amore!"}
            response = await node_agent.admin_POST(
                path=f"/connections/{conn_id}/send-message", data=message
            )
            print(json.dumps(response, indent=4))

            await asyncio.sleep(1)
        # =========================================================================================
        # END Event Loop
        # =========================================================================================

    finally:
        await node_agent.terminate()


if __name__ == "__main__":
    parser = arg_parser(ident="authority_node")
    args = parser.parse_args()

    # execute main
    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        os._exit(1)
