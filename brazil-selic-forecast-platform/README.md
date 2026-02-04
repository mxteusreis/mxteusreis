# Brazil Selic Forecast Platform

## Visão geral
A taxa Selic influencia custo de crédito, inflação e decisões de investimento. Antecipar movimentos da Selic ajuda empresas e investidores a planejar caixa, risco de carteira e políticas de preço. Este projeto cria um pipeline simples para ingestão de dados do Banco Central do Brasil, construção de dataset consolidado e treinamento de um modelo baseline, além de expor resultados via API.

## Fonte de dados
- **Banco Central do Brasil (SGS)**: série 11 (Selic). A coleta utiliza a API pública do SGS.

## Arquitetura
```
┌─────────────┐   ┌────────────┐   ┌──────────────┐   ┌─────────────┐
│ Ingestão    │→  │ Features   │→  │ Treinamento  │→  │ API FastAPI │
│ (SGS API)   │   │ (Gold)     │   │ (baseline)  │   │ (consulta)  │
└─────────────┘   └────────────┘   └──────────────┘   └─────────────┘
```

## Como rodar localmente

### 1) Preparar ambiente
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Ingestão de dados
```bash
make ingest
# opcionalmente:
python -m src.ingestion.pull_sgs_series --start-date 01/01/2010 --end-date 31/12/2024
```

### 3) Construção do dataset gold
```bash
make features
```

### 4) Treinar baseline e gerar previsões
```bash
make train
```

### 4.1) Exportar datasets estáveis (BI)
```bash
make export
```

### 5) Subir API
```bash
make api
```

A API expõe:
- `GET /health`
- `GET /series/selic`
- `GET /forecast/selic?horizon=30`
- `GET /bi/selic/history`
- `GET /bi/selic/forecast`
- `GET /bi/metadata`

## Web UI (Streamlit)

### Rodar localmente
1. Inicie a API em outro terminal:
```bash
make api
```
2. Suba a UI:
```bash
make ui
```

### Rodar com Docker Compose
```bash
make up
```

Para parar:
```bash
make down
```

URLs úteis:
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- UI: [http://localhost:8501](http://localhost:8501)

## Estrutura de pastas
```
brazil-selic-forecast-platform/
├── api/               # FastAPI
├── artifacts/         # Modelo, métricas e previsões
├── data/              # Raw, curated, gold
├── src/               # Pipeline (ingestão, features, modelagem)
├── tests/             # Testes automatizados
```

## Roadmap
- Integração com Power BI
- Orquestração e versionamento de modelos (MLflow)
- Monitoramento de drift e qualidade

Próximos passos:
- Deploy em cloud
- MLflow + monitoramento

## Google Looker Studio Integration

Os datasets em `datasets/` são públicos, estáveis e pensados para consumo via URL/CSV.
### URLs para Looker Studio
- `http://localhost:8000/bi/selic/history`
- `http://localhost:8000/bi/selic/forecast`

### Passo a passo (resumido)
1. No Looker Studio, crie uma fonte de dados do tipo **CSV via URL**.
2. Cole a URL do endpoint desejado.
3. Valide o schema e finalize a conexão.

### Schema documentado

**selic_history_latest.csv**
```
date,selic_rate
```

**selic_forecast_latest.csv**
```
date,selic_rate_forecast,horizon_days,model_version
```

### Boas práticas
- Use a camada `datasets/` como fonte da verdade.
- Evite regras de negócio no BI (transformações pesadas).
- As URLs `/bi/...` são estáveis e sem parâmetros, ideais para refresh automático.

## Public Deployment & Access

### Arquitetura de deploy
- **API (FastAPI)**: expõe `/docs`, `/series/selic`, `/forecast/selic` e endpoints `/bi/*`.
- **UI (Streamlit)**: consome a API pública via `API_BASE_URL`.

### URLs esperadas após deploy
- UI: `https://<app-url>`
- API docs: `https://<api-url>/docs`
- Datasets (CSV):
  - `https://<api-url>/bi/selic/history`
  - `https://<api-url>/bi/selic/forecast`
  - `https://<api-url>/bi/metadata`

### Passo a passo genérico (container)
1. **Build** da imagem:
   ```bash
   docker build -f docker/Dockerfile.api -t selic-api:latest .
   docker build -f docker/Dockerfile.ui -t selic-ui:latest .
   ```
2. **Push** para o registry da sua cloud (Render/Cloud Run/Azure).
3. **Variáveis de ambiente**:
   - API: `PORT=8000`
   - UI: `PORT=8501` e `API_BASE_URL=https://<api-url>`
4. **Deploy** dos serviços (API e UI).

> Looker Studio consome diretamente os CSVs via URL dos endpoints `/bi/*`.

### Boas práticas de produção (sem overengineering)
- Cache: considere CDN ou cache de app para reduzir carga em endpoints CSV.
- Limites de uso: implemente rate limit no futuro se o tráfego crescer.
- Atualização dos dados: execução manual hoje, agendamento futuro (cron/Cloud Scheduler).

## Notas
- Este repositório é a versão inicial (v1) com ingestão real do SGS, baseline de regressão com lags e API REST.
