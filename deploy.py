import json
import os
from solcx import compile_standard, install_solc
from web3 import Web3
from dotenv import load_dotenv
import web3

load_dotenv()

with open("./contracts/Storage.sol", "r") as file:
    storage_file = file.read()
install_solc("0.8.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Storage.sol": {"content": storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["Storage.sol"]["Storage"]["evm"]["bytecode"][
    "object"
]

abi = compiled_sol["contracts"]["Storage.sol"]["Storage"]["abi"]

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chain_id = 1337
my_address = "0xd83999CA7d1ee8b0E8cdA1448880829E17828eF5"
private_key = os.getenv("PRIVATE_KEY")


Storage = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.getTransactionCount(my_address)
# 1. Build Txn, 2. Sign Txn. 3. Send Txn
print("Deploying contract...")
transaction = Storage.constructor().build_transaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# wait for some confirmation blocks
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")
# working with the contract required contract address and contract abi
storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print("Storing data...")
store_transaction = storage.functions.store(5).build_transaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)
signed_stored_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
stored_txn_hash = w3.eth.send_raw_transaction(signed_stored_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(stored_txn_hash)
print("Data Stored!")
print(storage.functions.retrieve().call())
