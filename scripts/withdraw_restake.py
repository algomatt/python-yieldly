#!/usr/bin/env python

from yieldly.operations.staking import StakeOperation, WithdrawOperation

# Amount to unstake in micro-YLDY (1000000 = 1 YLDY)
AMOUNT = 1000000

withdraw = WithdrawOperation(amount=AMOUNT)
withdraw.send()

stake = StakeOperation(amount=AMOUNT)
stake.send()
