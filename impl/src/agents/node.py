import asyncio
import os

import json

from agents.agent_container import (  # noqa:E402
    AriesAgent,
    arg_parser,
    create_agent_with_args,
)
from support.utils import log_json


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

    async def handle_revocation_notification(self, message):
        self.log("Received revocation notification message:")
        message["comment"] = json.loads(message["comment"])
        self.log_json(message)
        # TODO: (aver) handle update
        pass


async def main(args):
    # First setup all the agent related stuff
    agent_container = await create_agent_with_args(args)
    # agent_container.seed = "Node1_00000000000000000000000000"

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
            wallet_name=agent_container.ident,
            # WARN: (aver) key is same as identity, which is insecure, watch out!
            wallet_key=agent_container.ident,
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
    parser = arg_parser()
    args = parser.parse_args()

    # execute main
    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        os._exit(1)
