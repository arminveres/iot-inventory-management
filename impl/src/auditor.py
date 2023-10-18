"""
Demonstrative auditor to mark soft- or firmware as vulnerable
"""
# TODO: (aver)
# - add analysis of DB and post revocation
import asyncio
import os

from aiohttp import ClientSession
from support.agent import DEFAULT_INTERNAL_HOST
from support.database import OrionDB
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

        self.db_client = OrionDB(
            orion_db_url=orion_db_url,
            username=db_username,
            client_session=self.client_session,
        )

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
        except Exception:
            log_msg(response)


async def main():
    auditor = Auditor()
    db_name = "db1"

    # TODO: (aver) fix and implement a query all keys, so we don't have to save them externally
    # await auditor.db_query_all("db1")

    value = await auditor.db_client.query_key(db_name, "Controller_1")
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
