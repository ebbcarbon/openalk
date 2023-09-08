test:
	pytest

lint:
	black .
	flake8 .

install:
	pip3 install -r requirements.txt

install-dev:
	pip3 install -r requirements-dev.txt