# PySyncChain

![PySyncChain](https://img.shields.io/badge/Blockchain-P2P-blue.svg)  
![License](https://img.shields.io/badge/license-MIT-green.svg)  
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)  

PySyncChain is a high-performance, multithreaded, and asynchronous blockchain implemented in Python. It leverages `asyncio` for concurrent transaction processing, `threading` for efficient Proof-of-Work (PoW) mining, and `websockets` for real-time peer-to-peer (P2P) communication.

---

## 🚀 Features  

- **Asynchronous & Multithreaded**: Uses `asyncio` for non-blocking transaction processing and `threading` for parallel mining.  
- **Proof-of-Work (PoW) Mining**: Implements dynamically adjustable mining difficulty.  
- **UTXO-Based Double-Spending Prevention**: Ensures transaction security using unspent transaction outputs.  
- **ECDSA Digital Signatures**: Uses public-private key cryptography to authorize transactions.  
- **WebSockets for P2P Communication**: Supports real-time blockchain synchronization across nodes.  
- **Fault-Tolerant Peer Discovery**: Dynamically updates peer lists to maintain network consistency.  

---

## 🏗 Installation  

### Prerequisites  

- Python 3.8+  
- WebSockets library (`pip install websockets`)  
- ECDSA library (`pip install ecdsa`)  
- OpenSSL for cryptographic operations  

### Steps  

1. Clone the repository:  

  ```
  git clone https://github.com/yourusername/PySyncChain.git
  cd PySyncChain
  ```

2. Install dependencies:  

  ```
  pip install -r requirements.txt
  ```

3. Run a blockchain node:  

  ```
  python blockchain.py
  ```

4. Start a miner:  

  ```
  python miner.py
  ```

5. Run a second node for P2P communication:  

  ```
  python blockchain.py --peer ws://localhost:5000
  ```

---

## 📖 Usage  

- **Check blockchain status:**  
  ```
  python cli.py --status
  ```  

- **Create and broadcast a transaction:**  
  ```
  python cli.py --send --from <wallet_address> --to <recipient_address> --amount <value>
  ```

- **Start mining:**  
  ```
  python cli.py --mine
  ```

---

## 🛠️ Configuration  

Modify `config.json` to adjust mining difficulty, peer discovery settings, and network ports.  

```
{
  "mining_difficulty": 4,
  "p2p_port": 5000,
  "peer_discovery": true,
  "enable_logging": true
}
```  

---

## ⛏️ Mining & Multithreading  

1. **Proof-of-Work (PoW) Algorithm** - Miners solve a cryptographic puzzle based on a **difficulty target**.  
2. **Multithreaded Mining** - Uses Python’s `threading` to offload PoW computation to a separate worker thread.  
3. **Longest Chain Rule** - Nodes always follow the **chain with the most cumulative Proof-of-Work**.  

### **Mining a New Block (Multithreading Implementation)**  
```
import threading

def mine_block(block):
    while not block.hash.startswith("0" * difficulty):
        block.nonce += 1
        block.hash = block.compute_hash()

# Run mining in a separate thread
mining_thread = threading.Thread(target=mine_block, args=(block,))
mining_thread.start()
```  

---

## 🌐 Peer-to-Peer Networking  

Nodes communicate using **WebSockets**, allowing real-time **block broadcasting and chain synchronization**.  

### **Broadcast a New Block**  
```
async def broadcast_block(self, block):
    for peer in PEERS.copy():
        try:
            async with websockets.connect(f"ws://{peer}") as websocket:
                await websocket.send(json.dumps(block.__dict__))
        except:
            PEERS.remove(peer)
```  

### **Request Blockchain from Peers**  
```
async def sync_with_peers(self):
    for peer in PEERS:
        async with websockets.connect(peer) as websocket:
            await websocket.send(json.dumps({"action": "request_chain"}))
            response = await websocket.recv()
            new_chain = json.loads(response)
            if len(new_chain) > len(self.chain):
                self.chain = [Block(**block) for block in new_chain]
                self.save_chain_to_file()
```  

---

## 🛡️ Security  

- **ECDSA Digital Signatures**: Prevents unauthorized transactions.  
- **UTXO Model**: Ensures coins cannot be double-spent.  
- **Block Validation Rules**: Rejects invalid or tampered blocks.  
- **Automatic Peer Blacklisting**: Removes inactive or malicious peers.  

---

## 📜 License  

This project is licensed under the **MIT License**, a permissive open-source license that allows anyone to use, modify, and distribute the software with minimal restrictions.  

### Why MIT License?  

- **Freedom to Use**: Anyone can use, modify, and distribute the software.  
- **Permissive & Business-Friendly**: Allows commercial and private use without restrictions.  
- **Minimal Liability**: Protects contributors from legal claims.  
- **Broad Adoption**: The most widely used open-source license, making it easier for others to contribute.  

Full MIT License text:  

```
MIT License  

Copyright (c) 2025 Your Name  

Permission is hereby granted, free of charge, to any person obtaining a copy  
of this software and associated documentation files (the "Software"), to deal  
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
copies of the Software, and to permit persons to whom the Software is  
furnished to do so, subject to the following conditions:  

The above copyright notice and this permission notice shall be included in all  
copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
SOFTWARE.
```  

---

## 🤝 Contributing  

Contributions are welcome! Open an issue or submit a pull request to improve PySyncChain.  

---

## 📧 Contact  

For questions, reach out to **your-email@example.com** or visit the GitHub repository.  
