#!/usr/bin/env python

from yieldly.util import calculate_claimable, get_account

from algosdk.future.transaction import (
    ApplicationNoOpTxn,
    AssetTransferTxn,
    PaymentTxn,
    LogicSigTransaction,
)

from yieldly.constants import (
    APPLICATION_ID_PROXY,
    APPLICATION_ID_LOTTERY,
    ASSET_ID,
    ESCROW_ADDR,
)

from yieldly.operations.base import BaseOperation


class ClaimOperation(BaseOperation):
    def __init__(self):
        self.claimable = calculate_claimable(APPLICATION_ID_LOTTERY, total_key="TYUL")

        print("Claiming from NLL:")
        print(f"{self.claimable / 1e6:.6} YLDY")

        super().__init__()

    def create_transactions(self):
        if not self.claimable:
            raise Exception("No claimable YLDY.")

        # Call Proxy contract
        self.transactions.append(
            ApplicationNoOpTxn(
                get_account(),
                self.params,
                APPLICATION_ID_PROXY,
                [b"check"],
            )
        )

        # Call Lottery contract for YLDY withdrawal
        self.transactions.append(
            ApplicationNoOpTxn(
                get_account(),
                self.params,
                APPLICATION_ID_LOTTERY,
                [b"CA"],
                [ESCROW_ADDR],
            )
        )

        # Transfer YLDY from Escrow
        self.transactions.append(
            AssetTransferTxn(
                ESCROW_ADDR,
                self.params,
                get_account(),
                self.claimable,
                ASSET_ID,
            )
        )

        # Pay for withdrawal fees
        self.transactions.append(
            PaymentTxn(
                get_account(),
                self.params,
                ESCROW_ADDR,
                self.params.fee,
            )
        )

    def sign_transactions(self, private_key, escrow_lsig):
        self.signed_transactions = [
            self.transactions[0].sign(private_key),
            self.transactions[1].sign(private_key),
            LogicSigTransaction(self.transactions[2], escrow_lsig),
            self.transactions[3].sign(private_key),
        ]
