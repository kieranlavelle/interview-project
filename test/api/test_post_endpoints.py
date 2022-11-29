from uuid import UUID
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

from service_provider_api import models
from service_provider_api.schemas.new_service_provider import NewServiceProviderInSchema
from service_provider_api.schemas.service_provider import ServiceProviderSchema
from service_provider_api.schemas.service_provider_review import (
    NewServiceProviderReview,
    ServiceProviderReview,
)


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


def test_can_create_service_provider_review(
    test_client: TestClient,
    user_id: UUID,
    service_provider_review: NewServiceProviderReview,
    create_service_provider_in_db: models.ServiceProvider,
) -> None:

    payload = jsonable_encoder(service_provider_review)
    response = test_client.post(
        f"/service-provider/{create_service_provider_in_db.id}/review", json=payload, headers={"user-id": str(user_id)}
    )

    # check we get the correct status code back
    if response.status_code != HTTPStatus.CREATED:
        pytest.fail("Service provider review not created")

    # check we get the correct type back
    # coerce the response type, if it raises an error the test will fail
    review = ServiceProviderReview(**response.json())

    # check the review we get back is the one we created
    if ServiceProviderReview(**payload, user_id=user_id) != review:
        pytest.fail("Review recieved from API does not match the one sent")
