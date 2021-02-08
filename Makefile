
tests:
	python -m unittest discover -s tests

fulltests:
	@echo "Running full integration tests"
	python -m unittest discover complete-check -s tests

check:
	@echo "Checking flake8"
	flake8 pyhpo
	@echo "Checking mypy standard"
	mypy pyhpo
	@echo "Checking mypy more stict"
	mypy --disallow-untyped-calls --disallow-untyped-defs --disallow-incomplete-defs --warn-redundant-casts --warn-unused-ignores --warn-unreachable pyhpo

docs:
	@echo "Generating documentation"
	sphinx-build -b html -d _build/doctrees docs _build/html/

build:
	@echo "Building packages"
	python setup.py sdist bdist_wheel

.PHONY: tests fulltests check html build