from uuid import UUID
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from service_provider_api.database import models


def test_raises_not_found_for_non_existant_service_provider(
    test_client: TestClient,
) -> None:
    response = test_client.get(
        "/v1_0/service-provider/00000000-0000-0000-0000-000000000000",
        headers={"user-id": "00000000-0000-0000-0000-000000000000"},
    )
    if response.status_code != HTTPStatus.NOT_FOUND:
        pytest.fail("API returned a status code other than 404")


def test_get_service_provider_with_reviews(
    test_client: TestClient,
    user_id: UUID,
    create_service_provider_reviews_in_db: models.Reviews,
) -> None:
    """Test that the API returns a service provider with reviews calculated"""

    response = test_client.get(
        f"/v1_0/service-provider/{create_service_provider_reviews_in_db.service_provider_id}",
        headers={"user-id": str(user_id)},
    )

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")

    json_response = response.json()
    if json_response["review_rating"] != 5.0:
        pytest.fail("Review rating is not correct")
