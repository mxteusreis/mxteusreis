from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import GOLD_DIR, RAW_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_raw_files() -> pd.DataFrame:
    raw_files = sorted(RAW_DIR.glob("*.csv"))
    if not raw_files:
        raise FileNotFoundError("No raw files found. Run ingestion first.")
    frames = [pd.read_csv(file) for file in raw_files]
    return pd.concat(frames, ignore_index=True)


def build_dataset() -> Path:
    df = load_raw_files()
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date", "value"]).sort_values("date")
    df = df.drop_duplicates(subset=["date"], keep="last")
    output_path = GOLD_DIR / "selic_dataset.csv"
    df.to_csv(output_path, index=False)
    logger.info("Saved gold dataset to %s", output_path)
    return output_path


if __name__ == "__main__":
    build_dataset()
