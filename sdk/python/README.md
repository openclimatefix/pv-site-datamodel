# pvsite_datamodel

Python library to interact with PV Site postgres database

## Install the dependencies (requires [poetry][poetry])

    poetry install


## Structure

```yaml
pvsite_datamodel:
  read: # Sub package containing modules for reading from the database
  write: # Sub package containing modules for writing to the database
  - connection.py # Class for connecting to the database
  - schema.py # Pandera pandas dataframe validation schemas
  - sqlmodels.py # SQLAlchemy definitions of table schemas
tests: # External tests package
```


## Top-level functions

Classes specifying table schemas:
- SiteSQL
- GenerationSQL
- ForecastSQL
- ForecastValueSQL
- ClientSQL
- StatusSQL

Database connection objects:
- DatabaseConnection


## Read package functions

Currently available functions accessible via `from pvsite_datamodel.read import <func>`:

- get_pv_generation_by_client
- get_pv_generation_by_sites
- get_site_by_uuid
- get_site_by_client_site_id
- get_site_by_client_site_name
- get_all_sites
- get_latest_status


## Write package functions

Currently available write functions accessible via `from pvsite_datamodels.write import <func>`:
- insert_generation_values


## Formatting

Format the library **in place**.

    make format


## Linting

    make lint


## Tests

    poetry run pytest tests

[poetry]: https://python-poetry.org/
