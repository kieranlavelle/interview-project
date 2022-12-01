from datetime import date
from uuid import uuid4, UUID

import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from service_provider_api.database import models
from service_provider_api.core.repositories.service_provider import (
    ServiceProviderRepository,
)
from service_provider_api.core.repositories.service_provider_review import (
    ServiceProviderReviewRepository,
)
from service_provider_api.database.database import Base, engine, SessionLocal
from service_provider_api.api import schemas
from service_provider_api.api.app import app


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the API.

    This is used to make requests to the API in the context of a test.

    Returns:
        TestClient: The test client.
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_database(db_connection: Session):
    """Clean the database after each test.

    This ensures that the database state is consistent
    for each test we run.

    Args:
        db_connection (Session): The database connection.

    Returns:
        None
    """

    db_connection.execute("TRUNCATE TABLE service_providers CASCADE")
    db_connection.commit()


@pytest.fixture
def db_connection() -> Session:
    """Create a database connection that we can use in tests.

    Yields:
        Session: The database connection.
    """

    # bind the models to the DB engine
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def user_id() -> str:
    """A convenience fixture to generate a user ID."""
    return uuid4()


@pytest.fixture
def service_provider() -> schemas.NewServiceProviderInSchema:
    """A convenience fixture to generate a service provider.

    This service provider schema can be used as an input
    to the API.

    Returns:
        NewServiceProviderInSchema: The service provider.
    """

    return schemas.NewServiceProviderInSchema(
        name="John Smith",
        skills=["plumbing", "electrical"],
        cost_in_pence=1000,
        availability=[
            schemas.ServiceProviderAvailabilitySchema(
                from_date=date(2021, 1, 1),
                to_date=date(2021, 1, 2),
            ),
            schemas.ServiceProviderAvailabilitySchema(
                from_date=date(2021, 1, 3),
                to_date=date(2021, 1, 4),
            ),
        ],
    )


@pytest.fixture
def multiple_service_providers() -> list[schemas.NewServiceProviderInSchema]:
    """A convenience fixture to generate a multiple service providers.

    This is generally used as an input into other fixtures to pre-seed
    the database with multiple service providers.

    Returns:
        list[NewServiceProviderInSchema]: The service providers.
    """

    return [
        schemas.NewServiceProviderInSchema(
            name="John Smith",
            skills=["plumbing", "electrical"],
            cost_in_pence=1000,
            availability=[
                schemas.ServiceProviderAvailabilitySchema(
                    from_date=date(2021, 1, 1),
                    to_date=date(2021, 1, 2),
                ),
                schemas.ServiceProviderAvailabilitySchema(
                    from_date=date(2021, 1, 3),
                    to_date=date(2021, 1, 4),
                ),
            ],
        ),
        schemas.NewServiceProviderInSchema(
            name="Dean Greene",
            skills=["IT Services", "SEO"],
            cost_in_pence=2000,
            availability=[
                schemas.ServiceProviderAvailabilitySchema(
                    from_date=date(2022, 1, 1),
                    to_date=date(2022, 1, 2),
                ),
                schemas.ServiceProviderAvailabilitySchema(
                    from_date=date(2022, 1, 3),
                    to_date=date(2022, 1, 4),
                ),
            ],
        ),
    ]


@pytest.fixture
def service_provider_review() -> schemas.NewServiceProviderReview:
    """A convenience fixture to generate a service provider review.

    This is either used as an input to the API or as an input
    to other fixtures to pre-seed the database.

    Returns:
        NewServiceProviderReview: The service provider review.
    """
    return schemas.NewServiceProviderReview(
        rating=5,
    )


#############################
# data seeding fixtures
#############################


@pytest.fixture
def create_service_provider_in_db(
    service_provider: schemas.NewServiceProviderInSchema,
    user_id: UUID,
    db_connection: Session,
) -> models.ServiceProvider:
    """Pre-seed the database with a service provider.

    Args:
        service_provider (NewServiceProviderInSchema): The service provider.
        user_id (UUID): The user ID of the user who created the service provider.
        db_connection (Session): The database connection.

    Returns:
        ServiceProvider: The service provider that was created.
    """

    providers = ServiceProviderRepository.new(service_provider, user_id, db_connection)
    db_connection.commit()
    return providers


@pytest.fixture
def create_multiple_service_providers_in_db(
    multiple_service_providers: list[schemas.NewServiceProviderInSchema],
    user_id: UUID,
    db_connection: Session,
) -> list[models.ServiceProvider]:
    """Pre-seed the database with multiple service providers.

    Args:
        multiple_service_providers (list[NewServiceProviderInSchema]): The service providers.
        user_id (UUID): The user ID of the user who created the service providers.
        db_connection (Session): The database connection.

    Returns:
        list[ServiceProvider]: The service providers that were created.
    """

    providers = [
        ServiceProviderRepository.new(provider, user_id, db_connection)
        for provider in multiple_service_providers
    ]
    db_connection.commit()
    return providers


@pytest.fixture
def create_multiple_service_provider_reviews_in_db(
    create_multiple_service_providers_in_db: list[models.ServiceProvider],
    user_id: UUID,
    db_connection: Session,
) -> list[models.Reviews]:
    """Pre-seed the database with multiple service provider's & reviews.

    Args:
        create_multiple_service_providers_in_db (list[ServiceProvider]): The service providers.
        user_id (UUID): The user ID of the user who created the service providers.
        db_connection (Session): The database connection.

    Returns:
        list[Reviews]: The reviews that were created. These have a back-reference to
            the service provider that they were created for.
    """

    one = ServiceProviderReviewRepository.new(
        service_provider_id=create_multiple_service_providers_in_db[0].id,
        review=schemas.NewServiceProviderReview(rating=5),
        user_id=user_id,
        db=db_connection,
    )

    two = ServiceProviderReviewRepository.new(
        service_provider_id=create_multiple_service_providers_in_db[1].id,
        review=schemas.NewServiceProviderReview(rating=2),
        user_id=user_id,
        db=db_connection,
    )

    db_connection.commit()
    return [one, two]


@pytest.fixture
def create_service_provider_reviews_in_db(
    create_service_provider_in_db: models.ServiceProvider,
    service_provider_review: schemas.NewServiceProviderReview,
    db_connection: Session,
) -> models.Reviews:
    """Pre-seed the database with a service provider & reviews.

    Args:
        create_service_provider_in_db (ServiceProvider): The service provider.
        service_provider_review (NewServiceProviderReview): The service provider review.
        db_connection (Session): The database connection.

    Returns:
        Reviews: The review that was created. This has a back-reference to
            the service provider that it was created for.
    """

    review_user_uuid = uuid4()
    service_provider_review_db = ServiceProviderReviewRepository.new(
        create_service_provider_in_db.id,
        service_provider_review,
        review_user_uuid,
        db_connection,
    )
    db_connection.commit()
    return service_provider_review_db
