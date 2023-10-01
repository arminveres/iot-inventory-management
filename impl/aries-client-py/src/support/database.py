"""
Contains a host of helper functions for managing the Orion database
"""
import json
from support.utils import log_msg, run_executable


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


def encode_data():
    raise NotImplementedError


def decode_data():
    raise NotImplementedError
