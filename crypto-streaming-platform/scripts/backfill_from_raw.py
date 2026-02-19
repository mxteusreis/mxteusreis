from __future__ import annotations

import json
import os
from pathlib import Path

from api.storage_repo import StorageRepo


def main() -> None:
    raw_dir = Path(os.getenv("RAW_DATA_DIR", "data/raw"))
    storage_path = os.getenv("STORAGE_PATH", "data/app.db")

    repo = StorageRepo(storage_path)
    count = 0

    for file in sorted(raw_dir.glob("*.jsonl")):
        events = []
        with file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                events.append(json.loads(line))
        repo.upsert_events(events)
        count += len(events)
        print(f"Backfilled {len(events)} events from {file}")

    print(f"Done. Total events processed: {count}")


if __name__ == "__main__":
    main()
