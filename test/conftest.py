from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from service_provider_api.utils.database import Base, engine, SessionLocal
from service_provider_api.schemas.service_provider.new_service_provider import (
    NewServiceProviderInSchema,
    ServiceProviderAvailabilitySchema,
)


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
def service_provider() -> NewServiceProviderInSchema:
    return NewServiceProviderInSchema(
        name="John Smith",
        skills=["plumbing", "electrical"],
        cost_in_pence=1000,
        availability=[
            ServiceProviderAvailabilitySchema(
                from_date=date(2021, 1, 1),
                to_date=date(2021, 1, 2),
            ),
            ServiceProviderAvailabilitySchema(
                from_date=date(2021, 1, 3),
                to_date=date(2021, 1, 4),
            ),
        ],
    )
