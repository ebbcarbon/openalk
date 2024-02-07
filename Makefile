.ONESHELL:

.PHONY: install
install:
	PROJECT_ROOT=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
	cd $$PROJECT_ROOT
	echo "Installing with repo location $$PROJECT_ROOT"
	sed "s+<REPO_LOCATION>+$$PROJECT_ROOT+g" install/ta.desktop > $$HOME/Desktop/ta.desktop
	sed "s+<REPO_LOCATION>+$$PROJECT_ROOT+g" install/ta.desktop > $$HOME/.local/share/applications/ta.desktop
	chmod a+x $$HOME/Desktop/ta.desktop
	python3 -m venv venv
	. venv/bin/activate
	pip3 install --upgrade pip && pip3 install -r requirements.txt

.PHONY: uninstall
uninstall:
	rm $$HOME/Desktop/ta.desktop
	rm $$HOME/.local/share/applications/ta.desktop
	rm -r venv

.PHONY: test
test:
	. venv/bin/activate
	python -m pytest --cov

.PHONY: lint
lint:
	. venv/bin/activate
	black .
	flake8 .
