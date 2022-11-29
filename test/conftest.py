from datetime import date
from uuid import uuid4, UUID

import pytest
from sqlalchemy.orm import Session

from service_provider_api import models
from service_provider_api.repositories.service_provider import ServiceProviderRepository
from service_provider_api.repositories.service_provider_review import ServiceProviderReviewRepository
from service_provider_api.utils.database import Base, engine, SessionLocal
from service_provider_api import schemas


@pytest.fixture(autouse=True)
def clean_database(db_connection: Session):
    # bind the models to the DB engine
    Base.metadata.create_all(bind=engine)

    db_connection.execute("TRUNCATE TABLE service_providers CASCADE")
    db_connection.commit()


@pytest.fixture
def db_connection() -> Session:
    # bind the models to the DB engine
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def user_id() -> str:
    return uuid4()


@pytest.fixture
def service_provider() -> schemas.NewServiceProviderInSchema:
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
    return schemas.NewServiceProviderReview(
        rating=5,
    )


#############################
### data seeding fixtures ###
#############################


@pytest.fixture
def create_service_provider_in_db(
    service_provider: schemas.NewServiceProviderInSchema, user_id: UUID, db_connection: Session
) -> models.ServiceProvider:
    providers = ServiceProviderRepository.new(service_provider, user_id, db_connection)
    db_connection.commit()
    return providers


@pytest.fixture
def create_multiple_service_providers_in_db(
    multiple_service_providers: list[schemas.NewServiceProviderInSchema], user_id: UUID, db_connection: Session
) -> list[models.ServiceProvider]:
    providers = [
        ServiceProviderRepository.new(provider, user_id, db_connection) for provider in multiple_service_providers
    ]
    db_connection.commit()
    return providers


@pytest.fixture
def create_service_provider_reviews_in_db(
    create_service_provider_in_db: models.ServiceProvider,
    service_provider_review: schemas.NewServiceProviderReview,
    db_connection: Session,
) -> models.Reviews:

    review_user_uuid = uuid4()
    service_provider_review_db = ServiceProviderReviewRepository.new(
        create_service_provider_in_db.id, service_provider_review, review_user_uuid, db_connection
    )
    db_connection.commit()
    return service_provider_review_db
