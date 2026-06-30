High-Concurrency Distributed Flash Sale Engine
A production-grade, distributed e-commerce backend engineered to handle high-concurrency flash sale events without inventory leakage or database exhaustion. The system processes a simulated high-volume traffic stampede by utilizing a hybrid memory-storage architecture, separating fast memory assertions from permanent persistence layers.

🏗️ System Architecture & Design
Standard relational databases crash or allow race conditions under sudden e-commerce stampedes due to lock contention. This engine implements a Two-Phase Commit/Validation Pattern to safeguard data integrity:

Plaintext
  [ 1,000 Concurrent Shoppers (Locust) ]
                     │
                     ▼
          [ 4x Uvicorn parallel Workers ]
                     │
       ┌─────────────┴─────────────┐
       ▼                           ▼
[ Phase 1: Redis RAM ]     [ Phase 2: Relational Disk ]
  Atomic Decr Token          Asynchronous ACID Write
  (Locks Inventory)          (Persists Order Ledger)
       │                           │
  If Count < 0               SQLAlchemy Pool
  Reject instantly           Only 500 rows created
Phase 1: Atomic Memory Throttling (Redis): Incoming traffic hits an asynchronous FastAPI gateway layer. The inventory count is decoupled from the disk and stored completely inside a central Redis instance. Every request executes an atomic DECR operation. Because Redis operates single-threaded in-memory, inventory depletion occurs deterministically.

Phase 2: Guarded Persistence (MySQL via SQLAlchemy): Only if the Redis operation returns a valid positive index does the request proceed to write an ACID-compliant row into the MySQL storage layer. If the stock is empty, the server fires an optimized HTTP 423 Locked exception, dropping the connection before it ever burdens the database pool.

⚡ Tech Stack & Core Mechanics
FastAPI: High-performance, ASGI-compliant framework running modern Python lifespan context managers for reliable system setup and teardown.

Uvicorn Multiprocessing: Run with 4 distinct OS-level workers to maximize multi-core CPU Utilization.

Redis Driver: Acts as the high-speed distributed gatekeeper executing atomic memory shifts.

MySQL 8.0 & SQLAlchemy Engine: Handles reliable persistence utilizing connection optimization layers to eliminate resource starvation.

Locust Performance Framework: Used to test system constraints, scaling user pools dynamically.

📈 Concurrency & Load Test Benchmarks
The system was benchmarked using an aggressive load profile simulating a classic flash-sale stampede scenario:

Peak Concurrency: 1,000 Concurrent Users

Spawn Ramp-up Rate: 100 users/second

Available Stock Inventory Initialized: 500 Units

The Results (Zero-Leak Verification)
During peak stress operations, the architecture maintained flawless transactional behavior:

Successful Allocations: Exactly 500 rows were successfully generated inside the MySQL ledger (SELECT COUNT(*) FROM orders; returned 500).

Auto-Increment Integrity: Primary keys map sequentially from 1 to 500 without gaps or duplicate allocations.

Graceful Rejection: Excess requests were safely terminated using low-overhead HTTP exceptions, allowing throughput to plateau efficiently without server dropouts.

🚀 Local Deployment & Replication
Prerequisites
Python 3.12+ (Anaconda environment recommended)

Redis Server (Running on default port 6379)

MySQL Server (Running on default port 3306)

1. Database Setup
Log into your MySQL interface and initialize the schema shell container:

SQL
CREATE DATABASE flash_sale;
2. Environment Installation
Clone the repository and install dependencies:

Bash
git clone https://github.com/YOUR_GITHUB_USERNAME/flash-sale-engine.git
cd flash-sale-engine
pip install fastapi uvicorn sqlalchemy pymysql redis locust
3. Running the Server Engine
Navigate to the source workspace and spin up the multi-worker deployment:

Bash
cd app
python main.py
The server will initialize your 500 stock tokens inside Redis and mount Uvicorn workers on http://127.0.0.1:8000.

4. Running the Traffic Swarm
Open a secondary terminal workspace and launch the simulation panel:

Bash
locust -f locustfile.py --host=http://127.0.0.1:8000
Navigate to http://localhost:8089 inside your web browser, configure your concurrency spikes, and start swarming.