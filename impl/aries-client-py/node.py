import os
import asyncio

# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_container import AriesAgent, arg_parser, create_agent_with_args  # noqa:E402


class NodeAgent(AriesAgent):
    """
    A NodeAgent represents an end target, that will hold credentials.
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


async def main(args):
    # First setup all the agent related stuff
    node_agent = await create_agent_with_args(args, ident="test_node")
    node_agent.seed = "Node1_00000000000000000000000000"

    agent = NodeAgent(
        "node.agent",
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


if __name__ == "__main__":
    parser = arg_parser(ident="test_node")
    args = parser.parse_args()

    # execute main
    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        os._exit(1)
