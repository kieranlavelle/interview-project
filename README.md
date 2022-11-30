# interview-project

## Requirements
*In order to run the project there are a couple of pre-requisits. These are listed and explained below.*
#### [Poetry](http://google.com)
*installation guide: [here](http://google.com)*

Poetry is the dependency management tool which I chose to use for the project. In order to work with the project locally poetry must be installed.

#### [Docker](http://google.com)
*installation guide: [here](http:google.com)*

Docker is used to containerse the application in order to make it easily deployable/runnable anywhere. In order to build the project, and the databases it depends on, Docker must be installed.

## Running the project
Once the dependencies specified in the *Requirements* section of the `README.md` have been installed you can begin working on & deploying the application. In order to aid with this, a number of commands have been provided in the `Makefile`. An explanation of those commands can be found below.

- `make setup`: Installs the `poetry` dependencies for the project.
- `make unit-test`: Installs project dependencies, creates & seed's a local db, and then run's unit tests locally.
- `make db-up`: Build's and run's a local instance of the database.
- `make db-down`: Removes any local running instances of the database.
- `make app-up`: Build's and run's a complete local version of the application (database & API).
- `make app-down`: Removes any locally running version of the application (database & API)

## Unit-tests

The unit / API tests are built using pytest. In the instances where a database is needed, the unit test's run against a locally running version of a `Postgres` database. This database can be ran by running `make db-up`, this creates the tables needed for the unit-tests and runs a `Postgres` database in a docker container. Alternatively, you can run the command `make unit-test`, which will install all the requirements, create a database & run the unit tests.

### Why are the unit test's ran against an actual database?
In some cases, depending on the database used, there are good mocking libraries available to mock your database connection / queries. An example would be the `moto` library for mocking `DynamoDB` tables. However, for a `Postgres` database the available libraries are not mature engough, nor of sufficent quality to justify using them in the unit-tests. This leaves us with two options, either patch the methods that perform data access or run a local database. As I wanted to be able to properly test are data access methods, I chose to run a local verson of `Postgres`.

## Database Archtecture & Technologies.
- repository & data model
- why postgres
- why sqlalchemy
- 3NF
- Why not DynamoDB
## Deviations from the Spec & Motivations for doing so.
- response format.
- service provider ratings

## Improvements
- async
- Turned into a lambda API / application so we could sclae endpoints.