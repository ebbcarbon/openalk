start:
	python3 Test.py

test:
	pytest

lint:
	black .
	flake8 .