"""
Demonstrative auditor to mark soft- or firmware as vulnerable
"""
# TODO: (aver)
# - add analysis of DB and post revocation
import asyncio
import os
import base64

from aiohttp import ClientSession
from support.agent import DEFAULT_INTERNAL_HOST
from support.database import sign_transaction, encode_data, decode_data
from support.utils import log_json, log_msg


class Auditor:
    """
    Class that holds logic for a sample auditor, marking software as vulnerable.
    Works by querying the orion database and notifying the issuer, i.e., the admin of a
    vulnerability.
    """

    def __init__(
        self,
        db_username="auditor",
        orion_db_url=f"http://{DEFAULT_INTERNAL_HOST}:6001",
    ):
        self.client_session = ClientSession()
        self.db_username = db_username
        self.__orion_db_url = orion_db_url
        self.__db_privatekey_path = f"crypto/{self.db_username}/{self.db_username}.key"
        self.__databases = []

    def __db_sign_tx(self, payload):
        """
        Wrapper function for signing a database transaction
        """
        return sign_transaction(payload, self.__db_privatekey_path)

    async def db_query_all(self):
        payload = {"user_id": self.db_username}
        signature = self.__db_sign_tx(payload)
        response = await self.client_session.get(
            url=f"{self.__orion_db_url}/data/db1",
            headers={"UserID": self.db_username, "Signature": signature},
        )

        if not response.ok:
            log_msg("\n\nERRROR HAPPENED\n\n")

        log_msg(f"Returned with {response.status}")
        response = await response.json()
        log_json(response)

    async def db_query_key(self, db_name, key):
        """
        https://labs.hyperledger.org/orion-server/docs/getting-started/transactions/curl/datatx#12-checking-the-existance-of-key1
        """
        # keys need to be send as base64, in order for =/- characters to work.
        enc_key = base64.urlsafe_b64encode(bytes(key, encoding="utf-8")).decode()

        payload = {"user_id": self.db_username, "db_name": db_name, "key": key}
        signature = self.__db_sign_tx(payload)

        response = await self.client_session.get(
            url=f"{self.__orion_db_url}/data/db1/{enc_key}",
            headers={"UserID": self.db_username, "Signature": signature},
        )

        if not response.ok:
            log_msg("\n\nERRROR HAPPENED\n\n")

        log_msg(f"Returned with {response.status}")
        response = await response.json()
        log_json(response)

        try:
            return response["response"]["value"]
        except Exception as e:
            raise e


async def main():
    auditor = Auditor()
    # try:
    # await auditor.db_query_all()

    # key = base64.urlsafe_b64encode(bytes("Controller_1", "utf-8"))
    # print(key.decode())
    # dec_key = base64.urlsafe_b64decode(key)
    # print(dec_key.decode())

    value = await auditor.db_query_key("db1", "Controller_1")
    log_msg(decode_data(value))

    # except Exception:
    await auditor.client_session.close()


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        os._exit(1)
