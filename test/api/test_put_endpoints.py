from uuid import UUID
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

from service_provider_api import models
from service_provider_api import schemas


def test_can_update_service_provider(
    test_client: TestClient,
    create_service_provider_in_db: models.ServiceProvider,
    service_provider: schemas.NewServiceProviderInSchema,
    user_id: UUID,
) -> None:

    # change the name on the service provider
    service_provider.name = "New Name"

    payload = jsonable_encoder(service_provider)
    response = test_client.put(
        f"/service-provider/{create_service_provider_in_db.id}", json=payload, headers={"user-id": str(user_id)}
    )

    # check we get the correct status code back
    if response.status_code != HTTPStatus.OK:
        pytest.fail("Service provider not created")

    # check we get the correct type back
    # coerce the response type, if it raises an error the test will fail
    json_response = response.json()
    schemas.ServiceProviderSchema(**json_response)

    # check that the service provder name has been updated
    if json_response["name"] != "New Name":
        pytest.fail("Service provider name not updated")


def test_cany_update_service_provider_we_dont_own(
    test_client: TestClient,
    create_service_provider_in_db: models.ServiceProvider,
    service_provider: schemas.NewServiceProviderInSchema,
) -> None:

    # change the name on the service provider
    service_provider.name = "New Name"

    payload = jsonable_encoder(service_provider)
    response = test_client.put(
        f"/service-provider/{create_service_provider_in_db.id}",
        json=payload,
        headers={"user-id": "00000000-0000-0000-0000-000000000000"},
    )

    # check we get the correct status code back
    if response.status_code != HTTPStatus.NOT_FOUND:
        pytest.fail("Service provider not created")


def test_can_update_availability():
    raise NotImplementedError


def test_can_update_skills():
    raise NotImplementedError


def test_cant_update_rating():
    raise NotImplementedError
