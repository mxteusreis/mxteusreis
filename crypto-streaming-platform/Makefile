PYTHON ?= python3

.PHONY: up down producer consumer test

up:
	docker compose -f docker/docker-compose.yml up -d

down:
	docker compose -f docker/docker-compose.yml down

producer:
	$(PYTHON) producer/producer.py

consumer:
	$(PYTHON) consumer/consumer.py

test:
	$(PYTHON) -m pytest -q
