from algosdk.future.transaction import (
    ApplicationNoOpTxn,
    AssetTransferTxn,
)

from yieldly.constants import (
    APPLICATION_ID_PROXY,
    APPLICATION_ID_STAKING,
    ASSET_ID,
    ESCROW_ADDR,
)

from yieldly.operations.base import BaseOperation
from yieldly.util import get_account


class StakeOperation(BaseOperation):
    def __init__(self, amount):
        print(f"Staking {amount / 1e6:.6} YLDY")

        self.amount = amount

        super().__init__()

    def create_transactions(self):
        # Call Proxy contract
        self.transactions.append(
            ApplicationNoOpTxn(
                get_account(),
                self.params,
                APPLICATION_ID_PROXY,
                [b"check"],
            )
        )

        # Call Staking contract
        self.transactions.append(
            ApplicationNoOpTxn(
                get_account(),
                self.params,
                APPLICATION_ID_STAKING,
                [b"S"],
            )
        )

        # Transfer YLDY to Escrow
        self.transactions.append(
            AssetTransferTxn(
                get_account(),
                self.params,
                ESCROW_ADDR,
                self.amount,
                ASSET_ID,
            )
        )

    def sign_transactions(self, private_key, escrow_lsig):
        self.signed_transactions = [
            self.transactions[0].sign(private_key),
            self.transactions[1].sign(private_key),
            self.transactions[2].sign(private_key),
        ]
