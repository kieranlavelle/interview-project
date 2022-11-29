from uuid import UUID
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

from service_provider_api.schemas.service_provider.new_service_provider import NewServiceProviderInSchema
from service_provider_api.schemas.service_provider.service_provider import ServiceProviderSchema


def test_can_create_service_provider(
    test_client: TestClient, service_provider: NewServiceProviderInSchema, user_id: UUID
) -> None:

    payload = jsonable_encoder(service_provider)
    response = test_client.post("/service-provider", json=payload, headers={"user-id": str(user_id)})

    # check we get the correct status code back
    if response.status_code != HTTPStatus.CREATED:
        pytest.fail("Service provider not created")

    # check we get the correct type back
    # coerce the response type, if it raises an error the test will fail
    ServiceProviderSchema(**response.json())
