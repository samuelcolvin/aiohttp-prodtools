.PHONY: install
install:
	pip install -U setuptools pip
	pip install -U .
	pip install -r tests/requirements.txt

.PHONY: isort
isort:
	isort -rc -w 120 aiohttp_prodtools
	isort -rc -w 120 tests

.PHONY: lint
lint:
	python setup.py check -rms
	flake8 aiohttp_prodtools/ tests/
	pytest aiohttp_prodtools -p no:sugar -q --cache-clear

.PHONY: test
test:
	pytest --cov=aiohttp_prodtools && coverage combine

.PHONY: testcov
testcov:
	pytest --cov=aiohttp_prodtools && (echo "building coverage html"; coverage combine; coverage html)

.PHONY: all
all: testcov lint

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	python setup.py clean
