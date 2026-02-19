# crypto-streaming-platform

A reproducible crypto data platform with streaming ingestion, queryable storage, and public API endpoints for analytics and BI.

## What problem does this solve?
Most free crypto sources provide current snapshots but not a stable, queryable history suitable for analytics and BI. This project captures Binance market events continuously and exposes that history through API endpoints and stable CSV contracts consumable by Looker Studio.

## Architecture (v1)

```text
Binance API -> Producer -> Kafka (crypto_prices) -> Consumer -> data/raw JSONL
```

## Architecture (v2)

```text
v1 pipeline + queryable SQLite storage + FastAPI public API + /bi/*.csv endpoints
```

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for Mermaid diagrams.

## Project structure

```text
crypto-streaming-platform/
├── api/
├── bi/
├── consumer/
├── data/
├── docker/
├── producer/
├── scripts/
├── tests/
├── ARCHITECTURE.md
├── COSTS.md
├── SECURITY.md
└── README.md
```

## Quickstart (v1 local Kafka)

1. `cp .env.example .env`
2. `make up`
3. Terminal 1: `make consumer`
4. Terminal 2: `make producer`
5. Verify raw files in `data/raw/`

## Quickstart (v2 online/direct mode)

1. `cp .env.example .env`
2. Set `BROKER_MODE=direct` and keep `STORAGE_PATH=data/app.db`
3. Start producer: `make producer`
4. Start API: `make api`
5. Open `http://localhost:8000/health`

You can also run containerized direct mode:

- `make online-up`
- API at `http://localhost:8000`

## API endpoints

- `GET /health`
- `GET /symbols`
- `GET /trades/latest?symbol=BTCUSDT&limit=200`
- `GET /trades/range?symbol=BTCUSDT&start=2026-01-01T00:00:00Z&end=2026-01-07T00:00:00Z`

### Stable BI endpoints

- `GET /bi/daily_ohlc.csv?symbol=BTCUSDT&days=90`
- `GET /bi/daily_volume.csv?symbol=BTCUSDT&days=90`
- `GET /bi/latest_prices.csv?symbols=BTCUSDT,ETHUSDT`

All BI endpoints return CSV with fixed headers and cache-control headers.

## Data contract (event)

```json
{
  "timestamp_utc": "2026-01-15T14:03:22.913852+00:00",
  "symbol": "BTCUSDT",
  "lastPrice": "68001.20",
  "priceChangePercent": "1.87",
  "volume": "24567.123",
  "source": "binance_api_v3_ticker_24hr"
}
```

## Environment variables

- `STORAGE_PATH` (e.g., `data/app.db`)
- `SYMBOLS`
- `POLL_INTERVAL_SECONDS`
- `BROKER_MODE` (`kafka` | `direct`)
- `ENABLE_DB_SINK`
- `KAFKA_BOOTSTRAP_SERVERS`
- `TOPIC_NAME`

## Live Demo (v2)

- API base URL: `https://<your-public-url>`
- Health: `https://<your-public-url>/health`
- BI sample: `https://<your-public-url>/bi/daily_ohlc.csv?symbol=BTCUSDT&days=90`

## Deploy (free tier)

A Render blueprint is included in [`render.yaml`](render.yaml). You can also deploy with Docker using `docker/Dockerfile.api`.

## Commands

- `make up` / `make down`
- `make producer`
- `make consumer`
- `make api`
- `make online-up` / `make online-down`
- `make backfill`
- `make bi-build`
- `make verify-bi`
- `make lint`
- `make test`

## Roadmap (v2+)

- Bronze/Silver/Gold modeling
- Volatility metrics and market features
- Hardened rate limiting and API auth options
- Stable `/bi/*` datasets for broader BI use
- Public deployment hardening
- Future Kubernetes orchestration
