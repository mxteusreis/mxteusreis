# Costs and free-tier strategy

## Why v2 can stay free

- `BROKER_MODE=direct` allows online demos without maintaining Kafka in production.
- SQLite uses a single embedded file (`STORAGE_PATH`) and avoids managed database costs.
- API + producer can run on a free web/container tier (Render/Fly.io).

## Limits and risks

- Free tiers can sleep and cause delayed ingestion.
- Local disk is often ephemeral on free plans; persistent disk volume is recommended.
- Public endpoints can be abused without throttling.
