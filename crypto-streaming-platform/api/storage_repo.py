from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path


class StorageRepo:
    def __init__(self, db_path: str) -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                timestamp_utc TEXT,
                symbol TEXT,
                last_price REAL,
                price_change_percent REAL,
                volume REAL,
                source TEXT,
                ingested_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp_utc)
            )
            """
        )
        self.conn.commit()

    def upsert_events(self, events: list[dict]) -> None:
        if not events:
            return
        rows = [
            (
                event["timestamp_utc"],
                event["symbol"],
                float(event["lastPrice"]),
                float(event["priceChangePercent"]),
                float(event["volume"]),
                event["source"],
            )
            for event in events
        ]
        self.conn.executemany(
            """
            INSERT OR IGNORE INTO events
            (timestamp_utc, symbol, last_price, price_change_percent, volume, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        self.conn.commit()

    def query_latest(self, symbol: str, limit: int) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT timestamp_utc, symbol, last_price, price_change_percent, volume, source
            FROM events
            WHERE symbol = ?
            ORDER BY timestamp_utc DESC
            LIMIT ?
            """,
            (symbol.upper(), limit),
        ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def query_range(self, symbol: str, start: datetime, end: datetime) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT timestamp_utc, symbol, last_price, price_change_percent, volume, source
            FROM events
            WHERE symbol = ?
              AND timestamp_utc BETWEEN ? AND ?
            ORDER BY timestamp_utc ASC
            """,
            (symbol.upper(), start.isoformat(), end.isoformat()),
        ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def bi_daily_ohlc(self, symbol: str, days: int) -> list[dict]:
        rows = self.conn.execute(
            """
            WITH base AS (
                SELECT date(timestamp_utc) AS day, timestamp_utc, last_price
                FROM events
                WHERE symbol = ?
                  AND date(timestamp_utc) >= date('now', '-' || (? - 1) || ' day')
            )
            SELECT
                b.day AS day,
                (SELECT last_price FROM base WHERE day = b.day ORDER BY timestamp_utc ASC LIMIT 1) AS open,
                MAX(b.last_price) AS high,
                MIN(b.last_price) AS low,
                (SELECT last_price FROM base WHERE day = b.day ORDER BY timestamp_utc DESC LIMIT 1) AS close
            FROM base b
            GROUP BY b.day
            ORDER BY b.day ASC
            """,
            (symbol.upper(), days),
        ).fetchall()
        return [
            {"date": row["day"], "open": row["open"], "high": row["high"], "low": row["low"], "close": row["close"]}
            for row in rows
        ]

    def bi_daily_volume(self, symbol: str, days: int) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT date(timestamp_utc) AS day, AVG(volume) AS volume
            FROM events
            WHERE symbol = ?
              AND date(timestamp_utc) >= date('now', '-' || (? - 1) || ' day')
            GROUP BY day
            ORDER BY day ASC
            """,
            (symbol.upper(), days),
        ).fetchall()
        return [{"date": row["day"], "volume": row["volume"]} for row in rows]

    def last_ingest_time(self) -> str | None:
        row = self.conn.execute("SELECT max(timestamp_utc) AS max_ts FROM events").fetchone()
        return row["max_ts"] if row and row["max_ts"] else None

    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> dict:
        return {
            "timestamp_utc": row["timestamp_utc"],
            "symbol": row["symbol"],
            "lastPrice": row["last_price"],
            "priceChangePercent": row["price_change_percent"],
            "volume": row["volume"],
            "source": row["source"],
        }
