<h1 align="center">pvsite-datamodel</h1>

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-12-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

<p align="center">
    <a href="https://github.com/openclimatefix/ocf-meta-repo?tab=readme-ov-file#overview-of-ocfs-nowcasting-repositories" alt="Ease of Contribution">
        <img src="https://img.shields.io/badge/ease%20of%20contribution:%20easy-32bd50"></a>
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
- APIRequestSQL
- GenerationSQL
- ForecastSQL
- ForecastValueSQL
- MLModelSQL
- UserSQL
- SiteSQL
- SiteGroupSQL
- StatusSQL
- ClientSQL

Database connection objects:
- DatabaseConnection


### Read package functions

Currently available functions accessible via `from pvsite_datamodel.read import <func>`:

- get_user_by_email
- get_pv_generation_by_sites
- get_site_by_uuid
- get_site_by_client_site_id
- get_site_by_client_site_name
- get_sites_by_client_name 
- get_all_sites
- get_sites_by_country
- get_site_group_by_name
- get_latest_status
- get_latest_forecast_values_by_site
- get_client_by_name


### Write package functions

Currently available write functions accessible via `from pvsite_datamodels.write import <func>`:
- insert_forecast_values
- insert_generation_values
- create_site
- create_site_group
- create_user
- add_site_to_site_group
- change_user_site_group
- update_user_site_group
- edit_site
- delete_site
- delete_user
- delete_site_group
- make_fake_site
- create_client
- edit_client
- assign_site_to_client


## Install the dependencies (requires [poetry][poetry])

    poetry install


## Coding style

Format the code **in place**.

    make format

Lint the code

    make lint


## Running the tests

    make test

## PVSite Database Schema

```mermaid
---
title: SQLAlchemy relationships
---
classDiagram

    class UserSQL{
        + user_uuid : UUID ≪ PK ≫
        + email : String(255) ≪ U ≫
        + site_group_uuid : UUID ≪ FK ≫
    }
        class SiteGroupSQL{
        + site_group_uuid : UUID ≪ PK ≫
        + site_group_name : String(255) ≪ U ≫
        + service_level : Integer ≪ U ≫
    }

    class SiteGroupSiteSQL{
        + site_group_site_uuid : UUID ≪ PK ≫
        + site_group_uuid : UUID ≪ FK ≫
        + site_uuid : UUID ≪ FK ≫
    }

    class SiteSQL{
        + site_uuid : UUID ≪ PK ≫
        + client_site_id : Integer
        + client_site_name : String(255)
        + country : String(255) ≪ D ≫
        + region : String(255)
        + dno : String(255)
        + gsp : String(255)
        + asset_type : Enum ≪ D ≫
        + orientation : Float
        + tilt : Float
        + latitude : Float
        + longitude : Float
        + capacity_kw : Float
        + inverter_capacity_kw : Float
        + module_capacity_kw : Float
        + ml_id : Integer ≪ U ≫
        + client_uuid : UUID ≪ FK ≫
    }

    class ClientSQL{
        + client_uuid : UUID ≪ PK ≫
        + client_name : String(255)
    }

    class GenerationSQL{
        + generation_uuid : UUID ≪ PK ≫
        + site_uuid : UUID ≪ FK ≫
        + generation_power_kw : Float
        + start_utc : DateTime
        + end_utc : DateTime
    }

    class ForecastSQL{
        + forecast_uuid : UUID ≪ PK ≫
        + site_uuid : UUID ≪ FK ≫
        + timestamp_utc : DateTime
        + forecast_version : String(32)
    }

    class ForecastValueSQL{
        + forecast_value_uuid : UUID ≪ PK ≫
        + start_utc : DateTime
        + end_utc : DateTime
        + forecast_power_kw : Float
        + horizon_minutes : Integer
        + forecast_uuid : UUID ≪ FK ≫
    }

    class StatusSQL{
        + status_uuid : UUID ≪ PK ≫
        + status : String(255)
        + message : String(255)
    }

    class InverterSQL{
        + inverter_uuid : UUID ≪ PK ≫
        + site_uuid : UUID ≪ FK ≫
    }

    class APIRequestSQL{
        + uuid : UUID ≪ PK ≫
        + url : String
        + user_uuid : UUID ≪ FK ≫
    }
    
    class MLModelSQL{
        + uuid : UUID ≪ PK ≫
        + mode_name : String
        + model_version : UUID ≪ FK ≫
    }

    UserSQL "1" -- "N" SiteGroupSQL : belongs_to
    SiteGroupSQL "N" -- "N" SiteSQL : contains
    SiteGroupSQL "1" -- "N" SiteGroupSiteSQL : contains
    SiteSQL "1" -- "N" GenerationSQL : generates
    SiteSQL "1" -- "N" ForecastSQL : forecasts
    ForecastSQL "1" -- "N" ForecastValueSQL : contains
    MLModelSQL "1" -- "N" ForecastValueSQL : forecasts
    SiteSQL "1" -- "N" InverterSQL : contains
    UserSQL "1" -- "N" APIRequestSQL : performs_request
    ClientSQL "1" -- "N" SiteSQL : owns
    class Legend{
    UUID: Universally Unique Identifier
    PK: Primary Key
    FK: Foreign Key
    U: Unique Constraint
    D: Default Value
    }

```

## Multiple Clients

We have the ability to have these different scenarios
1. one user - can add or view one site
2. one user, can add or view multiple sites
3. Two users (for example from the sample company), want to look at one site
4. Two users, wanting to look at multiple sites (could be added by another user). Any user from site group can add a site. 
5. OCF user want to see everything (admin)

### Solution
```mermaid
  graph TD;
      User-- N:1 -->SiteGroup;
      SiteGroup-- N:N -->Site;
```
- One `user` is in one `sitegroup`. Each site group can have multiple users. 
- Each `sitegroup` contains multiple `sites`. One `site` can be in multiple `sitegroups`


### 1. one user - one site

```mermaid
  graph TD;
      A(User=Alice)-->B(SiteGroup=Alice1);
      B --> C(Site);
```

### 2. one user - two sites

```mermaid
  graph TD;
      A(User=Alice)-->B(SiteGroup=Alice1);
      B --> C1(Site1);
B --> C2(Site2);
```

### 3. Two users - one site

```mermaid
  graph TD;
      A1(User=Alice)-->B(SiteGroup);
A2(User=Bob)-->B(SiteGroup);
      B --> C1(Site1);
```

### 4. Two users - two site

```mermaid
  graph TD;
      A1(User=Alice)-->B(SiteGroup);
A2(User=Bob)-->B(SiteGroup);
      B --> C1(Site1);
B --> C2(Site2);
```

### 5. OCF can see everything

```mermaid
  graph TD;
      A1(User=Alice)-->B(SiteGroup1);
A2(User=Bob)-->B(SiteGroup1);
A3(User=OCF)-->B2(SiteGroup2);
      B --> C1(Site1);
B --> C2(Site2);
      B2 --> C1(Site1);
B2 --> C2(Site2);
B2 --> C3(Site3);
```





## Database migrations using alembic

[./alembic](./alembic)



[poetry]: https://python-poetry.org/

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/abhijelly"><img src="https://avatars.githubusercontent.com/u/75399048?v=4?s=100" width="100px;" alt="Abhijeet"/><br /><sub><b>Abhijeet</b></sub></a><br /><a href="https://github.com/openclimatefix/pv-site-datamodel/commits?author=abhijelly" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/devsjc"><img src="https://avatars.githubusercontent.com/u/47188100?v=4?s=100" width="100px;" alt="devsjc"/><br /><sub><b>devsjc</b></sub></a><br /><a href="https://github.com/openclimatefix/pv-site-datamodel/commits?author=devsjc" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/peterdudfield"><img src="https://avatars.githubusercontent.com/u/34686298?v=4?s=100" width="100px;" alt="Peter Dudfield"/><br /><sub><b>Peter Dudfield</b></sub></a><br /><a href="https://github.com/openclimatefix/pv-site-datamodel/commits?author=peterdudfield" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://confusedmatrix.com"><img src="https://avatars.githubusercontent.com/u/617309?v=4?s=100" width="100px;" alt="Chris Briggs"/><br /><sub><b>Chris Briggs</b></sub></a><br /><a href="https://github.com/openclimatefix/pv-site-datamodel/commits?author=confusedmatrix" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://racheltipton.dev"><img src="https://avatars.githubusercontent.com/u/86949265?v=4?s=100" width="100px;" alt="rachel tipton"/><br /><sub><b>rachel tipton</b></sub></a><br /><a href="https://github.com/openclimatefix/pv-site-datamodel/commits?author=rachel-labri-tipton" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ericcccsliu"><img src="https://avatars.githubusercontent.com/u/62641231?v=4?s=100" width="100px;" alt="Eric Liu"/><br /><sub><b>Eric Liu</b></sub></a><br /><a href="https://github.com/openclimatefix/pv-site-datamodel/commits?author=ericcccsliu" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/braddf"><img src="https://avatars.githubusercontent.com/u/41056982?v=4?s=100" width="100px;" alt="braddf"/><br /><sub><b>braddf</b></sub></a><br /><a href="https://github.com/openclimatefix/pv-site-datamodel/commits?author=braddf" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/bikramb98"><img src="https://avatars.githubusercontent.com/u/24806286?v=4?s=100" width="100px;" alt="Bikram Baruah"/><br /><sub><b>Bikram Baruah</b></sub></a><br /><a href="https://github.com/openclimatefix/pv-site-datamodel/commits?author=bikramb98" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://andrewlester.net"><img src="https://avatars.githubusercontent.com/u/23221268?v=4?s=100" width="100px;" alt="Andrew Lester"/><br /><sub><b>Andrew Lester</b></sub></a><br /><a href="https://github.com/openclimatefix/pv-site-datamodel/commits?author=AndrewLester" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/suleman1412"><img src="https://avatars.githubusercontent.com/u/37236131?v=4?s=100" width="100px;" alt="Suleman Karigar"/><br /><sub><b>Suleman Karigar</b></sub></a><br /><a href="https://github.com/openclimatefix/pv-site-datamodel/commits?author=suleman1412" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/vishalj0501"><img src="https://avatars.githubusercontent.com/u/92500255?v=4?s=100" width="100px;" alt="Vishal J"/><br /><sub><b>Vishal J</b></sub></a><br /><a href="https://github.com/openclimatefix/pv-site-datamodel/commits?author=vishalj0501" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ProfessionalCaddie"><img src="https://avatars.githubusercontent.com/u/180212671?v=4?s=100" width="100px;" alt="Nicholas Tucker"/><br /><sub><b>Nicholas Tucker</b></sub></a><br /><a href="https://github.com/openclimatefix/pv-site-datamodel/commits?author=ProfessionalCaddie" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
