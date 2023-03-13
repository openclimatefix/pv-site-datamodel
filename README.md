<h1 align="center">pvsite-datamodel</h1>
<p align="center">
    <a href="https://pypi.org/project/pvsite-datamodel/0.1.18/" alt="PyPi package">
        <img src="https://img.shields.io/pypi/v/pvsite-datamodel"></a>
    <a href="https://github.com/openclimatefix/pv-datamodel/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc" alt="Issues">
        <img src="https://img.shields.io/github/issues/openclimatefix/pv-datamodel"/></a>
    <a href="https://github.com/openclimatefix/pv-datamodel/graphs/contributors" alt="Contributors">
        <img src="https://img.shields.io/github/contributors/openclimatefix/pv-datamodel" /></a>
</p>

Database schema specification for PV Site data.


## Repository structure

```yaml
pvsite_datamodel:
  read: # Sub package containing modules for reading from the database
  write: # Sub package containing modules for writing to the database
  - connection.py # Class for connecting to the database
  - sqlmodels.py # SQLAlchemy definitions of table schemas
tests: # External tests package
```

### Top-level functions

Classes specifying table schemas:
- SiteSQL
- GenerationSQL
- ForecastSQL
- ForecastValueSQL
- ClientSQL
- StatusSQL

Database connection objects:
- DatabaseConnection


### Read package functions

Currently available functions accessible via `from pvsite_datamodel.read import <func>`:

- get_pv_generation_by_client
- get_pv_generation_by_sites
- get_site_by_uuid
- get_site_by_client_site_id
- get_site_by_client_site_name
- get_all_sites
- get_latest_status
- get_latest_forecast_values_by_site


### Write package functions

Currently available write functions accessible via `from pvsite_datamodels.write import <func>`:
- insert_generation_values


## Install the dependencies (requires [poetry][poetry])

    poetry install


## Coding style

Format the code **in place**.

    make format

Lint the code

    make lint


## Running the tests

    make test


## Database migrations using alembic

[./alembic](./alembic)



[poetry]: https://python-poetry.org/
