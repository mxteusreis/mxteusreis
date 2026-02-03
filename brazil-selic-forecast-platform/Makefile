PYTHON=python
PYTHONPATH=.

.PHONY: ingest features train api test

ingest:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m src.ingestion.pull_sgs_series

features:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m src.features.build_features

train:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m src.modeling.train_baseline

api:
	PYTHONPATH=$(PYTHONPATH) uvicorn api.main:app --reload

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q
