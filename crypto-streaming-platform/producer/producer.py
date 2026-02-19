"""Producer that supports kafka mode (v1) and direct mode (v2)."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from kafka import KafkaProducer

from binance_client import fetch_ticker_24h

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from api.storage_repo import StorageRepo  # noqa: E402


def _parse_symbols(symbols_env: str) -> list[str]:
    return [symbol.strip().upper() for symbol in symbols_env.split(",") if symbol.strip()]


def build_producer(bootstrap_servers: str) -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        key_serializer=lambda key: key.encode("utf-8"),
        retries=3,
        linger_ms=50,
    )


def main() -> None:
    load_dotenv()

    broker_mode = os.getenv("BROKER_MODE", "kafka").lower()
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic_name = os.getenv("TOPIC_NAME", "crypto_prices")
    poll_interval_seconds = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
    storage_path = os.getenv("STORAGE_PATH", "data/app.db")
    symbols = _parse_symbols(os.getenv("SYMBOLS", "BTCUSDT,ETHUSDT"))

    if not symbols:
        raise ValueError("SYMBOLS cannot be empty")

    producer = build_producer(bootstrap_servers=bootstrap_servers) if broker_mode == "kafka" else None
    repo = StorageRepo(storage_path) if broker_mode == "direct" else None

    print(
        f"Producer started: mode={broker_mode}, topic={topic_name}, symbols={symbols}, interval={poll_interval_seconds}s"
    )

    while True:
        try:
            events = fetch_ticker_24h(symbols)
            if broker_mode == "kafka":
                assert producer is not None
                for event in events:
                    producer.send(topic_name, key=event["symbol"], value=event)
                producer.flush()
                print(f"Published {len(events)} events to topic={topic_name}")
            elif broker_mode == "direct":
                assert repo is not None
                repo.upsert_events(events)
                print(f"Persisted {len(events)} events directly to {storage_path}")
            else:
                raise ValueError("BROKER_MODE must be either 'kafka' or 'direct'")
        except Exception as exc:  # noqa: BLE001
            print(f"Producer cycle failed: {exc}")

        time.sleep(poll_interval_seconds)


if __name__ == "__main__":
    main()
