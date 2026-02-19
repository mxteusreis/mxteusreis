from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app


class FakeRepo:
    def last_ingest_time(self) -> str:
        return "2026-01-01T00:00:00+00:00"

    def query_latest(self, symbol: str, limit: int) -> list[dict]:
        return [
            {
                "timestamp_utc": "2026-01-01T00:00:00+00:00",
                "symbol": symbol,
                "lastPrice": 100.0,
                "priceChangePercent": 1.0,
                "volume": 200.0,
                "source": "test",
            }
        ][:limit]

    def query_range(self, symbol, start, end):
        return self.query_latest(symbol, 1)

    def bi_daily_ohlc(self, symbol: str, days: int) -> list[dict]:
        return [{"date": "2026-01-01", "open": 1, "high": 2, "low": 0.5, "close": 1.5}]

    def bi_daily_volume(self, symbol: str, days: int) -> list[dict]:
        return [{"date": "2026-01-01", "volume": 999.0}]


client = TestClient(app)
app.state.repo = FakeRepo()


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["last_ingest_time"] == "2026-01-01T00:00:00+00:00"


def test_trades_latest_endpoint() -> None:
    response = client.get("/trades/latest", params={"symbol": "BTCUSDT", "limit": 1})
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["symbol"] == "BTCUSDT"


def test_bi_daily_ohlc_csv_header() -> None:
    response = client.get("/bi/daily_ohlc.csv", params={"symbol": "BTCUSDT", "days": 90})
    assert response.status_code == 200
    lines = response.text.strip().splitlines()
    assert lines[0] == "date,open,high,low,close"
