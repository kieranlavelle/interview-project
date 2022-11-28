from datetime import datetime

import pytest

from service_provider_api.schemas.service_provider.new_service_provider import (
    NewServiceProviderInSchema,
    ServiceProviderAvailabilitySchema,
)
from service_provider_api.utils.database import get_connecton


@pytest.fixture(autouse=True)
def clean_database():
    with get_connecton() as connection:
        cursor = connection.cursor()
        cursor.execute("TRUNCATE service_providers CASCADE")
        cursor.execute("TRUNCATE service_provider_skills CASCADE")
        cursor.execute("TRUNCATE service_provider_availability CASCADE")
        connection.commit()


@pytest.fixture
def example_service_provider_schema_fixture() -> NewServiceProviderInSchema:
    return NewServiceProviderInSchema(
        name="John Smith",
        skills=["plumbing", "electrical"],
        cost_in_pence=1000,
        availability=[
            ServiceProviderAvailabilitySchema(
                from_date=datetime(2021, 1, 1, 0, 0, 0),
                to_date=datetime(2021, 1, 2, 23, 59, 59),
            ),
            ServiceProviderAvailabilitySchema(
                from_date=datetime(2021, 1, 3, 0, 0, 0),
                to_date=datetime(2021, 1, 4, 23, 59, 59),
            ),
        ],
        review_rating=4.5,
    )
