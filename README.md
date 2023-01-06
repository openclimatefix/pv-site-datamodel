<h1 align="center">pv-datamodel</h1>
<p align="center">
    <a href="https://dbdocs.io/ocf/pvdata" alt="Interactive pvdatamodel documentation">
        <img src="https://img.shields.io/badge/docs-dbdocs.io-blue" /></a>
    <a href="https://github.com/openclimatefix/pv-datamodel/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc" alt="Issues">
        <img src="https://img.shields.io/github/issues/openclimatefix/pv-datamodel"/></a>
    <a href="https://github.com/openclimatefix/pv-datamodel/actions/workflows/generate-ddl.yml" alt="Code generation pipeline">
        <img src="https://img.shields.io/github/actions/workflow/status/openclimatefix/pv-datamodel/generate-ddl.yml?label=codegen"></a>
    <a href="https://github.com/openclimatefix/pv-datamodel/actions/workflows/publish-docs.yml" alt="Documentation publishing pipeline">
        <img src="https://img.shields.io/github/actions/workflow/status/openclimatefix/pv-datamodel/publish-docs.yml?label=publish"></a>
    <a href="https://github.com/badges/shields/graphs/contributors" alt="Contributors">
        <img src="https://img.shields.io/github/contributors/openclimatefix/pv-datamodel" /></a>
</p>

Database schema specification for PV Site data.


## Repository structure

```yml
pv-datamodel:
  - datamodel.dbml # Ground-truth database specification
  gen: # Folder containing auto-generated code
    - pvdatamodel.sql # SQL soecification of the datamodel
    - pvdatamodel.py # SQLAlchemy specification of the datamodel
```


## Generating SQL and SQLAlchemy

In repo, code generation is carried out by the gen-sqlalchemy github workflow.
To generate SQL and SQLAlchemy locally from the `.dbml` file, carry out the
following steps:

Install the [dbml cli tool](https://www.dbml.org/cli/#installation)

```bash
$ npm install -g @dbml/cli

# or if you're using yarn
$ yarn global add @dbml/cli
```

Use the tool to convert `.dbml` schema to SQL

```bash
$ dbml2sql datamodel.dbml -o pvdatamodel.sql
```

This will have created all the CREATE TABLE statements required to build a
local version of the db.

For SQLAlchemy, install the python package O!MyModels

```bash
$ pip install omymodels
```

Use the package to convert the SQL to SQLAlchemy

```bash
$ omm pvdatamodel.sql -t pvdatamodel.py
```

Further reading:
    - https://xnuinside.medium.com/code-generation-how-to-generate-pydantic-sqlalchemy-ginoorm-models-from-sql-ddl-2c111b08b7a7


## Editing the datamodel

For syntax highlighting and hints in VSCode, use the 
[https://marketplace.visualstudio.com/items?itemName=matt-meyers.vscode-dbml](vscode-dbml) plugin.
If you'd rather a live view of the tables as you edit, https://dbdiagram.io/d gives a realtime
visualision of the datamodel.