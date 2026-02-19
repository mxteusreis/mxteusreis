from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from api.storage_repo import StorageRepo  # noqa: E402


def write_events_to_db(events: list[dict], storage_path: str) -> None:
    repo = StorageRepo(storage_path)
    repo.upsert_events(events)
