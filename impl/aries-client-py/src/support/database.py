"""
Contains a host of helper functions for managing the Orion database
"""
import base64
import json
from uuid import uuid4

from support.utils import log_msg, run_executable

# TODO: (aver) create class to hold database logic for less duplication


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
