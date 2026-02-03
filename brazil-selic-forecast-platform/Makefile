PYTHON=python
PYTHONPATH=.

.PHONY: ingest features train api ui up down test

ingest:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m src.ingestion.pull_sgs_series

features:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m src.features.build_features

train:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m src.modeling.train_baseline

api:
	PYTHONPATH=$(PYTHONPATH) uvicorn api.main:app --reload

ui:
	PYTHONPATH=$(PYTHONPATH) streamlit run ui/app.py

up:
	docker compose -f docker/docker-compose.yml up --build

down:
	docker compose -f docker/docker-compose.yml down

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q
