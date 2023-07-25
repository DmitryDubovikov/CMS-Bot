.PHONY: install
install:
	poetry install

.PHONY: installprecommit
installprecommit:
	poetry run pre-commit uninstall; poetry run pre-commit install

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: run
run:
	poetry run python echobot.py
