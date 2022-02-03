.PHONY: tests
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

# Print the comment for each make command
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

install-hooks: ## Install pre-commit hooks
	pre-commit install

run-hooks: ## Run pre-commit hooks on staged files
	pre-commit run

run-hooks-all: ## Run pre-commit hooks on all files
	pre-commit run --all-files

clean-build: ## Remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

install: ## Install the package
	pip install .

install-dev: ## Install development version and pre-commit hooks
	pip install -e .[dev]
	$(MAKE) install-hooks

release: ## Package and upload
	python setup.py sdist
	twine upload dist/*

tests: ## Run unit tests
	pytest .
