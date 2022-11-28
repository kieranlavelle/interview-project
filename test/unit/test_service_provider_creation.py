from uuid import uuid4

import pytest

from service_provider_api.models.service_provider import ServiceProviderModel
from service_provider_api.repositories.service_provider import ServiceProviderRepository
from service_provider_api.schemas.service_provider.new_service_provider import (
    NewServiceProviderInSchema,
)


def test_can_create_service_provider(
    example_service_provider_schema_fixture: NewServiceProviderInSchema,
) -> None:

    user_id = uuid4()

    # setup
    new_service_provider = ServiceProviderRepository.new(
        example_service_provider_schema_fixture, user_id
    )

    # check we get the correct type back
    assert isinstance(new_service_provider, ServiceProviderModel)

    # check that the returned service provider is in the database
    db_service_provider = ServiceProviderRepository.get(
        new_service_provider.id, user_id
    )
    if not isinstance(db_service_provider, ServiceProviderModel):
        pytest.fail("Service provider not found in database")

    # check that the returned service provider is the same as the one we created
    assert new_service_provider == db_service_provider
