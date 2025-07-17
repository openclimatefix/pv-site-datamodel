#
# This mostly contains shortcut for multi-command steps.
#

.PHONY: lint
lint:
	uv run ruff check --fix pvsite_datamodel

.PHONY: test
test:
	uv run ruff check --fix tests
	uv run pytest tests
