"""Storage helpers for raw append-only JSONL history."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

RAW_DATA_DIR = Path("data/raw")


def _extract_date(event: dict) -> str:
    timestamp = event.get("timestamp_utc")
    if timestamp:
        return timestamp[:10]
    return datetime.now(timezone.utc).date().isoformat()


def append_events_jsonl(events: list[dict], base_path: Path = RAW_DATA_DIR) -> Path | None:
    """Append events to a date-partitioned JSONL file."""
    if not events:
        return None

    date_ref = _extract_date(events[0])
    base_path.mkdir(parents=True, exist_ok=True)
    target_file = base_path / f"crypto_prices_{date_ref}.jsonl"

    with target_file.open("a", encoding="utf-8") as outfile:
        for event in events:
            outfile.write(json.dumps(event, ensure_ascii=False) + "\n")

    return target_file
