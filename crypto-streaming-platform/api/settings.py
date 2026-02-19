from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    app_name: str = "crypto-streaming-platform-api"
    app_version: str = "2.0.0"
    symbols: list[str] = None
    storage_path: str = "data/app.db"

    @classmethod
    def from_env(cls) -> "Settings":
        symbols_env = os.getenv("SYMBOLS", "BTCUSDT,ETHUSDT")
        symbols = [s.strip().upper() for s in symbols_env.split(",") if s.strip()]
        return cls(
            symbols=symbols,
            storage_path=os.getenv("STORAGE_PATH", "data/app.db"),
        )


settings = Settings.from_env()
