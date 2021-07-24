from yieldly.util import calculate_claimable, get_account

from algosdk.future.transaction import (
    ApplicationNoOpTxn,
    AssetTransferTxn,
    PaymentTxn,
    LogicSigTransaction,
)

from yieldly.constants import (
    APPLICATION_ID_PROXY,
    APPLICATION_ID_STAKING,
    ASSET_ID,
    ESCROW_ADDR,
)

from yieldly.operations.base import BaseOperation


class ClaimOperation(BaseOperation):
    def __init__(self):
        self.claimable = {
            "algo": calculate_claimable(APPLICATION_ID_STAKING, total_key="TAP"),
            "yldy": calculate_claimable(APPLICATION_ID_STAKING, total_key="TYUL"),
        }

        print("Claiming from YLDY staking:")
        print(f"{self.claimable['algo'] / 1e6:.6} ALGO")
        print(f"{self.claimable['yldy'] / 1e6:.6} YLDY")

        super().__init__()

    def create_transactions(self):
        if not self.claimable["algo"]:
            raise Exception("No claimable ALGO.")

        if not self.claimable["yldy"]:
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

        # Call Staking contract for YLDY withdrawal
        self.transactions.append(
            ApplicationNoOpTxn(
                get_account(),
                self.params,
                APPLICATION_ID_STAKING,
                [b"CA"],
                [ESCROW_ADDR],
            )
        )

        # Call Staking contract for ALGO withdrawal
        self.transactions.append(
            ApplicationNoOpTxn(
                get_account(),
                self.params,
                APPLICATION_ID_STAKING,
                [b"CAL"],
                [ESCROW_ADDR],
            )
        )

        # Transfer YLDY from Escrow
        self.transactions.append(
            AssetTransferTxn(
                ESCROW_ADDR,
                self.params,
                get_account(),
                self.claimable["yldy"],
                ASSET_ID,
            )
        )

        # Transfer ALGO from Escrow
        self.transactions.append(
            PaymentTxn(
                ESCROW_ADDR,
                self.params,
                get_account(),
                self.claimable["algo"],
            )
        )

        # Pay for withdrawal fees
        self.transactions.append(
            PaymentTxn(
                get_account(),
                self.params,
                ESCROW_ADDR,
                self.params.fee * 2,
            )
        )

    def sign_transactions(self, private_key, escrow_lsig):
        self.signed_transactions = [
            self.transactions[0].sign(private_key),
            self.transactions[1].sign(private_key),
            self.transactions[2].sign(private_key),
            LogicSigTransaction(self.transactions[3], escrow_lsig),
            LogicSigTransaction(self.transactions[4], escrow_lsig),
            self.transactions[5].sign(private_key),
        ]
