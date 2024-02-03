.PHONY: install
install:
	GIT_TOPLEVEL=$(shell git rev-parse --show-toplevel); \
	echo "Installing with repo location $$GIT_TOPLEVEL"; \
	sed "s+<REPO_LOCATION>+$$GIT_TOPLEVEL+g" install/ta.desktop > $$HOME/Desktop/ta.desktop; \
	sed "s+<REPO_LOCATION>+$$GIT_TOPLEVEL+g" install/ta.desktop > $$HOME/.local/share/applications/ta.desktop; \
	chmod a+x $$HOME/Desktop/ta.desktop; \
	python3 -m venv venv; \
	. venv/bin/activate; \
	pip3 install --upgrade pip && pip3 install -r requirements.txt;

.PHONY: uninstall
uninstall:
	rm $$HOME/Desktop/ta.desktop
	rm $$HOME/.local/share/applications/ta.desktop
	rm -r venv

.PHONY: test
test:
	. venv/bin/activate; \
	python -m pytest --cov;

.PHONY: lint
lint:
	. venv/bin/activate; \
	black .; \
	flake8 .;

