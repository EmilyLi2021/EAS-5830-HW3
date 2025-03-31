from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import json
import os

URL = 'https://api.avax-test.network/ext/bc/C/rpc'
abi_file = 'NFT.abi'
contract_address = '0x85ac2e065d4526FBeE6a2253389669a12318A412'
private_key = '0x90d95f1f6817ca2b02a8659feae338dda7f5d63d8fa0f10b0710c8a7d52c6397'

def main():
    # Connect to the Avalanche Fuji testnet
    w3 = Web3(Web3.HTTPProvider(URL))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Load the contract ABI
    with open(abi_file, 'r') as abi_definition:
        abi = json.load(abi_definition)

    # Create a contract instance
    contract = w3.eth.contract(address=contract_address, abi=abi)

    # Get the account from the private key
    account = Account.from_key(private_key)

    # Get the nonce for the account
    nonce = w3.eth.getTransactionCount(account.address)

    for i in range(10):
        # Generate a random nonce
        random_nonce = os.urandom(32)

        # Create the transaction
        transaction = contract.functions.claim(random_nonce).buildTransaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': w3.to_wei('25', 'gwei')
        })

        # Sign the transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

        try:
            # Send the transaction
            txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            print(f"Transaction sent with hash: {txn_hash.hex()}")

            # Wait for the transaction to be mined
            txn_receipt = w3.eth.waitForTransactionReceipt(txn_hash)
            print(f"Transaction receipt: {txn_receipt}")

            # check balance
            balance = contract.functions.balanceOf(account.address).call()
            print(f"Balance after claiming: {balance}")

            if balance > 0:
                print(f"NFT claimed successfully! Current balance: {balance}")
                break
            else:
                print("NFT claim failed. Retrying...")
        except Exception as e:
            print(f"Error sending transaction: {e}")
    

if __name__ == '__main__':
    main()