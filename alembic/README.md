# Migrations

We use [alembic][alembic] to manage the database schema migrations.


## Updating the database to the latest migration

```bash
DB_URL=<your_db_url> poetry run alembic upgrade head
```


## Creating a new migration

When we change the data models of the database we will need to run a database migration.

### 1. Run a database locally with the *old* schema

First you need to have a database in the state *before* the migration you want to apply.

Usually this can be done by [starting a local database](#db_docker) and running all the migrations
so far. This should look like running `git checkout main` followed by the steps in the previous
section (`alembic upgrade head`).


### 2. Change the database models

Edit the [sqlmodels.py](../pvsite_datamodel/sqlmodels.py) file to reflect the changes you
want to bring to the schema.


### 3. Generate the migration code

In most cases, you can have alembic generate a migration automatically:

```bash
DB_URL=<your_db_url> poetry run alembic revision --autogenerate -m "Some comment explaining the change"
```

Make sure that the generated code makes sense. Adjust if needed.


### 4. Run migrations scripts

Run your latest migration:

```bash
DB_URL=<your_db_url> poetry run alembic upgrade head`
```

Make sure everything looks good in the database.


### 5. Commit the migration

Commit the migrations to the repo, make a pull request and tag someone for review.


### 6. Start AWS task on ECS with docker container from this repo
This will run all the migrations an update the database in production / development
TODO Set up task definition using terraform
The current solution is to oopen ssh tunnel and run the migrations from there



<a name="db_docker"></a>
## How to start a local database using docker

```bash
    docker run \
        -it --rm \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -p 54545:5432 postgres:14-alpine \
        postgres
```

The corresponding `DB_URL` will be

`postgresql://postgres:postgres@localhost:54545/postgres`


[alembic]: https://alembic.sqlalchemy.org/en/latest
