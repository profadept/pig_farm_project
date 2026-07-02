.PHONY: setup lint format format-check test help check

COMPOSE = podman compose
APP_CONTAINER = farm_app
DB_CONTAINER = farm_postgres

setup: ## Bootstrap a fresh clone: install deps and pre-commit hooks
	uv sync
	uv run pre-commit install

lint: ## Run ruff lint check
	uv run ruff check .

fix: ## Auto-fix lint issues (import sorting, safe fixes)
	uv run ruff check --fix .

format: ## Reformat code with ruff
	uv run ruff format .

format-check:  ## Verify code is formatted (no changes made)
	uv run ruff format --check

test: ## Run the test suite
	uv run pytest

check: lint format-check test ## Run all checks (lint, format-check, test)

up: ## Start project containers
	$(COMPOSE) up -d

rebuild: ## Rebuild and restart project containers
	$(COMPOSE) up --build -d

down: ## Stop and remove project containers
	$(COMPOSE) down

logs: ## Stream logs from all containers
	$(COMPOSE) logs -f

app-logs: ## Stream app container logs
	podman logs -f $(APP_CONTAINER)

db-logs: ## Stream db container logs
	podman logs -f $(DB_CONTAINER)

app-shell: ## Shell into the app container
	podman exec -it $(APP_CONTAINER) /bin/bash

db-shell: ## Open psql shell in db container
	podman exec -it $(DB_CONTAINER) psql -U farm_user -d pig_farm_db

migrate: ## Apply alembic migrations
	podman exec -it $(APP_CONTAINER) alembic upgrade head

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
