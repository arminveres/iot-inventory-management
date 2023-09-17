import json
import os
import asyncio

from agent_container import AriesAgent, arg_parser, create_agent_with_args
from support.utils import log_json, log_msg  # noqa:E402


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

    response = await node_agent.generate_invitation(
        reuse_connections=node_agent.reuse_connections
    )
    invite = response["invitation"]

    # Say we have the DID from a DATABASE
    node_did = "did:sov:TMmqycDZquFUg1gyFnvreF"
    response = await node_agent.admin_GET(f"/resolver/resolve/{node_did}")
    # print(json.dumps(response, indent=4))
    # print(response["did_document"]["service"][0]["serviceEndpoint"])
    node_url = response["did_document"]["service"][0]["serviceEndpoint"]
    # fix url to admin point
    node_url = node_url[:-1] + "1"
    print(node_url)
    response = await agent.client_session.post(
        url=f"{node_url}/out-of-band/receive-invitation", json=invite
    )
    # log_msg(response)
    print(response)


if __name__ == "__main__":
    parser = arg_parser(ident="authority_node")
    args = parser.parse_args()

    # execute main
    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        os._exit(1)
