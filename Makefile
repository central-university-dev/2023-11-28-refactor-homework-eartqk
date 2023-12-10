CODE_FOLDERS := refactor_tool
TEST_FOLDERS := tests

install:
	poetry install

update:
	poetry lock

test:
	poetry run pytest $(TEST_FOLDER)

coverage:
	poetry run pytest --cov=$(CODE_FOLDERS) $(TEST_FOLDERS)

format:
	black . -S

lint:
	poetry run black --check . -S
	poetry run flake8 --ignore=C0209 $(CODE_FOLDERS) $(TEST_FOLDERS)
	poetry run pylint $(CODE_FOLDERS) $(TEST_FOLDERS)