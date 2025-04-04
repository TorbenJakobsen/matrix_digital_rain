.ONESHELL:

.DEFAULT_GOAL := setup

PYTHON=./venv/bin/python3
PYTEST=./venv/bin/pytest
FLAKE8=./venv/bin/flake8
MYPY=./venv/bin/mypy
COVERAGE=./venv/bin/coverage
RSTCHECK=./venv/bin/rstcheck

venv/bin/activate:
	python3.11 -m venv venv
	. ./venv/bin/activate
	$(PYTHON) -m pip install --upgrade pip setuptools
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -r requirements_test.txt
	$(PYTHON) -m pip install -r requirements_dev.txt


venv: venv/bin/activate
	. ./venv/bin/activate


.PHONY: setup
setup: clean venv

.PHONY: clean
clean:
	# Clean __pycache__ dirs - abuses list comprehension by using "side effect" of `rmtree`
	python3 -Bc "import pathlib; import shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"
	rm -rf venv

.PHONY: test
test: venv
	$(PYTEST)

.PHONY: coverage
coverage: venv
	$(COVERAGE) run -m pytest tests
	$(COVERAGE) report -m

.PHONY: coverage_html
coverage_html: venv
	$(COVERAGE) run -m pytest tests
	$(COVERAGE) html
# macOS
	open htmlcov/index.html


.PHONY: lint
lint: venv
	$(FLAKE8) *.py


.PHONY: mypy
mypy: venv
	$(MYPY) *.py


.PHONY: code
code: venv
	code .


.PHONY: all
all: setup


.PHONY: rstcheck
rstcheck: venv
	$(RSTCHECK) *.rst docs/source/*.rst


.PHONY: format
format: venv
	$(PYTHON) -m black *.py


.PHONY: run
run: venv
	$(PYTHON) matrix_rain.py -c blue -H red
