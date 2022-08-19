.PHONY: clean
clean: clean-build clean-pyc clean-test

.PHONY: clobber
clobber: clean-build clean-pyc clean-test clean-output

.PHONY: clean-build
clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

.PHONY: clean-output
clean-output: ## remove output files
	rm -f output.jsonl
	rm -f zaiko.pdf

.PHONY: scrape
scrape:
	python scrape.py

.PHONY: http
http:
	uvicorn app:app --reload
