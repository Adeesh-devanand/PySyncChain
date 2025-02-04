import asyncio
import hashlib
import time
import json
import base64
import ecdsa
import websockets
import os
from typing import List, Dict

MINING_REWARD = 10  # Reward for mining a block
P2P_PORT = 5000  # Websocket port for P2P communication
BLOCKCHAIN_FILE = "blockchain.json"  # Local blockchain storage


class Block:
    def __init__(self, index, previous_hash, transactions, miner_address, timestamp=None, nonce=0, block_hash=None):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.miner_address = miner_address
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.hash = block_hash or self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        prefix = '0' * difficulty
        while not self.hash.startswith(prefix):
            self.nonce += 1
            self.hash = self.compute_hash()


class Blockchain:
    def __init__(self, difficulty=4):
        self.difficulty = difficulty
        self.chain: List[Block] = self.load_chain_from_file()
        self.pending_transactions = []
        self.utxo_pool: Dict[str, float] = {}  # Track unspent transaction outputs
        if not self.chain:
            self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, "0", [], "", time.time())
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        self.save_chain_to_file()

    def load_chain_from_file(self):
        if os.path.exists(BLOCKCHAIN_FILE):
            with open(BLOCKCHAIN_FILE, "r") as file:
                return [Block(**block) for block in json.load(file)]
        return []

    def save_chain_to_file(self):
        with open(BLOCKCHAIN_FILE, "w") as file:
            json.dump([block.__dict__ for block in self.chain], file)

    def validate_block(self, block):
        if block.previous_hash != self.chain[-1].hash:
            return False
        reward_count = 0
        mempool_transactions = self.get_pending_transactions()

        for transaction in block.transactions:
            if transaction not in mempool_transactions and transaction["sender"] != "Network":
                print("Block rejected: Contains transactions not in mempool.")
                return False

            if transaction["sender"] != "Network" and self.utxo_pool.get(transaction["sender"], 0) < transaction[
                "amount"]:
                print("Block rejected: Double spending detected.")
                return False

            sender_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(transaction["public_key"]), curve=ecdsa.SECP256k1)
            message = f"{transaction['sender']}-{transaction['receiver']}-{transaction['amount']}"
            if not sender_key.verify(base64.b64decode(transaction["signature"].encode()), message.encode()):
                print("Block rejected: Invalid transaction signature.")
                return False

            if transaction["sender"] == "Network":
                reward_count += 1
                if transaction["receiver"] != block.miner_address or transaction["amount"] > MINING_REWARD:
                    print("Block rejected: Invalid mining reward.")
                    return False

        if reward_count != 1:
            print("Block rejected: Incorrect number of mining rewards.")
            return False

        return True

    async def broadcast_block(self, block):
        async with websockets.connect(f"ws://localhost:{P2P_PORT}") as websocket:
            await websocket.send(json.dumps(block.__dict__))

    async def receive_blocks(self, websocket, path):
        async for message in websocket:
            block_data = json.loads(message)
            block = Block(**block_data)
            if self.validate_block(block):
                self.add_block(block)
                print(f"New block added from network: {block.hash}")

    async def sync_with_peers(self):
        async with websockets.connect(f"ws://localhost:{P2P_PORT}") as websocket:
            await websocket.send(json.dumps({"action": "request_chain"}))
            response = await websocket.recv()
            new_chain = json.loads(response)
            if len(new_chain) > len(self.chain):  # Accept longest chain
                self.chain = [Block(**block) for block in new_chain]
                self.save_chain_to_file()

    async def start_p2p_server(self):
        async with websockets.serve(self.receive_blocks, "localhost", P2P_PORT):
            await asyncio.Future()


class Miner:
    def __init__(self, blockchain, miner_address):
        self.blockchain = blockchain
        self.miner_address = miner_address

    async def mine_pending_transactions(self):
        while True:
            await asyncio.sleep(5)
            transactions = self.blockchain.get_pending_transactions()
            if transactions:
                transactions.append({"sender": "Network", "receiver": self.miner_address, "amount": MINING_REWARD})
                new_block = Block(len(self.blockchain.chain), self.blockchain.chain[-1].hash, transactions,
                                  self.miner_address)
                new_block.mine_block(self.blockchain.difficulty)
                await self.blockchain.broadcast_block(new_block)
                self.blockchain.clear_pending_transactions()
                self.blockchain.save_chain_to_file()
                print(f"New block mined by {self.miner_address}: {new_block.hash}")


async def main():
    blockchain = Blockchain()
    await blockchain.sync_with_peers()
    miner = Miner(blockchain, "miner_wallet")
    p2p_server = asyncio.create_task(blockchain.start_p2p_server())
    miner_task = asyncio.create_task(miner.mine_pending_transactions())
    await asyncio.sleep(30)
    miner_task.cancel()
    p2p_server.cancel()
    print("Blockchain:")
    for block in blockchain.chain:
        print(json.dumps(block.__dict__, indent=4))


if __name__ == "__main__":
    asyncio.run(main())
