# interview-project

## Requirements
*In order to run the project there are a couple of prerequisites. These are listed and explained below.*
#### [Poetry](https://python-poetry.org/)
*installation guide: [here](https://python-poetry.org/docs/)*

Poetry is the dependency management tool which I chose to use for the project. In order to work with the project locally poetry must be installed.

#### [Docker](https://www.docker.com/)
*installation guide: [here](https://docs.docker.com/get-docker/)*

Docker is used to containerize the application in order to make it easily deployable/runnable anywhere. In order to build the project, and the databases it depends on, Docker must be installed.

#### Python
The service is built in Python, and depends on version 3.10^ as some modern language features have been used in the project.

## Running the project
Once the dependencies specified in the *Requirements* section of the `README.md` have been installed you can begin working on & deploying the application. In order to aid with this, a number of commands have been provided in the `Makefile`. An explanation of those commands can be found below.

- `make setup`: Installs the `poetry` dependencies for the project & set's up `pre-commit`.
- `make unit-test`: Installs project dependencies, creates & seed's a local db, and then run's unit tests locally.
- `make db-up`: Build's and run's a local instance of the database.
- `make db-down`: Removes any local running instances of the database.
- `make app-up`: Build's and run's a complete local version of the application (database & API).
- `make app-down`: Removes any locally running version of the application (database & API)


## Unit-tests

The unit tests are built using Pytest. In the instances where a database is needed, the unit tests run against a locally running version of a `Postgres` database. This database can be run by running `make db-up`, this creates the tables needed for the unit tests and runs a `Postgres` database in a docker container. Alternatively, you can run the command `make unit-test`, which will install all the requirements, create a database & run the unit tests.

### Why are the unit tests run against an actual database?
In some cases, depending on the database used, there are good mocking libraries available to mock your database connection/queries. An example would be the `moto` library for mocking `DynamoDB` tables. However, for a `Postgres` database, the available libraries are not mature enough, nor of sufficient quality to justify using them in the unit tests. This leaves us with two options, either patch the methods that perform data access or run a local database. As I wanted to be able to properly test our data access methods, I chose to run a local version of `Postgres`.

If we developed more unit tests and some of them could function without a database connection we could add the pytest marker `@pytest.mark.skipif`, and create a check to see if a local version of the database was running.

### Why do the unit-tests work through an API Test Client?
Upon inspection of the unit tests, it becomes clear that an endpoint is considered a `unit` in the context of this service. When a new service/API is created I've found this a convenient way to achieve broad code coverage without spending excessive time creating a unit test for each public function within the code base. My criteria for deciding if a function should have a unit test are;
1. Is this a complex function that is not sufficiently covered by the current API-tests?
1. Has there been a bug found in this function?
If the answer to either of these is yes, then I create a unit test to cover that function, and/or the bug relating to that function.


## Dev tooling used
### [pre-commit](https://pre-commit.com/)
pre-commit is used to ensure each commit to our repo has a small number of hooks run before the commit. This can often help reduce the number of small issues found at PR time.

### [Pytest](https://docs.pytest.org/en/7.2.x/contents.html)
Pytest was used for unit testing within the project. It was chosen for its modern and innovative features such as `fixtures` & parameterized unit tests which are heavily leveraged within the code base.

### [Black](https://github.com/psf/black)
Black is an opinionated auto-formatting tool. It's used within the project the ensure all code is formatted in the same manner without the developer having to think about it.

### [flake8](https://flake8.pycqa.org/en/latest/)
Flake8 is a popular python code linting tool. It's used within the project to aid with formatting and to catch common code smells.

## Database Architecture & Technologies.

### Repository & data-model
This service was designed with two primary software development patterns in mind. The [Repository Pattern](https://deviq.com/design-patterns/repository-pattern) & the Data Model Pattern. The two `repositories` in the code base (`ServiceProviderRepository`, `ServiceProviderReviewRepository`) aim to abstract away data access into a simple to use & consistent interface.

The data models within the code base aim to provide a consistent view of the properties and attributes available on that model/resource. As an ORM was used in the project [[SQLAlchemy](https://www.sqlalchemy.org/)], the models from this ORM form the data models for the service.

### Postgres
[Postgres](https://www.postgresql.org/) is used as the primary persistence store for this service. The reasons for this are outlined below:
- Has wide support across the industry, particularly when it comes to managed hosting such as `AWS RDP Postgres`.
- Support's modern types such as `DateRange` which meshes quite well with the problem statement of the service.
- Support's complex search which would be ideal if we wanted to expand upon tasks #3 and #4.
- Widely used in the industry so it's easy to find developers with good work knowledge of it.

### SQL Alchemy
[SQLAlchemy](https://www.sqlalchemy.org/) is used as an ORM in the service. The motivations are outlined below:
- Using an ORM abstract’s away the SQL, as it generates it for you based on the models you've created. This is ideal in most cases as developers can often accidentally write poorly performing SQL.
- It abstracts away the underlying database system, making it simpler to switch between databases should the need arise.
- It tightly couples your data model and your database model, reducing the likelihood of you inserting bad data into your database.
- It trivialises working with a database model that has been normalized into 3NF, by allowing you to create `one-to-many` relationships on the models.

### Third Normal Form (3NF)
The database has been designed to be in the third normal form. This form is usually considered strong enough for database design, especially for a new service where the data access patterns are not 100% clear. The main motivation for doing this, in this case, is the removal of data redundancy where redundant data is having the same data in multiple places. By removing the data redundancy, it becomes easy to change the data as it is only present in one place. There are many other marginal advantages of 3NF, but they're not the primary motivation for the normalisation in this service.

One of the downsides of normalising the data is it makes it harder to select/join together all the attributes of an entity. Our ORM is able to help with this by allowing us to describe how our tables relate to each other through the use of [relationships](https://docs.sqlalchemy.org/en/14/orm/relationships.html). This then gives it all the information it needs to perform these joins for us.

## Pagination
For the aggregation endpoints in the service (`/v1_0/service-providers`, `/v1_0/service-providers/recommend`) it is possible to paginate the results set as a large number of results can theoretically be returned. In both cases, a consistent pagination interface is enabled through the use of query parameters on the endpoints. A user can use the query params `page` & `page_size` to paginate the result set.

## Versioning
The API is versioned using [fastapi-versioning](https://github.com/DeanWay/fastapi-versioning). The motivation around this was to make it trivial to produce a new version of an endpoint. All we'd need to do is duplicate the old version of the endpoint, alter the code in the endpoint handler and increment the `@version(1, 0)` decorator. The increment would depend on the change. The specific library was chosen as it works seamlessly with FastAPI.

## Logging & Structlog
[Structlog](https://www.structlog.org/en/stable/) was chosen as the logging package of choice for the service as it's a stable, mature logging library & standard that can grow with the service. It's also possible for us to build middleware into the FastAPI application that will add thing's like `user-id` into the logging context so we can see the user who performed the action associated with each log event.

## Deviations from the Spec & Motivations for doing so.
*At certain points in the code base, I have deviated from the specification outlined in the document for the take-home technical test. Below, I'll highlight the changes and justify them.*

### Alteration of the response format.
The spec document gives a view-centric example of what a service provider might look like. This is `#view 1` in the JSON snippet below. While there would be nothing wrong with creating an endpoint with a specific view in mind, or anything wrong with this exact payload, I considered it a better option to create a response format that could be easily consumed by other APIs or a front-end. This way, the display format of the data is the consumer's responsibility instead of the APIs.

`#view 2` Show's the response format I settled on for the `ServiceProviderSchema`, which forms the basis of most of the responses over the API. The major changes are:
1. `Cost` has become `cost_in_pence` and is now an integer value. Formatting this value has become the responsibility of the front end.
2. `Reviews Rating` has become `review_rating`, which is now a floating point number.
3. `Availability` has not really changed. Its format has just been clarified.


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
When designing the API I did not want to make `review_rating` an attribute of a service provider that could be edited. I decided to create a separate entity `Rating` which can be created over the API. The `review_rating` for a given service provider is the average of all of the `review_rating`'s for that service provider, if there are no ratings, their rating is 0.

### Users
I chose to add the notion of a user into the API. This is exposed through the header `user_id`, which is a `UUID` that several of the endpoints require. The motivation for adding this was that for some of the endpoints *_specifically, the post, put & delete ones_*, we want to make sure that the user taking the action, is the same user that owns the resource they're trying to modify. This feature was also useful for adding reviews, as we want to know which user's left a review.

## Task 3
Task 3 is exposed through the endpoint `POST: /v1_0/service-providers/recommend`. This endpoint returns a paginatable list of service providers ordered from most appropriate to least appropriate. There are multiple service providers returned when multiple of them match the conditions provided over the API. The endpoint is implemented as a POST instead of a GET due to the complex filtering requirements and them being complex to handle as query parameters.

Here is an example of the query params available to help with the following explanation:
```python
@dataclass
class ServiceProviderRecomendationParams:
    page: int = Query(default=1, ge=1)
    page_size: int = Query(default=10, ge=1)
    expected_job_duration_in_days: int = Query(default=1, ge=1)
    job_budget_in_pence: int = Query(ge=1)
    skills: list[str] = Query()
    availability: list[date] = Query()
    minimum_review_rating: Optional[float] = Query(default=0, le=5, ge=0)
```

The most appropriate service provider is determined using the following process:
1. Identify the user's `max_cost_per_day`: `job_budget_in_pence / expected_job_duration_in_days`
2. Filter the service providers with:
    1. `service_provider.cost_per_day <= max_cost_per_day`.
    2. At least one of the service providers' skills matches the skills requested by the user.
    3. The service provider is available over the date range the user requested.
    4. If the user specified it, the service provider's rating must be >= `minimum_review_rating`
    5. Order the remaining list of service providers by `cost` DESC & `review_rating` DESC.

### Potential improvements to Task 3 - Given more time.
1. We could also rank `service_providers` by how many of their skills matched what the user requests. We could also rule `service_providers` out if they didn't have every skill a user requested, although the user might then miss out on relevant searches.
2. We could also rank `service_providers` by how many reviews they had instead of just the average value of all of their reviews, as a `review_rating` of `5.0` with `1` review is arguably not as good as a `4.5` with `20,000` reviews.
3. Add additional validation to the endpoint to make sure that the `expected_job_duration_in_days` parameter is consistent with the `availability` parameter. I.e if the user provides the date range `date(2022, 1, 1) -> date(2022, 1, 2)` but sets `expected_job_duration_in_days` to `50`, then that is invalid.

## Task 4 - How else would you enhance the system?

### Improvements to Reviews
As part of `#Task 3`, I changed the way reviews work. There are further modifications that could be made to reviews to improve them.
1. As there is more complexity surrounding reviews when compared to the other sub-resources of a service provider, it might be good to de-couple the resource from the service provider by creating a new micro-service. This would have several advantages such as:
    1. Decreasing the complexity of the `service-provider-api`, making it easier to maintain.
    1. Increasing the resilience of the services overall, as if the `reviews-service` breaks, the `service-provider-api` can still continue to function (although some features will temporarily break, such as displaying reviews.)
1. Reviews could support adding comments, the change itself would be trivial, but you'd likely want to implement some sort of content moderation to ensure the reviews on the comments are appropriate.
1. User's should not be able to review their own content. This would be trivial in the current code base as we could simply do a check that `service_provider.user_id != review_user.user_id`.
1. Reviews could be added on a per-skill basis. This would allow us to give more accurate recommendations to our users.
1. Store an eventually consistent estimate of a `service_providers` average skill. This would make queires for fetching service providers faster.


### Async
Out of the box, `FastAPI` has good support for sync & async code and endpoint handlers. Even when the endpoint handlers are defined synchronously `def endpoind_handler(...)`, FastAPI can simultaneously serve multiple requests by using a thread pool. Handlers should only be defined as async when the code inside them is non-blocking. `SQLAlchemy` supports non-blocking async database connections (the document's can be found [here](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)) so it's possible to make our API asynchronous. The primary advantage of this would be allowing the service to have better utilisation of resources as it can do other work (serve other requests more efficiently) while it is waiting for I/O-bound tasks such as reading from the database. This would make our API feel more responsive and would allow us to serve more users as requests would execute faster.

### Alembic
[Alembic](https://alembic.sqlalchemy.org/en/latest/) is a data migration tool that helps to capture every schema change as a migration script and ensures that the database accurately reflects the data models. These data migration scripts can be automatically generated. Adding `Alembic` to the service would reduce the amount of work the developer needs to do in order to maintain a traditional RDBMS and reduce the likelihood of errors. The tool is easy to get started with and would be an easy win.

### Scaling
Depending on how the service grows over time, there are some additional steps we could take to help it scale.

### Scaling the database
 Databases such as Postgres are capable of growing to massive scales. However, they're typically hard to scale which becomes more of a problem when you consider the shift-left-infrastructure movement where developers are taking on more and more dev-ops work. Given this, if the service needed to be massively scaled we might want to consider something like AWS DynamoDB. Dynamo has been built to be easy to scale and generally doesn't leave any room for design patterns that don't scale well. It's also incredibly easy to manage. These points would make it a good option for moving to a more easily scalable database.

 One of the downsides of DynamoDB is you can typically only make full use of it when you're confident about what your service's data-access patterns will look like, as you need to design the table according to them. Another downside is that it doesn't support the complex searching/filtering that we've been able to do in Postgres. In order to meet that need for the service, we'd likely also need to include `AWS CloudSearch` on top of our `AWS DynamoDB Table`.

### Scaling the API.
While the API is scalable out of the box, through the use of something like `AWS ECS`, we could potentially make it even more scalable by migrating to a `lambda-per-endpoint` model with the use of `AWS Lambda` & `AWS API Gateway`. This would essentially allow the API to scale infinitely to the demand on the service at any given time and could make the service more resilient to bugs that affect multiple endpoints. It comes with an increased development overhead, but this can be mitigated by using appropriate tooling.

### Logging & Service Monitoring
One potential point of improvement would be to add [Sentry](https://sentry.io/) into the application. This would notify us when unhandled exceptions have been raised in the service, allow us to view all the details surrounding these exceptions and then triage the issue in order to solve it.

It would also be useful to create several dashboards with key health information about the service using a tool such as [Grafana](https://grafana.com/)

In order to get better information from our logging, we could also bind a `trace-id` to our logging context. This would allow us to trace a request, and get all of the relevant logs for a given request in a single query. In my experience, this has dramatically reduced the amount of time it's taken me to solve bugs in the past.

### Infrastructure As Code & CI/CD
By adding some infrastructure as code tooling such as `Terraform`, `Serverless` or `CloudFormation` we could dramatically reduce the time & complexity of managing our infrastructure.

By adding a robust CI/CD Pipeline we would reduce the management overhead of deploying new versions of the service to our servers/cloud provider. Ideally, the CI/CD pipeline would also act as a secondary quality control gate (After PR/MR), that could ensure all unit tests pass, all code is linted and any other additional quality steps we wanted to take.
