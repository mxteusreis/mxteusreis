"""Kafka producer that publishes Binance ticker events."""

from __future__ import annotations

import json
import os
import time

from dotenv import load_dotenv
from kafka import KafkaProducer

from binance_client import fetch_ticker_24h


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

    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic_name = os.getenv("TOPIC_NAME", "crypto_prices")
    poll_interval_seconds = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
    symbols = _parse_symbols(os.getenv("SYMBOLS", "BTCUSDT,ETHUSDT"))

    if not symbols:
        raise ValueError("SYMBOLS cannot be empty")

    producer = build_producer(bootstrap_servers=bootstrap_servers)

    print(f"Producer started: topic={topic_name}, symbols={symbols}, interval={poll_interval_seconds}s")

    while True:
        try:
            events = fetch_ticker_24h(symbols)
            for event in events:
                producer.send(topic_name, key=event["symbol"], value=event)

            producer.flush()
            print(f"Published {len(events)} events to topic={topic_name}")
        except Exception as exc:  # noqa: BLE001
            print(f"Producer cycle failed: {exc}")

        time.sleep(poll_interval_seconds)


if __name__ == "__main__":
    main()
