"""Module to hold all of the unit tests for the POST endpoints."""

from uuid import UUID
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

from service_provider_api.database import models
from service_provider_api.api import schemas


# TODO: Come back and check payloads


def test_can_create_service_provider(
    test_client: TestClient,
    service_provider: schemas.NewServiceProviderInSchema,
    user_id: UUID,
) -> None:
    """Test that we can create a service provider over the API.

    Args:
        test_client (TestClient): The FastAPI test client.
        service_provider (schemas.NewServiceProviderInSchema): The service provider
            that we want to create.
        user_id (UUID): The user ID who created the service provider.
    """

    payload = jsonable_encoder(service_provider)
    response = test_client.post(
        "/v1_0/service-provider", json=payload, headers={"user-id": str(user_id)}
    )

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
    """Test that we can create a service provider review over the API.

    Args:
        test_client (TestClient): The FastAPI test client.
        user_id (UUID): The user ID who created the service provider.
        service_provider_review (schemas.NewServiceProviderReview): The service provider
            review that we want to create.
        create_service_provider_in_db (models.ServiceProvider): The service provider
            that was created in the database.
    """

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
        pytest.fail("Review received from API does not match the one sent")
