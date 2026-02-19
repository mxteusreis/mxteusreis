# BI endpoints and contracts

Stable endpoints exposed by the API for Looker Studio:

- `/bi/daily_ohlc.csv?symbol=BTCUSDT&days=90`
  - Header: `date,open,high,low,close`
- `/bi/daily_volume.csv?symbol=BTCUSDT&days=90`
  - Header: `date,volume`
- `/bi/latest_prices.csv?symbols=BTCUSDT,ETHUSDT`
  - Header: `symbol,timestamp_utc,lastPrice,priceChangePercent,volume`

## Looker Studio connection

Use **File > New Data Source > URL** and point to one of the public CSV URLs from the deployed API.

Examples:

- `https://<your-app-url>/bi/daily_ohlc.csv?symbol=BTCUSDT&days=90`
- `https://<your-app-url>/bi/daily_volume.csv?symbol=ETHUSDT&days=90`
- `https://<your-app-url>/bi/latest_prices.csv?symbols=BTCUSDT,ETHUSDT`
