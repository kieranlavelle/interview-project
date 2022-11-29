from uuid import UUID
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from service_provider_api import models


def test_cant_delete_for_non_existant_service_provider(test_client: TestClient, user_id: UUID) -> None:
    response = test_client.delete(
        "/service-provider/00000000-0000-0000-0000-000000000000",
        headers={"user-id": str(user_id)},
    )
    if response.status_code != HTTPStatus.NOT_FOUND:
        pytest.fail("API returned a status code other than 404")


def test_user_cant_delete_service_provider_they_dont_own(
    test_client: TestClient, create_service_provider_reviews_in_db: models.Reviews
) -> None:
    response = test_client.delete(
        f"/service-provider/{create_service_provider_reviews_in_db.service_provider_id}",
        headers={"user-id": "00000000-0000-0000-0000-000000000000"},
    )
    if response.status_code != HTTPStatus.NOT_FOUND:
        pytest.fail("API returned a status code other than 404")


def test_delete_service_provider(
    test_client: TestClient, user_id: UUID, create_service_provider_reviews_in_db: models.Reviews
) -> None:
    """Test that the API returns a service provider with reviews calculated"""

    response = test_client.delete(
        f"/service-provider/{create_service_provider_reviews_in_db.service_provider_id}",
        headers={"user-id": str(user_id)},
    )

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 404")

    json_response = response.json()
    if json_response != {}:
        pytest.fail("API returned a non-empty response")
