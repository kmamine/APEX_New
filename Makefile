.DEFAULT_GOAL := help
.PHONY: help install install-gpu sync lint format type test test-gpu api web gen-types vllm worker demo clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install:  ## Install core + dev deps (no GPU stacks) via uv
	uv sync --extra dev

install-gpu:  ## Install everything incl. local GPU inference stacks
	uv sync --extra dev --extra local-gpu --extra api --extra queue

lint:  ## Lint with ruff
	uv run ruff check src tests

format:  ## Auto-format with ruff
	uv run ruff format src tests
	uv run ruff check --fix src tests

type:  ## Type-check with mypy
	uv run mypy

test:  ## Run the GPU-free test suite
	uv run pytest -m "not gpu and not network"

test-gpu:  ## Run the full suite incl. GPU/network tests (needs hardware + endpoints)
	uv run pytest

api:  ## Run the FastAPI server (reads .env)
	uv run uvicorn apex.api.app:app --reload --host $${APEX_HOST:-127.0.0.1} --port $${APEX_PORT:-8000}

web:  ## Run the React dev server
	cd web && npm run dev

gen-types:  ## Regenerate web TS types from the live OpenAPI schema
	cd web && npm run gen-types

vllm:  ## Helper to (re)launch the gemma MLLM via vLLM (see scripts/run_vllm.sh)
	bash scripts/run_vllm.sh

worker:  ## Run the arq queue worker (full-stack/docker deployment)
	uv run arq apex.api.runner.WorkerSettings

demo:  ## Run an end-to-end demo on the fake backend (no GPU)
	APEX_BACKEND_MODE=fake uv run apex run --image $${IMG:-tests/fixtures/sample_face.png} --preset "LinkedIn Professional"

clean:  ## Remove caches and build artifacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov coverage.xml dist build
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
