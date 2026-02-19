PYTHON ?= python3

.PHONY: up down producer consumer api online-up online-down backfill bi-build verify-bi test lint

up:
	docker compose -f docker/docker-compose.yml up -d

down:
	docker compose -f docker/docker-compose.yml down

online-up:
	docker compose -f docker/docker-compose.online.yml up -d --build

online-down:
	docker compose -f docker/docker-compose.online.yml down

producer:
	$(PYTHON) producer/producer.py

consumer:
	$(PYTHON) consumer/consumer.py

api:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

backfill:
	$(PYTHON) scripts/backfill_from_raw.py

bi-build:
	$(PYTHON) bi/build_bi_views.py

verify-bi:
	$(PYTHON) scripts/verify_bi_contract.py

lint:
	ruff check .

test:
	$(PYTHON) -m pytest -q
