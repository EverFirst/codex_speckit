VENV?=.venv
PYTHON?=python

.PHONY: install fmt lint test run

install:
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -e .[dev]

fmt:
	$(PYTHON) -m isort app tests
	$(PYTHON) -m black app tests

lint:
	$(PYTHON) -m black --check app tests
	$(PYTHON) -m isort --check app tests

test:
	$(PYTHON) -m pytest

run:
	$(PYTHON) -m uvicorn app.main:app --reload
