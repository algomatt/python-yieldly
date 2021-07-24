import base64
import time

from algosdk import mnemonic
from algosdk.v2client import algod
from algosdk.future import transaction
from algosdk.future.transaction import LogicSig

from .constants import (
    ACCOUNT_PASS,
    ALGOD_ADDRESS,
    ALGOD_TOKEN,
    ESCROW_PROGRAM_STR,
)


def get_client():
    return algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)


def get_params():
    params = get_client().suggested_params()
    params.flat_fee = True
    params.fee = 1000

    return params


def get_escrow_lsig():
    program = base64.decodebytes(ESCROW_PROGRAM_STR.encode())

    return LogicSig(program)


def get_private_key():
    return mnemonic.to_private_key(ACCOUNT_PASS)


def get_account():
    return mnemonic.to_public_key(ACCOUNT_PASS)


def group_transactions(txns):
    gid = transaction.calculate_group_id(txns)

    for txn in txns:
        txn.group = gid


def wait_for_confirmation(client, txid):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    last_round = client.status().get("last-round")

    txinfo = client.pending_transaction_info(txid)

    while not (txinfo.get("confirmed-round") and txinfo.get("confirmed-round") > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)

    print(f"Transaction {txid} confirmed in round {txinfo['confirmed-round']}.")

    return txinfo


def process_state(raw_state):
    state = {}

    for item in raw_state:
        key = base64.b64decode(item["key"]).decode()

        if item["value"].get("bytes"):
            value = item["value"]["bytes"]
        else:
            value = item["value"]["uint"]

        state[key] = value

    return state


def process_account_state(account):
    app_state = {}

    for raw_app_state in account["apps-local-state"]:
        if "key-value" not in raw_app_state:
            continue

        app_state[raw_app_state["id"]] = process_state(raw_app_state["key-value"])

    return app_state


def calculate_claimable(application_id, total_key="TYUL"):
    client = get_client()

    global_state = process_state(
        client.application_info(application_id)["params"]["global-state"]
    )

    user_state = process_account_state(client.account_info(get_account()))[
        application_id
    ]

    days_since_gt = (time.time() - global_state["GT"]) // 86400
    days_since_ut = (time.time() - user_state["UT"]) // 86400

    gss = global_state["GSS"] + (global_state["GA"] * days_since_gt)
    uss = user_state.get("USS", 0) + (user_state["UA"] * days_since_ut)

    return int(global_state[total_key] * (uss / gss))
