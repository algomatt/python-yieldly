#!/usr/bin/env python

from algosdk.future.transaction import (
    ApplicationNoOpTxn,
    PaymentTxn,
    LogicSigTransaction,
)

from yieldly.constants import (
    APPLICATION_ID_PROXY,
    APPLICATION_ID_LOTTERY,
    ESCROW_ADDR,
)

from yieldly.operations.base import BaseOperation
from yieldly.util import get_account


class WithdrawOperation(BaseOperation):
    def __init__(self, amount):
        print(f"Withdrawing from NLL Algo staking: {amount / 1e6:.6} Algo")

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
                APPLICATION_ID_LOTTERY,
                [b"W"],
                [ESCROW_ADDR],
            )
        )

        # Transfer Algo from Escrow
        self.transactions.append(
            PaymentTxn(
                ESCROW_ADDR, 
                self.params,
                get_account(),
                self.amount,
            )
        )

        # Pay for transaction #3 fee
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
