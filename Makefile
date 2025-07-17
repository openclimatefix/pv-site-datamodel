#
# This mostly contains shortcut for multi-command steps.
#
SRC = pvsite_datamodel tests

.PHONY: lint
lint:
	uv run ruff $(SRC)


.PHONY: format
format:
	uv run ruff check --fix $(SRC)
	uv run black $(SRC)
	uv run isort $(SRC)

.PHONY: test
test:
	uv run pytest tests
