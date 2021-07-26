#!/usr/bin/env python

from yieldly.operations import lottery, staking
from yieldly.util import post_slack_message

lottery_claim = lottery.ClaimOperation()
lottery_claim.send()

staking_claim = staking.ClaimOperation()
staking_claim.send()

claimed = lottery_claim.claimable + staking_claim.claimable["yldy"]

stake = staking.StakeOperation(amount=claimed)
stake.send()

post_slack_message(f'Claim & restake of {claimed / 1e6:.6} YLDY complete.')
