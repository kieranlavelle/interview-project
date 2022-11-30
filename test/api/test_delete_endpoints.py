from uuid import UUID
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from service_provider_api import models


def test_cant_delete_for_non_existant_service_provider(test_client: TestClient, user_id: UUID) -> None:
    response = test_client.delete(
        "/v1_0/service-provider/00000000-0000-0000-0000-000000000000",
        headers={"user-id": str(user_id)},
    )
    if response.status_code != HTTPStatus.NOT_FOUND:
        pytest.fail("API returned a status code other than 404")


def test_user_cant_delete_service_provider_they_dont_own(
    test_client: TestClient, create_service_provider_reviews_in_db: models.Reviews
) -> None:
    response = test_client.delete(
        f"/v1_0/service-provider/{create_service_provider_reviews_in_db.service_provider_id}",
        headers={"user-id": "00000000-0000-0000-0000-000000000000"},
    )
    if response.status_code != HTTPStatus.NOT_FOUND:
        pytest.fail("API returned a status code other than 404")


def test_delete_service_provider(
    test_client: TestClient, user_id: UUID, create_service_provider_reviews_in_db: models.Reviews
) -> None:
    """Test that the API returns a service provider with reviews calculated"""

    response = test_client.delete(
        f"/v1_0/service-provider/{create_service_provider_reviews_in_db.service_provider_id}",
        headers={"user-id": str(user_id)},
    )

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 404")

    json_response = response.json()
    if json_response != {}:
        pytest.fail("API returned a non-empty response")


def test_deleting_service_provider_cascades(
    test_client: TestClient,
    user_id: UUID,
    create_service_provider_reviews_in_db: models.Reviews,
    db_connection: Session,
) -> None:

    # check the service prover is in the database
    service_provider = (
        db_connection.query(models.ServiceProvider)
        .filter(models.ServiceProvider.id == create_service_provider_reviews_in_db.service_provider_id)
        .one()
    )
    if not service_provider:
        pytest.fail("Service provider not in database. Can't test cascade")

    # check the reviews are in the database
    if not service_provider.review_rating:
        pytest.fail("Service provider has no reviews. Can't test cascade")

    # check the skills are in the database
    if not service_provider.skills:
        pytest.fail("Service provider has no skills. Can't test cascade")

    # check the availability is in the database
    if not service_provider.availability:
        pytest.fail("Service provider has no availability. Can't test cascade")

    # delete the service provider
    response = test_client.delete(
        f"/v1_0/service-provider/{create_service_provider_reviews_in_db.service_provider_id}",
        headers={"user-id": str(user_id)},
    )

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")

    # check the service provider deletion cascaded
    # if there are
    skills = (
        db_connection.query(models.Skills)
        .filter(models.Skills.service_provider_id == service_provider.id)
        .one_or_none()
    )
    availability = (
        db_connection.query(models.Availability)
        .filter(models.Availability.service_provider_id == service_provider.id)
        .one_or_none()
    )
    reviews = (
        db_connection.query(models.Reviews)
        .filter(models.Reviews.service_provider_id == service_provider.id)
        .one_or_none()
    )

    if skills or availability or reviews:
        pytest.fail("Service provider deletion did not cascade")
