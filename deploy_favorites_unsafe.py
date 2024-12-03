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

    # We could do this next line as a shortcut :)
    # tx_hash = favorites_contract.constructor().transact()

    print("Building the transaction...")
    transaction = favorites_contract.constructor().build_transaction(
        {
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce,
            "gas": 3000000,  # Higher gas limit for RSK
            "gasPrice": w3.eth.gas_price * 2,  # Increase gas price to ensure transaction goes through
        }
    )

    print("Signing transaction...")
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    print("We signed it, check it out:")
    print(signed_txn)

    print("Deploying Contract!")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print("Waiting for transaction to finish...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Done! Contract deployed to {tx_receipt.contractAddress}")


if __name__ == "__main__":
    main()
