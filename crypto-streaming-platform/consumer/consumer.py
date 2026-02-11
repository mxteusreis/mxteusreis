"""Kafka consumer that stores raw events into JSONL files."""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from kafka import KafkaConsumer

from storage import append_events_jsonl


def build_consumer(
    bootstrap_servers: str,
    topic_name: str,
    group_id: str,
) -> KafkaConsumer:
    return KafkaConsumer(
        topic_name,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda raw: json.loads(raw.decode("utf-8")),
    )


def main() -> None:
    load_dotenv()

    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic_name = os.getenv("TOPIC_NAME", "crypto_prices")
    group_id = os.getenv("CONSUMER_GROUP_ID", "crypto-raw-consumer")

    consumer = build_consumer(
        bootstrap_servers=bootstrap_servers,
        topic_name=topic_name,
        group_id=group_id,
    )

    print(f"Consumer started: topic={topic_name}, group_id={group_id}")

    for message in consumer:
        event = message.value
        target_file = append_events_jsonl([event])
        print(f"Stored 1 event in {target_file}")


if __name__ == "__main__":
    main()
