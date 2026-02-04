from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(
    os.getenv("SELIC_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CURATED_DIR = DATA_DIR / "curated"
GOLD_DIR = DATA_DIR / "gold"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
DATASETS_DIR = PROJECT_ROOT / "datasets"

for directory in [RAW_DIR, CURATED_DIR, GOLD_DIR, ARTIFACTS_DIR, DATASETS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
