# ==============================================================================
# Makefile for AI-Powered Security Monitoring Platform
# ==============================================================================

.PHONY: help up down logs build migrate superuser shell test train evaluate edge-sim

help:
	@echo "AI-Powered Security Monitoring Platform Command Shortcuts:"
	@echo "  up           - Start the local docker development stack"
	@echo "  down         - Shut down all running containers"
	@echo "  logs         - Tail backend logs"
	@echo "  build        - Rebuild docker containers from source"
	@echo "  migrate      - Apply database migrations"
	@echo "  superuser    - Create an admin django superuser"
	@echo "  shell        - Open django interactive shell"
	@echo "  test         - Run django backend test suite"
	@echo "  train        - Run ML training pipelines"
	@echo "  evaluate     - Run model benchmark evaluator"
	@echo "  edge-sim     - Run simulated edge MQTT publisher node"

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f backend

build:
	docker compose build

migrate:
	docker compose exec backend python manage.py migrate

superuser:
	docker compose exec backend python manage.py createsuperuser

shell:
	docker compose exec backend python manage.py shell

test:
	docker compose exec backend pytest

train:
	cd ml-training && python train_isolation_forest.py && python train_xgboost.py && python train_lstm.py

evaluate:
	cd ml-training && python evaluate.py

edge-sim:
	cd edge && python mqtt_publisher.py
