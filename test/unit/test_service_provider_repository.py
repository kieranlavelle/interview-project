from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from service_provider_api import models
from service_provider_api.repositories.service_provider import ServiceProviderRepository
from service_provider_api.schemas.new_service_provider import (
    NewServiceProviderInSchema,
)


def test_can_create_service_provider(
    service_provider: NewServiceProviderInSchema, user_id: UUID, db_connection: Session
) -> None:

    # setup
    new_service_provider = ServiceProviderRepository.new(service_provider, user_id, db_connection)

    # check we get the correct type back
    assert isinstance(new_service_provider, models.ServiceProvider)

    # check that the returned service provider is in the database
    db_service_provider = ServiceProviderRepository.get(new_service_provider.id, db_connection)
    if not isinstance(db_service_provider, models.ServiceProvider):
        pytest.fail("Service provider not found in database")

    # check that the returned service provider is the same as the one we created
    assert new_service_provider == db_service_provider
