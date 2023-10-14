"""
Demonstrative auditor to mark soft- or firmware as vulnerable
"""
# TODO: (aver)
# - add analysis of DB and post revocation
import asyncio
import base64
import json
import os

from aiohttp import ClientSession
from support.agent import DEFAULT_INTERNAL_HOST
from support.database import decode_data, encode_data, sign_transaction
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

    async def db_query_all(self, db_name):
        """
        https://github.com/hyperledger-labs/orion-server/blob/0009ffdf5f35e8cf9e6a938378733d4e5e6474d1/pkg/constants/http.go#L97
        """
        # FIXME: dunno how to fix this method, documentation is not existent and if I imitate the source
        # code I get 404
        key = "Controller_1"
        key = ""
        enc_key = base64.urlsafe_b64encode(bytes(key, encoding="utf-8")).decode()
        payload = {
            "user_id": self.db_username,
            "db_name": db_name,
            "start_key": key,
            "end_key": key,
            "limit": 10,
        }
        signature = self.__db_sign_tx(payload)
        response = await self.client_session.get(
            # url=f"{self.__orion_db_url}/data/db1/startkey={enc_key}&endkey={enc_key}/",
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

        enc_value = response["response"]["value"]
        dec_value = decode_data(enc_value)

        try:
            return dec_value
        except Exception as e:
            log_msg(e.with_traceback())

    def check_vulnerability(self, db_name, components):
        return [
            {
                "vulnerability": {"software": {"shady_stuff": 0.9}},
                "db_name": db_name,
            }
        ]

    async def notify_maintainer(self, db_name, vulnerabilities):
        response = await self.client_session.post(
            url=f"http://{DEFAULT_INTERNAL_HOST}:8012/webhooks/topic/notify_vulnerability/",
            json=vulnerabilities,
        )
        if not response.ok:
            log_msg("\n\nERRROR HAPPENED\n\n")
        log_msg(f"Returned with {response.status}")
        try:
            response = await response.json()
            log_json(response)
        except:
            log_msg(response)


async def main():
    auditor = Auditor()
    db_name = "db1"

    # TODO: (aver) fix and implement a query all keys, so we don't have to save them externally
    # await auditor.db_query_all("db1")

    value = await auditor.db_query_key(db_name, "Controller_1")
    log_json(value)
    # do some magic, analysis and return with the marked vulnerable component send revoke request to issuer
    marked_vulnerabilities = auditor.check_vulnerability(db_name, value["components"])
    await auditor.notify_maintainer(db_name, marked_vulnerabilities)

    # except Exception:
    await auditor.client_session.close()


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        os._exit(1)
