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

- `make setup`: Installs the `poetry` dependencies for the project & set's up `pre-commit`.
- `make unit-test`: Installs project dependencies, creates & seed's a local db, and then run's unit tests locally.
- `make db-up`: Build's and run's a local instance of the database.
- `make db-down`: Removes any local running instances of the database.
- `make app-up`: Build's and run's a complete local version of the application (database & API).
- `make app-down`: Removes any locally running version of the application (database & API)

## Unit-tests

The unit / API tests are built using pytest. In the instances where a database is needed, the unit test's run against a locally running version of a `Postgres` database. This database can be ran by running `make db-up`, this creates the tables needed for the unit-tests and runs a `Postgres` database in a docker container. Alternatively, you can run the command `make unit-test`, which will install all the requirements, create a database & run the unit tests.

### Why are the unit test's ran against an actual database?
In some cases, depending on the database used, there are good mocking libraries available to mock your database connection / queries. An example would be the `moto` library for mocking `DynamoDB` tables. However, for a `Postgres` database the available libraries are not mature engough, nor of sufficent quality to justify using them in the unit-tests. This leaves us with two options, either patch the methods that perform data access or run a local database. As I wanted to be able to properly test are data access methods, I chose to run a local verson of `Postgres`.

### Why do the unit-tests work through an API Test Client?
Upon inspection of the unit test's it becomes clear that an endpoint is considered a `unit` in the context of this service. When a new service/api is created I've found this a convenient way to achive broad code coverage without spending excessive time creating a unit test for each public function within the code base. My criteria for deciding if a function should have a unit test is;
1. Is this a complex function that is not sufficient covered by the current api-tests?
1. Has there been a bug found in this function?
If the answer to either of this is yes, then I create a unit test to cover that function, and/or the bug relating to that function.

## Dev tooling used
### [pre-commit](https://pre-commit.com/)
pre-commit is used to ensure each commit to our repo has a small number of hook's ran before the commit. This can often help reduce the number of small issues found at PR time.
### [Pytest](https://docs.pytest.org/en/7.2.x/contents.html)
Pytest was used for unit testing within the project. It was chosen for it's modern and innovative features such as `fixtures` & peramiterized unit tests which are heavily leveraged within the code base.

### [Black](https://github.com/psf/black)
Black is an opinionated auto-formatting tool. It's used within the project the ensure all code is formatted in the same manner without the developer having to think about it.

### [flake8](https://flake8.pycqa.org/en/latest/)
Flake8 is a popular python code linting tool. It's used within the project to aid with formatting and to catch common code smells.
## Database Archtecture & Technologies.

### Repository & data-model
This service was designed with two primary software development patterns in mind. The [Repository Pattern](https://deviq.com/design-patterns/repository-pattern) & the Data Model Pattern. The two `repositories` in the code base (`ServiceProviderRepository`, `ServiceProviderReviewRepository`) aim to abstract away data access into a simple to use & consistent interface.

The data models within the code base aim to provide a consistent view of the properties and attributes available on that model / resource. As an ORM was used in the project [[SQLAlchemy](https://www.sqlalchemy.org/)], the models from this ORM form the data-models for the service.

### Postgres
[Postgres](https://www.postgresql.org/) is used as the primary persistence store for this service. The reasons for this are outlined below:
- Has wide support across the industry, perticularly for managed hosting such as `AWS RDP Postgres`.
- Support's modern typs such as `DateRange` which meshes quite well with the problem statement of the service.
- Support's complex search which would be ideal if we wanted to expand upon tasks #3 and #4.
- Widely used in the industry so it's easy to find developers with good work knowledge of it.

### SQL Alchemy
[SQLAlchemy](https://www.sqlalchemy.org/) is used as an ORM in the service. The motivations are outlined below:
- Using an ORM abstracts away the SQL as it generates it for you based on the models you've created. This is ideal in most cases as developers can often accidentally write poorly performing SQL.
- It abstracts away the underlying database system, making it simpler to switch between database's should the need arise.
- It tightly couples your data-model and your database model, reducing the liklihood of you inserting bad data into your database.
- It trivialises working with a database model that has been normalized into 3NF, by allowing you to create `one-to-many` relationships on the models.

### Third Normal Form (3NF)
The database has been designed to be in the third normal form. This form is usually considered strong enough for data base design, especially for a new service where the data access patterns are not 100% clear. The main motivation for doing this in this case is the removal of data redundancy where redundant data is having the same data in multiple places. By removing the data redundancy, it becomes easy to change the data as it is only present in one place. There are many other marginal advantages of 3NF, but they're not the primary motivation for normalisation in this service.

One of the downsides of normalising the data is it makes it harder to select / join together all the attributes of an entity. Our ORM is able to help with this by allowing us to describe how our tables relate to eachother through the use of [relationships](https://docs.sqlalchemy.org/en/14/orm/relationships.html). This then gives it all the infomation it need's to perform these joins for us.

### Pagination
For the aggregation endpoints in the service (`/v1_0/service-providers`, `/v1_0/service-providers/recommend`) it is possible to paginate the results set as a large amount of results can theoretically be returned. In both cases a consistent pagination interface is enabled though the user of query peramiters on the endpoints. A user can use the query params `page` & `page_size` to paginate the result set.

### Versioning
The API is versioned using [fastapi-versioning](https://github.com/DeanWay/fastapi-versioning). The motivation around this was to make it trivial to produce a new version of an endpoint. All we'd need to do is duplicate the old version of the endpoint, alter the code in the endpoint handler and increment the `@version(1, 0)` decorator. The increment would depend on the change. The specific library was chosen as it works seemlessly with FastAPI.

### Logging & Structlog
[Structlog](https://www.structlog.org/en/stable/) was chosen as the logging package of choice for the service as it's a stable, mature logging library & standard that can grow with the service. It's also possible for us to build middleware into the FastAPI application that will add thing's like `user-id` into the logging context so we can see the user who perfomed the action associated with each log event.

## Deviations from the Spec & Motivations for doing so.
*At certain points in the code base I have deviated from the specification outlined in the document for the take home technical test. Below, I'll highlight the changes and justify them.*
### Alteration of the response format.
The spec document gives a view centric example of what a service provider might look like. This is `#view 1` in the json snippet below. While there would be nothing wrong with creating an endpoint with a specific view in mind, or anything wrong with this exact payload, I considered it a better option to create a response format that could be easily consumed by other API's or a front-end. This way, the display format of the data is the consumers responsibility instead of the APIs.

`#view 2` Show's the response format I settled on for the `ServiceProviderSchema`, which forms the basis of most of the responses over the API. The major changes are:
1. `Cost` has became `cost_in_pence` and is now an integer value. Formatting this value has became the responsibility of the front end.
2. `Reviews Rating` has became `review_rating`, which is now a floating point number.
3. `Availability` has not really changed. It's format has just been clarified.


`#view 1`
```json
{
    "Name": "SEO Incorporated",
    "Skills": ["SEO Optimisation", "Digital Marketing", "Cold Calling"],
    "Cost": "£250/day",
    "Availability": ["date range 1", "date range 2", "date range3"],
    "Reviews Rating": "3.5/5.0"
}
```

`#view 2`
```json
{
    "name": "SEO Incorporated",
    "skills": ["SEO Optimisation", "Digital Marketing", "Cold Calling"],
    "cost_in_pence": 25000,
    "availability": [
        {
            "from_date": "2022-11-12",
            "to_date": "2022-12-28"
        },
        ...
    ],
    "review_rating": 3.5
}
```

### Service Provider Ratings
When designing the API I did not want to make `review_rating` an attribute of a service provider that could be edited. I decided to create a seperate entity `Rating` which can be created over the API. The `review_rating` for a given service provider is the average of all of the `review_rating`'s for that service provider, if there are no ratings, their rathing is 0.

### Users
- added the notion of users, so we can control who can do write/delete operations

## Task 3 - ...

## Task 4 - How else would you enhance the system.
- async
- Turned into a lambda API / application so we could sclae endpoints.
- DynamoDB depending on the scale needed
- Split reviews out into a seperate micro-service
- Add end-to-end trace-ids???
- Add elebic to support db-migrations
- Store review-count so it doesnt have to be calculated
- Add comments to the review object
- filter the skills that can be added / add a skills search to populate a dropdown
- sentry
- review ratings could be per skill and have a date added field
