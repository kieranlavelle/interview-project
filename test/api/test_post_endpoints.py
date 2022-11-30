from uuid import UUID
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

from service_provider_api import models
from service_provider_api import schemas


def test_can_create_service_provider(
    test_client: TestClient, service_provider: schemas.NewServiceProviderInSchema, user_id: UUID
) -> None:

    payload = jsonable_encoder(service_provider)
    response = test_client.post("/v1_0/service-provider", json=payload, headers={"user-id": str(user_id)})

    # check we get the correct status code back
    if response.status_code != HTTPStatus.CREATED:
        pytest.fail("Service provider not created")

    # check we get the correct type back
    # coerce the response type, if it raises an error the test will fail
    schemas.ServiceProviderSchema(**response.json())


def test_can_create_service_provider_review(
    test_client: TestClient,
    user_id: UUID,
    service_provider_review: schemas.NewServiceProviderReview,
    create_service_provider_in_db: models.ServiceProvider,
) -> None:

    payload = jsonable_encoder(service_provider_review)
    response = test_client.post(
        f"/v1_0/service-provider/{create_service_provider_in_db.id}/review",
        json=payload,
        headers={"user-id": str(user_id)},
    )

    # check we get the correct status code back
    if response.status_code != HTTPStatus.CREATED:
        pytest.fail("Service provider review not created")

    # check we get the correct type back
    # coerce the response type, if it raises an error the test will fail
    review = schemas.ServiceProviderReview(**response.json())

    # check the review we get back is the one we created
    if schemas.ServiceProviderReview(**payload, user_id=user_id) != review:
        pytest.fail("Review recieved from API does not match the one sent")
