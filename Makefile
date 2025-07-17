#
# This mostly contains shortcut for multi-command steps.
#

.PHONY: lint
lint:
	uv run ruff check --fix src

.PHONY: test
test:
	uv run pytest tests
