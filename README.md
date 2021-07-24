# Python / Yieldly Experiments

This repo contains my experimentation with the Yieldly smart contracts using the Algorand Python SDK.

I will add a better readme but the main things included are:

* The `yieldly/` folder contains a set of classes describing the currently implemented operations (e.g. claiming, staking)
* There are currently two scripts in the `scripts/` folder that utilise these:
* * `withdraw_restake.py` is a good test, it simply withdraws 1 YLDY and restakes it
* * `claim_restake.py` will perform the full claiming chain (from both NLL & YLDY staking), and restake the resulting YLDY

Example:

`python3 -m venv venv && source venv/bin/activate && PYTHONPATH scripts/withdraw_restake.py`

Important points:

* Set your account mnemonic in the `yieldly/constants.py` file - this allows the scripts to sign transactions
* A running Algorand node is required - enter the endpoint & token in `yieldly/constants.py`
* This repo is purely for educational purposes, it is very raw and I take no responsibility for any errors or loss of funds that you may encounter.