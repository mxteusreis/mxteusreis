from __future__ import annotations

import os

from api.storage_repo import StorageRepo


def main() -> None:
    storage_path = os.getenv("STORAGE_PATH", "data/app.db")
    symbol = os.getenv("VERIFY_SYMBOL", "BTCUSDT")
    repo = StorageRepo(storage_path)

    ohlc = repo.bi_daily_ohlc(symbol, 30)
    volume = repo.bi_daily_volume(symbol, 30)

    assert not ohlc or set(ohlc[0].keys()) == {"date", "open", "high", "low", "close"}
    assert not volume or set(volume[0].keys()) == {"date", "volume"}

    print("BI contract verification passed")


if __name__ == "__main__":
    main()
