# pvsite_datamodel

Python library to interact with PV Site postgres database


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
- LatestForecastValueSQL
- ClientSQL
- DatetimeIntervalSQL
- StatusSQL

Database connection objects:
- DatabaseConnection


## Read package functions

Currently available functions accessible via `from pvsite_datamodel.read import <func>`:

- get_pv_generation_by_client
- get_pv_generation_by_sites
- get_latest_forecast_values_by_site
- get_site_by_uuid
- get_site_by_client_site_id
- get_site_by_client_site_name
- get_all_sites
- get_latest_status


## Write package functions

Currently available write functions accessible via `from pvsite_datamodels.write import <func>`:
- insert_forecast_values
- insert_generation_values


 ## Tests

To run tests use `pytest`
