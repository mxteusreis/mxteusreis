# Datasets públicos (BI)

Esta pasta contém os datasets públicos e estáveis para consumo por ferramentas de BI
como Google Looker Studio, Google Sheets e Excel.

## Contrato de dados

Os arquivos abaixo são sempre sobrescritos a cada refresh e mantêm schema fixo.

### selic_history_latest.csv
```
date,selic_rate
```

### selic_forecast_latest.csv
```
date,selic_rate_forecast,horizon_days,model_version
```

### metadata.json
Campos:
- generated_at
- data_source
- model_type
- model_version
- max_forecast_horizon
