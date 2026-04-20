.PHONY: install install-dev lint test format clean audit-site probe-endpoints build-grid run-pipeline demo

PYTHON ?= python
PIP    ?= pip

# ── Installation ──────────────────────────────────────────────────────────────

install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"
	pre-commit install

# ── Code quality ──────────────────────────────────────────────────────────────

lint:
	ruff check src tests
	ruff format --check src tests
	mypy src

format:
	ruff format src tests
	ruff check --fix src tests

# ── Tests ─────────────────────────────────────────────────────────────────────

test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ --cov=src/gdynia_thermal_audit --cov-report=html --cov-report=term-missing

# ── Pipeline targets ──────────────────────────────────────────────────────────

audit-site:
	gta audit-site

probe-endpoints:
	gta probe-endpoints

build-grid:
	gta build-grid --size 250

run-pipeline:
	gta run-pipeline

demo:
	gta run-pipeline --config config/config.example.yaml --demo

# ── Housekeeping ──────────────────────────────────────────────────────────────

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.py[cod]" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ .pytest_cache/ .mypy_cache/ .ruff_cache/ htmlcov/
	@echo "Clean complete."
