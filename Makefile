
tests:
	python -m unittest discover -s tests

fulltests:
	@echo "Running full integration tests"
	python -m unittest discover complete-check -s tests

check:
	@echo "Checking black linting"
	black --check .
	@echo "Checking ruff"
	ruff check .
	@echo "Checking mypy standard"
	mypy pyhpo
	@echo "Checking mypy more strict"
	mypy --disallow-untyped-calls --disallow-untyped-defs --disallow-incomplete-defs --warn-redundant-casts --warn-unreachable pyhpo

docs:
	@echo "Generating documentation"
	sphinx-build -a -b html -d _build/doctrees docs _build/html/

build:
	@echo "Building packages"
	python setup.py sdist bdist_wheel

coverage:
	@echo "Running unittest coverage analysis"
	python -m coverage run -m unittest discover tests
	python -m coverage html --include "pyhpo/*"

.PHONY: tests fulltests check docs build
