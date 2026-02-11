# crypto-streaming-platform

A reproducible streaming pipeline that ingests real crypto market snapshots from Binance, publishes events to Kafka, and stores a raw append-only history for later analytics.

## What problem does this solve?
Most free crypto sources expose only current snapshots or limited history. For data engineering use cases (auditing, analytics baselines, and future feature generation), teams need a reliable pipeline that continuously captures market events and persists the raw trail.

This project solves that by building a local-first streaming pipeline that can be extended to cloud/public deployment in future phases.

## Architecture (v1)

```text
Binance API (ticker/24hr)
    -> Producer (Python)
    -> Kafka topic: crypto_prices
    -> Consumer (Python)
    -> Raw Storage (JSONL in data/raw/)
```

## Project structure

```text
crypto-streaming-platform/
├── README.md
├── .gitignore
├── requirements.txt
├── .env.example
├── Makefile
├── docker/
│   └── docker-compose.yml
├── producer/
│   ├── binance_client.py
│   └── producer.py
├── consumer/
│   ├── consumer.py
│   └── storage.py
├── data/
│   ├── raw/
│   └── README.md
└── tests/
    └── test_binance_client.py
```

## Quickstart

1. Install dependencies:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy environment file:
   ```bash
   cp .env.example .env
   ```
3. Start Kafka and create topic automatically:
   ```bash
   make up
   ```
4. Run consumer in terminal #1:
   ```bash
   make consumer
   ```
5. Run producer in terminal #2:
   ```bash
   make producer
   ```
6. Check raw files:
   ```bash
   ls data/raw/
   tail -n 5 data/raw/crypto_prices_YYYY-MM-DD.jsonl
   ```

## Configuration

- `KAFKA_BOOTSTRAP_SERVERS` (default: `localhost:9092`)
- `TOPIC_NAME` (default: `crypto_prices`)
- `SYMBOLS` (default: `BTCUSDT,ETHUSDT`)
- `POLL_INTERVAL_SECONDS` (default: `60`)
- `CONSUMER_GROUP_ID` (default: `crypto-raw-consumer`)

## Data contract

Each event sent to Kafka and persisted in raw storage follows this schema:

```json
{
  "timestamp_utc": "2026-01-15T14:03:22.913852+00:00",
  "symbol": "BTCUSDT",
  "lastPrice": "68001.20",
  "priceChangePercent": "1.87",
  "volume": "24567.123",
  "source": "binance_api_v3_ticker_24hr"
}
```

## Commands

```bash
make up        # start Kafka + Zookeeper + topic init
make down      # stop all containers
make producer  # run producer loop
make consumer  # run consumer loop
make test      # run tests
```

## Roadmap (v2+)

- Bronze/Silver/Gold layered modeling
- Volatility and derived market metrics
- REST API for historical queries
- Stable CSV datasets in `/bi/*` for Looker Studio
- Public free deployment (API + UI)
- Future Kubernetes orchestration
