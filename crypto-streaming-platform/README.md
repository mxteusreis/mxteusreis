# Crypto Streaming Platform

## Business Problem
Crypto markets move in seconds, and trading desks, research teams, and risk analysts need a
reliable, low-latency pipeline to capture price movements as they happen. This project delivers
that foundation by streaming real-time crypto prices into a scalable data pipeline that can feed
analytics, dashboards, and machine learning systems.

## Architecture Overview
1. **Binance Producer (Python)** pulls real-time prices from the public Binance API every 60 seconds.
2. **Kafka** receives the events in the `crypto_prices` topic as a durable streaming layer.
3. **Spark Structured Streaming** consumes the topic, parses JSON events, and prints them to the console.

This first release prioritizes a clean ingestion pipeline and a reproducible local setup.

## Tech Stack
- **Python** for the producer
- **Kafka + Zookeeper** for streaming ingestion
- **Docker Compose** for local infrastructure
- **Apache Spark (PySpark Structured Streaming)** for streaming consumption

## Repository Structure
```
crypto-streaming-platform/
├── producer/               # Binance API producer
├── kafka/                  # Docker Compose for Kafka
├── spark/                  # Spark streaming consumer
├── data/                   # Placeholder for pipeline outputs
├── notebooks/              # Reserved for future exploration
└── README.md
```

## How to Run Locally

### 1) Start Kafka
```bash
cd kafka
docker-compose up -d
```

### 2) Create the Kafka Topic
```bash
docker exec -it kafka bash -c \
  "kafka-topics --bootstrap-server localhost:9092 --create --topic crypto_prices --partitions 1 --replication-factor 1"
```

### 3) Run the Producer
```bash
cd ../producer
python binance_producer.py
```

Environment variables (optional):
- `KAFKA_BOOTSTRAP_SERVERS` (default: `localhost:9092`)
- `KAFKA_TOPIC` (default: `crypto_prices`)
- `CRYPTO_SYMBOLS` (default: `BTCUSDT,ETHUSDT`)

### 4) Run the Spark Streaming Consumer
```bash
cd ../spark
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 \
  streaming_job.py
```

You should see JSON records printed to the console as the producer publishes data.

## Next Planned Evolutions
- Delta Lake Bronze/Silver/Gold data lakehouse layout
- Volatility and market microstructure feature generation
- Machine learning models for anomaly detection and forecasting
- REST API for downstream consumption
- Kubernetes deployment for scalable streaming

## Notes
- This repository focuses on production-grade pipeline fundamentals, not notebooks or ML experimentation.
- Public Binance API is rate-limited; keep the 60-second interval for stability.
