import asyncio
import os
import sys

# add the source directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa

from agent_container import AriesAgent, arg_parser, create_agent_with_args  # noqa:E402


# class NodeAgent:
class NodeAgent(AriesAgent):
    """
    A NodeAgent represents an end target, that will hold credentials.
    TODO: Further differentiate between controller, function, edge nodes.
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

    async def handle_invitation(self, message):
        """
        Handle invitation received for connections
        """
        self.log("Received invitation:", message["content"])
        print("\n\ngot\n\n", message)


async def main(args):
    # First setup all the agent related stuff
    agent_container = await create_agent_with_args(args, ident="test_node")
    agent_container.seed = "Node1_00000000000000000000000000"

    try:
        agent = NodeAgent(
            "node.agent",
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
        await agent_container.initialize(the_agent=agent)

        while True:
            # pass
            await asyncio.sleep(0.1)

    finally:
        await agent_container.terminate()


if __name__ == "__main__":
    parser = arg_parser(ident="test_node")
    args = parser.parse_args()

    # execute main
    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        os._exit(1)
