#!/usr/bin/env python

from yieldly.operations import lottery, staking
from yieldly.util import post_slack_message

claimed = 0

lottery_claim = lottery.ClaimOperation()

if lottery_claim.claimable:
    lottery_claim.send()
    claimed += lottery_claim.claimable

staking_claim = staking.ClaimOperation()

if staking_claim.claimable["yldy"]:
    staking_claim.send()
    claimed += staking_claim.claimable["yldy"]

stake = staking.StakeOperation(amount=claimed)
stake.send()

post_slack_message(f"Claim & restake of {claimed / 1e6:.6} YLDY complete.")
