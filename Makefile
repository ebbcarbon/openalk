.ONESHELL:

.PHONY: install
install:
	PROJECT_ROOT=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
	cd $$PROJECT_ROOT
	echo "Installing with repo location $$PROJECT_ROOT"
	sed "s+<REPO_LOCATION>+$$PROJECT_ROOT+g" install/openalk.desktop > $$HOME/Desktop/openalk.desktop
	sed "s+<REPO_LOCATION>+$$PROJECT_ROOT+g" install/openalk.desktop > $$HOME/.local/share/applications/openalk.desktop
	chmod a+x $$HOME/Desktop/openalk.desktop
	python3 -m venv venv
	. venv/bin/activate
	pip3 install --upgrade pip && pip3 install -r requirements.txt

.PHONY: uninstall
uninstall:
	rm $$HOME/Desktop/openalk.desktop
	rm $$HOME/.local/share/applications/openalk.desktop
	rm -r venv

.PHONY: test
test:
	. venv/bin/activate
	python -m pytest --cov --cov-report term-missing

.PHONY: lint
lint:
	. venv/bin/activate
	black .
	flake8 .
