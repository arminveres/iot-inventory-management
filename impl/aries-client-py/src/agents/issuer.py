import asyncio
import os
from datetime import date

from agents.agent_container import (
    CRED_PREVIEW_TYPE,
    AgentContainer,
    AriesAgent,
    arg_parser,
    create_agent_with_args,
)
from support.agent import DEFAULT_INTERNAL_HOST
from support.database import encode_data, get_tx_id, sign_transaction
from support.utils import log_json, log_msg, log_status  # noqa:E402


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
        self.databases = []

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

    def _db_sign_tx(self, payload):
        """
        Wrapper function for signing a database transaction
        """
        return sign_transaction(payload, self._db_privatekey)

    def _db_glue_payload(self, payload: dict, signature: str):
        """
        Glues the payload and signature into a dict/json.
        """
        return {"payload": payload, "signature": signature}

    async def _db_check_db(self, db_name: str):
        """
        Check existence of a database with given name
        """
        payload = {"user_id": self._db_user_id, "db_name": db_name}
        signature = self._db_sign_tx(payload)
        response = await self.client_session.get(
            url=f"{self.orion_db_url}/db/{db_name}",
            headers={"UserID": self._db_user_id, "Signature": signature},
        )

        # TODO: (aver) improve error handling
        if not response.ok:
            print("\n\nERRROR HAPPENED\n\n")
            return False

        log_msg(f"Returned with {response.status}")
        response = await response.json()
        log_json(response)
        try:
            return response["response"]["exist"]
        except KeyError:
            return False

    async def _db_check_user(self, username: str):
        """
        Check existence of a user with given name
        """
        payload = {"user_id": self._db_user_id, "target_user_id": username}
        signature = self._db_sign_tx(payload)
        response = await self.client_session.get(
            url=f"{self.orion_db_url}/user/{username}",
            headers={"UserID": self._db_user_id, "Signature": signature},
        )

        # TODO: (aver) improve error handling
        if not response.ok:
            print("\n\nERRROR HAPPENED\n\n")
            return False

        log_msg(f"Returned with {response.status}")
        response = await response.json()
        log_json(response)
        try:
            return response["response"]["user"]["id"] == username
        except KeyError:
            return False

    async def create_database(self, db_name: str):
        """
        Creates a database with given name, but checks first whether it exists
        """

        if await self._db_check_db(db_name):
            log_status(f"{db_name}: Already exists")
            if db_name not in self.databases:
                self.databases.append(db_name)
            return

        payload = {
            "user_id": self._db_user_id,
            "tx_id": get_tx_id(),
            "create_dbs": [db_name],
        }
        signature = self._db_sign_tx(payload)
        data = self._db_glue_payload(payload, signature)

        response = await self.client_session.post(
            url=f"{self.orion_db_url}/db/tx", json=data, headers={"TxTimeout": "2s"}
        )

        # TODO: (aver) improve error handling
        if not response.ok:
            print("\n\nERRROR HAPPENED\n\n")
            return

        log_status(f"Returned with {response.status}")
        response = await response.json()
        log_json(response)
        self.databases.append(db_name)

    async def db_record_key(self, key_name: str, value: dict):
        headers = {"TxTimeout": "2s"}
        encoded_value = encode_data(value)
        payload = {
            "must_sign_user_ids": [self._db_user_id],
            "tx_id": get_tx_id(),
            "db_operations": [
                {
                    "db_name": self.databases[0],
                    "data_writes": [
                        {
                            "key": key_name,
                            "value": encoded_value,
                            "acl": {"read_write_users": {self._db_user_id: True}},
                        },
                    ],
                }
            ],
        }
        signature = self._db_sign_tx(payload)
        # cannot use the glue here, possibly multiple signatures expected...
        data = {"payload": payload, "signatures": {self._db_user_id: signature}}

        response = await self.client_session.post(
            url=f"{self.orion_db_url}/data/tx", json=data, headers=headers
        )
        if response.ok:
            log_status(f"Returned with {response.status}")
            response = await response.json()
            log_json(response)
        else:
            response = await response.json()
            log_msg("\n\nERRROR HAPPENED\n\n")
            log_json(response)

    async def db_create_user(self, username: str):
        """
        Creates a user with given `username` on request, if not already existing
        """
        if await self._db_check_user(username):
            log_status(f"{username}: Already exists")
            # return

        with open(f"./crypto/{username}/{username}.pem", "r") as file:
            # skip begin and end line
            certificate = file.readlines()[1:-1]
            # replace newlines, as certificate is broken up
            certificate = "".join(certificate).replace("\n", "")

        headers = {"TxTimeout": "10s"}
        payload = {
            "user_id": self._db_user_id,
            "tx_id": get_tx_id(),
            "user_writes": [
                {
                    "user": {
                        "id": username,
                        "certificate": certificate,
                        # give read write access to the first, and only, database
                        "privilege": {
                            # WARN: This is kind of another mess ... the guide says use 0 for Read
                            # access and 1 for ReadWrite access, but signature fails if numbers are
                            # used, therefore use string of enum `Read` or `ReadWrite`
                            "db_permission": {self.databases[0]: "ReadWrite"}
                        },
                    },
                    # We could further specify access control, by default, undefined, everyone can
                    # read credentials and privilege of the user
                    "acl": {
                        "read_users": {self._db_user_id: True},
                    },
                }
            ],
        }
        signature = self._db_sign_tx(payload)
        data = self._db_glue_payload(payload, signature)

        response = await self.client_session.post(
            url=f"{self.orion_db_url}/user/tx", json=data, headers=headers
        )

        if response.ok:
            log_status(f"Returned with {response.status}")
            response = await response.json()
        else:
            response = await response.json()
            print("\n\n\tERRROR HAPPENED\n\n")
        # log response in any case
        log_json(response)


async def send_message(agent: AriesAgent):
    message = {"content": f"hello from {agent.ident}!"}
    await agent.admin_POST(
        path=f"/connections/{agent.agent.connection_id}/send-message", data=message
    )


async def create_agent_container(args) -> AgentContainer:
    # First setup all the agent related stuff
    agent_container = await create_agent_with_args(args, ident="issuer_node")
    agent_container.seed = "Autho_00000000000000000000000000"
    agent = IssuerAgent(
        "issuer.agent",
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
    agent_container = await create_agent_container(args)

    try:
        # =========================================================================================
        # Set up schema and initialize
        # =========================================================================================

        await agent_container.agent.create_database("db1")

        schema_name = "controller id schema"
        schema_attributes = ["controller_id", "date", "status"]
        version = "0.0.1"

        # Currently the credential is of the same format as the entry to the database
        controller_1_cred = {
            "controller_id": "node0001",
            "date": date.isoformat(date.today()),
            "status": "valid",
        }

        await agent_container.agent.db_record_key("Controller_1", controller_1_cred)

        # we create an auditor user, who then will mark software as vulnerable
        await agent_container.agent.db_create_user("auditor")

        exit(0)

        agent_container.cred_def_id = await agent_container.create_schema_and_cred_def(
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
        await agent_container.agent.send_invitation(node_did)

        # send test message
        response = await agent_container.admin_GET("/connections")
        log_json(response)
        conn_id = response["results"][0]["connection_id"]
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
