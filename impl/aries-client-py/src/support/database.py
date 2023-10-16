"""
Contains a host of helper functions for managing the Orion database
"""
import base64
import json
from uuid import uuid4

from aiohttp import ClientSession
from support.utils import log_json, log_msg, run_executable, log_status


# TODO: (aver) create class to hold database logic for less duplication
class OrionDB:
    def __init__(
        self,
        orion_db_url: str,
        username: str,
        client_session: ClientSession,
        private_key_path="",
    ):
        self.__orion_db_url = orion_db_url
        self.__username = username
        self.__private_key_path = (
            private_key_path
            if not private_key_path == ""
            else f"crypto/{self.__username}/{self.__username}.key"
        )
        self.__client_session = client_session
        # Holds created databases
        self.databases = []
        # FIXME: Holds created keys until query_all works
        # Holds keys and `connection_id`s
        self.db_keys = {}

    def __sign_tx(self, payload):
        """
        Wrapper function for signing a database transaction
        """
        return sign_transaction(payload, self.__private_key_path)

    async def query_key(self, db_name, key):
        """
        https://labs.hyperledger.org/orion-server/docs/getting-started/transactions/curl/datatx#12-checking-the-existance-of-key1
        """
        # keys need to be send as base64, in order for =/- characters to work.
        enc_key = base64.urlsafe_b64encode(bytes(key, encoding="utf-8")).decode()

        payload = {"user_id": self.__username, "db_name": db_name, "key": key}
        signature = self.__sign_tx(payload)

        response = await self.__client_session.get(
            url=f"{self.__orion_db_url}/data/db1/{enc_key}",
            headers={"UserID": self.__username, "Signature": signature},
        )

        if not response.ok:
            log_msg("\n\nERRROR HAPPENED\n\n")

        log_msg(f"Returned with {response.status}")
        response = await response.json()
        log_json(response)

        enc_value = response["response"]["value"]
        dec_value = decode_data(enc_value)

        try:
            return dec_value
        except Exception as e:
            log_msg(e.with_traceback())

    def __glue_payload(self, payload: dict, signature: str):
        """
        Glues the payload and signature into a dict/json.
        """
        return {"payload": payload, "signature": signature}

    async def check_db(self, db_name: str):
        """
        Check existence of a database with given name
        """
        payload = {"user_id": self.__username, "db_name": db_name}
        signature = self.__sign_tx(payload)
        response = await self.__client_session.get(
            url=f"{self.__orion_db_url}/db/{db_name}",
            headers={"UserID": self.__username, "Signature": signature},
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

    async def check_user(self, username: str):
        """
        Check existence of a user with given name
        """
        payload = {"user_id": self.__username, "target_user_id": username}
        signature = self.__sign_tx(payload)
        response = await self.__client_session.get(
            url=f"{self.__orion_db_url}/user/{username}",
            headers={"UserID": self.__username, "Signature": signature},
        )

        # TODO: (aver) improve error handling
        if not response.ok:
            log_msg("\n\nERRROR HAPPENED\n\n")
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
        if db_name not in self.databases:
            self.databases.append(db_name)
            # self.db_keys[db_name] = []
            self.db_keys[db_name] = {}

        if await self.check_db(db_name):
            log_status(f"{db_name}: Already exists")
            return

        payload = {
            "user_id": self.__username,
            "tx_id": get_tx_id(),
            "create_dbs": [db_name],
        }
        signature = self.__sign_tx(payload)
        data = self.__glue_payload(payload, signature)

        response = await self.__client_session.post(
            url=f"{self.__orion_db_url}/db/tx", json=data, headers={"TxTimeout": "2s"}
        )

        # TODO: (aver) improve error handling
        if not response.ok:
            print("\n\nERRROR HAPPENED\n\n")
            return

        log_status(f"Returned with {response.status}")
        response = await response.json()
        log_json(response)
        self.databases.append(db_name)

    async def create_user(self, username: str):
        """
        Creates a user with given `username` on request, if not already existing
        """
        if await self.check_user(username):
            log_status(f"{username}: Already exists")
            # return

        with open(f"./crypto/{username}/{username}.pem", "r") as file:
            # skip begin and end line
            certificate = file.readlines()[1:-1]
            # replace newlines, as certificate is broken up
            certificate = "".join(certificate).replace("\n", "")

        headers = {"TxTimeout": "10s"}
        payload = {
            "user_id": self.__username,
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
                        "read_users": {self.__username: True},
                    },
                }
            ],
        }
        signature = self.__sign_tx(payload)
        data = self.__glue_payload(payload, signature)

        response = await self.__client_session.post(
            url=f"{self.__orion_db_url}/user/tx", json=data, headers=headers
        )

        if response.ok:
            log_status(f"Returned with {response.status}")
            response = await response.json()
        else:
            response = await response.json()
            print("\n\n\tERRROR HAPPENED\n\n")
        # log response in any case
        log_json(response)

    async def record_key(self, db_name: str, key_name: str, value: dict):
        headers = {"TxTimeout": "2s"}
        encoded_value = encode_data(value)
        payload = {
            "must_sign_user_ids": [self.__username],
            "tx_id": get_tx_id(),
            "db_operations": [
                {
                    "db_name": db_name,
                    "data_writes": [
                        {
                            "key": key_name,
                            "value": encoded_value,
                            "acl": {
                                "read_users": {"auditor": True},
                                "read_write_users": {self.__username: True},
                            },
                        },
                    ],
                }
            ],
        }
        signature = self.__sign_tx(payload)
        # cannot use the glue here, possibly multiple signatures expected...
        data = {"payload": payload, "signatures": {self.__username: signature}}

        response = await self.__client_session.post(
            url=f"{self.__orion_db_url}/data/tx", json=data, headers=headers
        )
        if response.ok:
            log_status(f"Returned with {response.status}")
            response = await response.json()
            log_json(response)
            # we also record the keys, as a workaround to not being able to query all keys in the
            # database
            if key_name not in self.db_keys[db_name]:
                # self.db_keys[db_name].append(key_name)
                self.db_keys[db_name][key_name] = {}
            else:
                log_msg(f"Key {key_name}, already recorded (possible update of values)")
            log_msg("Added to local map", self.db_keys[db_name])
        else:
            response = await response.json()
            log_msg("\n\nERRROR HAPPENED\n\n")
            log_json(response)

    async def query_all(self, db_name):
        """
        https://github.com/hyperledger-labs/orion-server/blob/0009ffdf5f35e8cf9e6a938378733d4e5e6474d1/pkg/constants/http.go#L97
        """
        # FIXME: dunno how to fix this method, documentation is not existent and if I imitate the source
        # code I get 404
        raise NotImplementedError
        key = "Controller_1"
        key = ""
        enc_key = base64.urlsafe_b64encode(bytes(key, encoding="utf-8")).decode()
        payload = {
            "user_id": self.__username,
            "db_name": db_name,
            "start_key": key,
            "end_key": key,
            "limit": 10,
        }
        signature = self.__sign_tx(payload)
        response = await self.__client_session.get(
            # url=f"{self.__orion_db_url}/data/db1/startkey={enc_key}&endkey={enc_key}/",
            url=f"{self.__orion_db_url}/data/db1",
            headers={"UserID": self.__username, "Signature": signature},
        )

        if not response.ok:
            log_msg("\n\nERRROR HAPPENED\n\n")

        log_msg(f"Returned with {response.status}")
        response = await response.json()
        log_json(response)


def sign_transaction(data: json, privatekey: str):
    """
    Sign a transaction for Hyperledger Orion
    params:
        data: data in json to be signed
        privatekey: location to private key
    """
    prepped_data = json.dumps(data).replace(" ", "")
    log_msg("Data to be signed:", prepped_data)
    signature = run_executable(
        (
            "./bin/signer",
            f"-data={prepped_data}",
            f"-privatekey={privatekey}",
        )
    )
    return signature


def encode_data(data: json):
    """
    Encodes data into base64
    """
    prepped_data = json.dumps(data).replace(" ", "")
    log_msg("Data to be encoded:", prepped_data)
    encoded_data = base64.b64encode(bytes(prepped_data, "utf-8")).decode()
    return encoded_data


def decode_data(encoded_data: str):
    """
    Decodes base64 data into a string
    """
    decoded_data = base64.b64decode(encoded_data)
    return json.loads(decoded_data)


def get_tx_id():
    """
    Generate a random uuid4 based id, generally to identify transactions
    """
    return str(uuid4())
