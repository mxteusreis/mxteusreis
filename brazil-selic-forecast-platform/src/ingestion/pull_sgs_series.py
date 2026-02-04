from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.config import RAW_DIR
from src.ingestion.sgs_client import SGSClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download SGS series data from BCB")
    parser.add_argument("--series-id", type=int, default=11, help="SGS series code")
    parser.add_argument("--start-date", type=str, default=None, help="Start date DD/MM/YYYY")
    parser.add_argument("--end-date", type=str, default=None, help="End date DD/MM/YYYY")
    return parser.parse_args()


def save_series(data: list[dict], series_id: int) -> Path:
    df = pd.DataFrame(data)
    df.rename(columns={"data": "date", "valor": "value"}, inplace=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    output_path = RAW_DIR / f"selic_{series_id}_{timestamp}.csv"
    df.to_csv(output_path, index=False)
    return output_path


def run(series_id: int, start_date: str | None, end_date: str | None) -> Path:
    client = SGSClient()
    logger.info("Fetching series %s from SGS", series_id)
    data = client.fetch_series(series_id, start_date=start_date, end_date=end_date)
    output_path = save_series(data, series_id)
    logger.info("Saved raw series to %s", output_path)
    return output_path


if __name__ == "__main__":
    args = parse_args()
    run(args.series_id, args.start_date, args.end_date)
