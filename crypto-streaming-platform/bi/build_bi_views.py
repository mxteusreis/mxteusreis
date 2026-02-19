from __future__ import annotations

import csv
import os
from pathlib import Path

from api.storage_repo import StorageRepo


BI_DIR = Path("bi/output")


def write_csv(path: Path, headers: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    storage_path = os.getenv("STORAGE_PATH", "data/app.duckdb")
    symbols = [s.strip().upper() for s in os.getenv("SYMBOLS", "BTCUSDT,ETHUSDT").split(",") if s.strip()]
    days = int(os.getenv("BI_DAYS", "90"))

    repo = StorageRepo(storage_path)
    for symbol in symbols:
        ohlc = repo.bi_daily_ohlc(symbol, days)
        volume = repo.bi_daily_volume(symbol, days)
        latest = repo.query_latest(symbol, 1)

        write_csv(BI_DIR / f"daily_ohlc_{symbol}.csv", ["date", "open", "high", "low", "close"], ohlc)
        write_csv(BI_DIR / f"daily_volume_{symbol}.csv", ["date", "volume"], volume)
        write_csv(
            BI_DIR / f"latest_prices_{symbol}.csv",
            ["symbol", "timestamp_utc", "lastPrice", "priceChangePercent", "volume", "source"],
            latest,
        )

    print(f"BI datasets created under {BI_DIR}")


if __name__ == "__main__":
    main()
