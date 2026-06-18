SHELL := /bin/bash


.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


.PHONY: install
install: ## Make venv and install requirements
	@uv sync
	@uv run --env-file=.env  pre-commit install
	@pre-commit autoupdate

.PHONY: run
run: ## Run the Django server
	@uv run --env-file=.env  python manage.py runserver

start: install run ## Install requirements, apply migrations, then start development server

.PHONY: test
test: ## Run the test suite
	@uv run --env-file=.env pytest

precommit: ## Run pre-commit hooks
	@git add . & uv run --env-file=.env pre-commit run --all-files

.PHONY: changelog ## update CHANGELOG.md and amend it on the commit
changelog:
	@uv run git-cliff --config pyproject.toml --output CHANGELOG.md
	@git add CHANGELOG.md
	@git commit --amend --no-edit

.PHONY: docs-build
docs-build: ## Build the documentation site
	@uv run zensical build --clean --config-file zensical.toml

.PHONY: docs-serve
docs-serve: ## Serve the documentation locally at localhost:8001
	@uv run zensical serve --config-file zensical.toml --dev-addr localhost:8001
