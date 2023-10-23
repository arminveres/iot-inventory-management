import asyncio
import json
import os
import sys

from agents.agent_container import (  # noqa:E402
    AgentContainer,
    AriesAgent,
    arg_parser,
    create_agent_with_args,
)
from support.utils import log_msg, prompt, prompt_loop


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

    # =============================================================================================
    # Webhook handler implementations
    # =============================================================================================
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

    # =============================================================================================
    # Additional methods
    # =============================================================================================


async def register_subnode(agent_container: AgentContainer, node_name: str):
    """
    Registers a subnode with name `node_name` to the agent in the `agent_container`
    TODO: (aver) could move this to AgentContainer implementation
    """
    await agent_container.agent.register_or_switch_wallet(
        target_wallet_name=f"{agent_container.ident}.sub.{node_name}",
        public_did=agent_container.public_did
        and (
            (not agent_container.endorser_role)
            or (not agent_container.endorser_role == "author")
        ),
        webhook_port=None,
        mediator_agent=agent_container.mediator_agent,
        endorser_agent=agent_container.endorser_agent,
        taa_accept=agent_container.taa_accept,
    )


async def main(args):
    # First setup all the agent related stuff
    agent_container = await create_agent_with_args(args)
    # agent_container.seed = "Node1_00000000000000000000000000"
    # TODO: (aver) save seed for provisioning to pick up on
    agent_container.seed = "d_000000000000000000000000752220"

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

        # =========================================================================================
        # Event Loop
        # =========================================================================================
        # New prompt based event loop, events such as webhooks still run in the background.

        # Setup options and make them dicts, so that they can be changed at runtime, although watch
        # out for duplicated keys.
        # TODO: (aver) find better way to interact with runtime options
        options = {
            "exit": "  [x]: Exit\n",
        }

        if agent_container.multitenant:
            options["reg_subnode"] = "  [1]: Register a subnode, i.e., and edge node\n"

        def get_prompt():
            options.update
            options_str = "Options:\n"
            for key, value in list(options.items()):
                options_str += value
            options_str += "> "
            return options_str

        async for option in prompt_loop(get_prompt):
            if option is not None:
                option.strip()
            if option is None or option == "":
                log_msg("Please give an option")

            if option == "1" and agent_container.multitenant:
                edge_node_name = (
                    await prompt("Enter a name for the subnode: ")
                ).strip()
                await register_subnode(agent_container, edge_node_name)

            elif option in "xX":
                sys.exit(0)

            else:
                log_msg("Unknown option: " + option)

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
