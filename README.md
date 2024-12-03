# Deploying a Vyper Smart Contract to RootStock (RSK) Testnet using Python

<p align="center">
 <img width="1000" src="https://github.com/EdwinLiavaa/Web3py-Vyper-RootStock/blob/main/pic.png">
</p>

## Table of Contents
- [Deploying a Vyper Smart Contract to RootStock (RSK) Testnet using Python](#deploying-a-vyper-smart-contract-to-rootstock-rsk-testnet-using-python)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [uv](#uv)
    - [pip/python](#pippython)
  - [Quickstart](#quickstart)
  - [Setup Environment](#setup-environment)
  - [Configuration](#configuration)
  - [Get Testnet RBTC](#get-testnet-rbtc)
  - [The Smart Contract](#the-smart-contract)
  - [Deployment Script](#deployment-script)
  - [Key Points About RSK Deployment](#key-points-about-rsk-deployment)
  - [Running the Deployment](#running-the-deployment)

This guide walks through the process of deploying a smart contract to the RootStock (RSK) testnet using Python and Web3.py. We'll be deploying a simple Vyper contract that demonstrates how to interact with the RSK network.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
  - You'll know you've done it right if you can run `uv --version` and see a version number.
- [git](https://git-scm.com/)
  - You'll know you've done it right if you can run `git --version` and see a version number.
  - Helpful shortcut:
  
```bash
# For bash
echo "source $HOME/.bashrc >> $HOME/.bash_profile"

# For zsh
echo "source $HOME/.zshenv >> $HOME/.zprofile"
```

- Python 3.x
- A text editor
- Basic understanding of smart contracts and Python
- RSK testnet RBTC (will show you how to get this)

## Installation

```bash
git clone https://github.com/cyfrin/web3py-favorites-cu
cd web3py-favorites-cu
```

### uv 

```bash
uv sync
```

### pip/python

```bash
python -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Quickstart

```bash
uv run hello.py # for UV
# or
python hello.py # for pip/python
```

## Setup Environment

First, let's set up our Python environment and install the necessary packages:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install required packages
pip install python-dotenv web3 vyper
```

## Configuration

Create a `.env` file in your project root with your configuration:

```env
RPC_URL="https://rpc.testnet.rootstock.io/[YOUR-API-KEY]"
PRIVATE_KEY="your-private-key"  # Never commit your real private key!
MY_ADDRESS="your-wallet-address"
```
THIS IS ONLY FOR TESTING - TYPICALLY YOU SHOULD NEVER SHARE YOUR PRIVATE KEY.

## Get Testnet RBTC

Before deploying, you'll need some testnet RBTC:

1. Go to the RSK faucet: https://faucet.rsk.co/
2. Enter your wallet address
3. Complete the captcha and request funds
4. Wait a few minutes for the transaction to be confirmed

## The Smart Contract

Here's our simple Vyper contract (`favorites.vy`):

```python
# @version ^0.3.7

favorite_number: public(uint256)
owner: public(address)

@external
def __init__():
    self.owner = msg.sender
    self.favorite_number = 0

@external
def store(new_number: uint256):
    self.favorite_number = new_number
```

## Deployment Script

Here's our Python script to deploy the contract (`deploy_favorites_unsafe.py`):

```python
from web3 import Web3
from dotenv import load_dotenv
from vyper import compile_code
import os

load_dotenv()

RPC_URL = os.getenv("RPC_URL")

def main():
    print("Let's read in the Vyper code and deploy it to the blockchain!")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    with open("favorites.vy", "r") as favorites_file:
        favorites_code = favorites_file.read()
        compliation_details = compile_code(
            favorites_code, output_formats=["bytecode", "abi"]
        )

    chain_id = 31  # RSK testnet chain ID

    print("Getting environment variables...")
    my_address = os.getenv("MY_ADDRESS")
    private_key = os.getenv("PRIVATE_KEY")

    # Check balance before deployment
    balance = w3.eth.get_balance(my_address)
    balance_in_rbtc = w3.from_wei(balance, "ether")
    print(f"Account balance: {balance_in_rbtc} RBTC")

    if balance == 0:
        print("Your account has no RBTC! Please get some testnet RBTC from the faucet:")
        print("1. Go to https://faucet.rsk.co/")
        print("2. Enter your address:", my_address)
        print("3. Complete the captcha and request funds")
        print("4. Wait a few minutes for the transaction to be confirmed")
        return

    # Create the contract in Python
    favorites_contract = w3.eth.contract(
        abi=compliation_details["abi"], bytecode=compliation_details["bytecode"]
    )

    # Submit the transaction that deploys the contract
    nonce = w3.eth.get_transaction_count(my_address)

    print("Building the transaction...")
    transaction = favorites_contract.constructor().build_transaction(
        {
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce,
            "gas": 3000000,  # Higher gas limit for RSK
            "gasPrice": w3.eth.gas_price * 2,  # Double the gas price to ensure transaction goes through
        }
    )

    print("Signing transaction...")
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    print("Deploying contract...")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Contract deployed! Address: {tx_receipt.contractAddress}")

if __name__ == "__main__":
    main()
```

## Key Points About RSK Deployment

1. **Chain ID**: RSK testnet uses chain ID 31
2. **Gas Settings**: 
   - We use a higher gas limit (3,000,000) for RSK
   - We double the gas price to ensure the transaction goes through
3. **Transaction Type**: 
   - RSK works best with legacy transactions (using `gasPrice` instead of EIP-1559 parameters)

## Running the Deployment

Execute the deployment script:

```bash
python deploy_favorites_unsafe.py
