.PHONY: help install install-dev test lint format type-check clean build upload

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install the package with development dependencies
	pip install -e ".[dev]"
	pre-commit install

test:  ## Run tests
	pytest -v --cov=spout --cov-report=term-missing --cov-report=html

test-fast:  ## Run tests without coverage
	pytest -v

lint:  ## Run linting
	flake8 src tests examples
	black --check src tests examples
	isort --check-only src tests examples

format:  ## Format code
	black src tests examples
	isort src tests examples

type-check:  ## Run type checking
	mypy src

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

build:  ## Build the package
	python -m build

upload:  ## Upload to PyPI (requires build first)
	python -m twine upload dist/*

demo:  ## Run the demo script
	python main.py

example-fastapi:  ## Generate client from FastAPI example
	spout generate --input examples --output generated_fastapi_client.ts --client-type fetch --verbose

example-axios:  ## Generate axios client from examples
	spout generate --input examples --output generated_axios_client.ts --client-type axios --base-url https://api.example.com --verbose

detect:  ## Detect frameworks in examples
	spout detect --input examples

list-generators:  ## List available client generators
	spout list-generators

dev-check: format lint type-check test  ## Run all development checks