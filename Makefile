PYTHON := uv run
SRC := funpaybotengine
TESTS := tests

.PHONY: format lint type test all ci clean install dev

install:
	uv sync
	@echo Production environment ready!

dev:
	uv sync --all-extras
	$(PYTHON) pre-commit install
	@echo Development environment ready!

format:
	$(PYTHON) ruff format $(SRC)
	@echo Code formatting complete!

lint:
	$(PYTHON) ruff check --fix $(SRC)
	@echo Code linting complete!

type:
	$(PYTHON) mypy $(SRC)
	@echo Type checking complete!

test:
	$(PYTHON) pytest $(TESTS)
	@echo Tests complete!

all: format lint type test

ci:
	$(PYTHON) ruff check $(SRC)
	$(PYTHON) ruff format --check $(SRC)
	$(PYTHON) mypy $(SRC)
	$(PYTHON) pytest $(TESTS)
	@echo CI checks complete!

clean:
	rm -rf __pycache__ */__pycache__
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf build dist
	rm -rf *.egg-info
	@echo Clean complete!
