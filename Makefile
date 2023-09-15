test:
	python -m pytest

lint:
	black .
	flake8 .

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt