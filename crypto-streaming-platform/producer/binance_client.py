"""Binance API client utilities for ticker snapshots."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone

import requests

BINANCE_TICKER_24H_URL = "https://api.binance.com/api/v3/ticker/24hr"
DEFAULT_TIMEOUT_SECONDS = 10
MAX_RETRIES = 3
BACKOFF_SECONDS = 1


def fetch_ticker_24h(symbols: list[str]) -> list[dict]:
    """Fetch 24h ticker data from Binance and return a normalized event list.

    Args:
        symbols: Trading pairs in Binance format, e.g. ["BTCUSDT", "ETHUSDT"].

    Returns:
        A list of normalized event dicts.
    """
    if not symbols:
        return []

    payload = {"symbols": json.dumps([symbol.upper() for symbol in symbols])}

    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(BINANCE_TICKER_24H_URL, params=payload, timeout=DEFAULT_TIMEOUT_SECONDS)
            response.raise_for_status()
            tickers = response.json()
            timestamp_utc = datetime.now(timezone.utc).isoformat()

            return [
                {
                    "timestamp_utc": timestamp_utc,
                    "symbol": ticker["symbol"],
                    "lastPrice": ticker["lastPrice"],
                    "priceChangePercent": ticker["priceChangePercent"],
                    "volume": ticker["volume"],
                    "source": "binance_api_v3_ticker_24hr",
                }
                for ticker in tickers
            ]
        except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                time.sleep(BACKOFF_SECONDS * attempt)

    raise RuntimeError(f"Failed to fetch ticker data after {MAX_RETRIES} attempts: {last_error}") from last_error
