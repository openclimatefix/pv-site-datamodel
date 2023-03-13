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

```yml
pvsite-datamodel:
  sdk: # Folder containing language specific ORM packages specific to this datamodel
    python:
      pvsite_datamodel: # Python ORM code for reading/writing data from this model
        - sqlmodels.py # Ground truth source for database definition
```


## Editing the datamodel

Make changes to the datamodel via modifications to the `sqlmodels.py` file.


## Pre-Commit

This repository implements a [pre-commit](https://pre-commit.com/#install) config that enables automatic fixes to code when you create a commit. This helps to maintin consistency in the main repo. To enable this, follow the [installation instructions on the precommit website](https://pre-commit.com/#install).
