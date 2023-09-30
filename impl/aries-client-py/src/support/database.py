"""
Contains a host of helper functions for managing the Orion database
"""
import json
from support.utils import run_executable


def sign_transaction(data, privatekey):
    print(f"'{json.dumps(data)}'")
    signature = run_executable(
        (
            "./bin/signer",
            f"-data='{json.dumps(data)}'",
            f"-privatekey={privatekey}",
        )
    )
    return signature


def encode_data():
    raise NotImplementedError


def decode_data():
    raise NotImplementedError
