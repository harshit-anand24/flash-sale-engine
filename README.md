High-Concurrency Distributed Flash Sale Engine
A production-grade, distributed e-commerce backend engineered to handle high-concurrency flash sale events without inventory leakage or database exhaustion. The system processes a simulated high-volume traffic stampede by utilizing a hybrid memory-storage architecture, separating fast memory assertions from permanent persistence layers.

System Architecture & Design
Standard relational databases crash or allow race conditions under sudden e-commerce stampedes due to lock contention. This engine implements a Two-Phase Commit/Validation Pattern to safeguard data integrity:

Phase 1: Atomic Memory Throttling (Redis): Incoming traffic hits an asynchronous FastAPI gateway layer. Every request executes an atomic decrement operation. Because Redis operates single-threaded in-memory, inventory depletion occurs deterministically.

Phase 2: Guarded Persistence (MySQL via SQLAlchemy): Only if the Redis operation returns a valid positive index does the request proceed to write an ACID-compliant row into the MySQL storage layer. If the stock is empty, the server fires an optimized HTTP 423 Locked exception, dropping the connection before it ever burdens the database pool.

Tech Stack & Core Mechanics
FastAPI: High-performance, ASGI-compliant framework running modern Python lifespan context managers for reliable system setup and teardown.

Uvicorn Multiprocessing: Run with 4 distinct OS-level workers to maximize multi-core CPU Utilization.

Redis Driver: Acts as the high-speed distributed gatekeeper executing atomic memory shifts.

MySQL 8.0 & SQLAlchemy Engine: Handles reliable persistence utilizing connection optimization layers to eliminate resource starvation.

Locust Performance Framework: Used to test system constraints, scaling user pools dynamically.

Concurrency & Load Test Benchmarks
The system was benchmarked using an aggressive load profile simulating a classic flash-sale stampede scenario:

Peak Concurrency: 1,000 Concurrent Users

Spawn Ramp-up Rate: 100 users/second

Available Stock Inventory Initialized: 500 Units

The Results (Zero-Leak Verification)
During peak stress operations, the architecture maintained flawless transactional behavior:

Successful Allocations: Exactly 500 rows were successfully generated inside the MySQL ledger.

Auto-Increment Integrity: Primary keys map sequentially from 1 straight to 500 without gaps or duplicate allocations.

Graceful Rejection: Excess requests were safely terminated using low-overhead HTTP exceptions, allowing throughput to plateau efficiently without server dropouts.

Local Deployment & Replication
Prerequisites
Python 3.12+ (Anaconda environment recommended)

Redis Server (Running on default port 6379)

MySQL Server (Running on default port 3306)

1. Database Setup
Log into your MySQL interface and initialize the schema shell container named flash_sale.

2. Environment Installation
Clone the repository from your profile and use pip to install the required dependencies: fastapi, uvicorn, sqlalchemy, pymysql, redis, and locust.

3. Running the Server Engine
Navigate to your app directory and execute the main python application file. The server will initialize your 500 stock tokens inside Redis and mount Uvicorn workers on your local host port 8000.

4. Running the Traffic Swarm
Open a secondary terminal workspace and launch the locust simulation panel. Navigate to local host port 8089 inside your web browser, configure your peak concurrency limits, and start swarming.