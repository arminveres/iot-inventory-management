"""
Demonstrative auditor to mark soft- or firmware as vulnerable
"""
# TODO: (aver)
# - add analysis of DB and post revocation

from aiohttp import (
    web,
    ClientSession,
    ClientRequest,
    ClientResponse,
    ClientError,
    ClientTimeout,
)


class Auditor:
    """
    Class that holds logic for a sample auditor, marking software as vulnerable.
    Works by querying the orion database and notifying the issuer, i.e., the admin of a
    vulnerability.
    """

    def __init__(self):
        self.client_session = ClientSession()


def main():
    auditor = Auditor()
    print("hello there")


if __name__ == "__main__":
    main()
