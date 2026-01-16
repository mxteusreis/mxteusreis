"""Stream Binance price data into Kafka.

This producer fetches real-time prices from the public Binance API every 60 seconds
and publishes JSON events to the Kafka topic `crypto_prices`.
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import List

import requests
from kafka import KafkaProducer

BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/price"
DEFAULT_SYMBOLS = ["BTCUSDT", "ETHUSDT"]


def fetch_prices(symbols: List[str]) -> List[dict]:
    """Fetch latest prices from Binance for the given symbols."""
    response = requests.get(BINANCE_TICKER_URL, params={"symbols": json.dumps(symbols)}, timeout=10)
    response.raise_for_status()
    prices = response.json()

    event_time = datetime.now(timezone.utc).isoformat()
    events = []
    for item in prices:
        events.append(
            {
                "symbol": item["symbol"],
                "price": float(item["price"]),
                "event_time": event_time,
                "source": "binance",
            }
        )
    return events


def create_producer(bootstrap_servers: str) -> KafkaProducer:
    """Create a Kafka producer with JSON serialization."""
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8"),
        retries=3,
        linger_ms=100,
    )


def main() -> None:
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC", "crypto_prices")

    symbols_env = os.getenv("CRYPTO_SYMBOLS", ",".join(DEFAULT_SYMBOLS))
    symbols = [symbol.strip().upper() for symbol in symbols_env.split(",") if symbol.strip()]

    producer = create_producer(bootstrap_servers)

    while True:
        try:
            # Pull fresh prices and emit one event per symbol.
            events = fetch_prices(symbols)
            for event in events:
                producer.send(topic, key=event["symbol"], value=event)
            producer.flush()
            print(f"Published {len(events)} events to {topic} at {events[0]['event_time']}")
        except Exception as exc:  # noqa: BLE001 - keep producer resilient for demo purposes
            print(f"Error while producing events: {exc}")

        # Keep the interval stable to avoid hitting public API rate limits.
        time.sleep(60)


if __name__ == "__main__":
    main()
