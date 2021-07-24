from typing import List, Union

from algosdk.future.transaction import (
    LogicSigTransaction,
    SignedTransaction,
    Transaction,
)

from yieldly.util import (
    get_client,
    get_escrow_lsig,
    get_params,
    get_private_key,
    group_transactions,
    wait_for_confirmation,
)


class BaseOperation:
    transactions: List[Transaction]
    signed_transactions: List[Union[SignedTransaction, LogicSigTransaction]]

    def __init__(self):
        self.params = get_params()

        self.transactions = []
        self.signed_transactions = []

    def prepare_transactions(self):
        self.create_transactions()

        if not self.transactions:
            raise Exception("No transactions to group.")

        group_transactions(self.transactions)

        escrow_lsig = get_escrow_lsig()
        private_key = get_private_key()

        self.sign_transactions(private_key, escrow_lsig)

    def send(self):
        self.prepare_transactions()

        if not self.signed_transactions:
            raise Exception("No signed transactions!")

        algod_client = get_client()

        txid = algod_client.send_transactions(self.signed_transactions)

        wait_for_confirmation(algod_client, txid)

    def create_transactions(self):
        raise NotImplementedError("Do not call BaseOperation directly.")

    def sign_transactions(self, private_key, escrow_lsig):
        raise NotImplementedError("Do not call BaseOperation directly.")
