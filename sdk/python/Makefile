#
# This mostly contains shortcut for multi-command steps.
#
SRC = pvsite_datamodel tests

.PHONY: lint
lint:
	poetry run ruff $(SRC)
	# Sadly `ruff` does not cover everything, we still need black
	poetry run black --check $(SRC)
	# As far as I can tell, `ruff` doesn't support isort's profile="black" setting.
	poetry run isort --check $(SRC)


.PHONY: format
format:
	poetry run ruff --fix $(SRC)
	poetry run black $(SRC)
	poetry run isort $(SRC)

.PHONY: test
test:
	poetry run pytest tests
