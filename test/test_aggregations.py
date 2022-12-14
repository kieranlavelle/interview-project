"""Module holds all of the tests relating to
the aggregation endpoints in the API."""

from http import HTTPStatus
from datetime import date

import pytest
from fastapi.testclient import TestClient

from service_provider_api.database import models


@pytest.mark.parametrize(
    "name,expected_provider",
    [("John Smith", "John Smith"), ("Dean Greene", "Dean Greene")],
)
def test_list_service_providers_name_filter(
    test_client: TestClient,
    create_multiple_service_providers_in_db: models.ServiceProvider,
    name: str,
    expected_provider: str,
):
    """Test that the API returns a list of service providers when filtered by name.

    Args:
        test_client (TestClient): The test client fixture.
        create_multiple_service_providers_in_db (models.ServiceProvider): The service
            provider fixture.
        name (str): The name to filter by.
        expected_provider (str): The expected provider name to get back over the API.
    """

    response = test_client.post("/v1_0/service-providers", json={"name": name})

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")

    json_response = response.json()
    matching_service_providers = json_response["service_providers"]

    # get the first service provider and check it is Dean Greene
    first_service_provider = matching_service_providers[0]
    if first_service_provider["name"] != expected_provider:
        pytest.fail("Did not get back the expected service provider from the API.")


@pytest.mark.parametrize(
    "skills,expected_providers",
    [(["plumbing", "SEO"], {"John Smith", "Dean Greene"}), (["SEO"], {"Dean Greene"})],
)
def test_list_service_providers_skills_filter(
    test_client: TestClient,
    create_multiple_service_providers_in_db: models.ServiceProvider,
    skills: list[str],
    expected_providers: set[str],
):
    """Test that the API returns a list of service providers when filtered
    by their skills.

    Args:
        test_client (TestClient): The test client fixture.
        create_multiple_service_providers_in_db (models.ServiceProvider): The service
            provider fixture.
        skills (list[str]): The skills to filter by.
        expected_providers (set[str]): The expected provider names to get back over the
            API.
    """

    response = test_client.post("/v1_0/service-providers", json={"skills": skills})

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")

    json_response = response.json()
    matching_service_providers = json_response["service_providers"]

    # get the first service provider and check it is Dean Greene
    providers = {provider["name"] for provider in matching_service_providers}
    if providers != expected_providers:
        pytest.fail("Did not get back the expected service provider from the API.")


@pytest.mark.parametrize(
    "cost_lt,cost_gt,expected_providers",
    [
        (1500, None, {"John Smith"}),
        (None, 1500, {"Dean Greene"}),
        (5000, 100, {"Dean Greene", "John Smith"}),
        (20, None, set()),
    ],
)
def test_list_service_providers_cost_filter(
    test_client: TestClient,
    create_multiple_service_providers_in_db: models.ServiceProvider,
    cost_lt: int,
    cost_gt: int,
    expected_providers: set[str],
):
    """Test that the API returns a list of service providers filtered by cost.

    Args:
        test_client (TestClient): The test client fixture.
        create_multiple_service_providers_in_db (models.ServiceProvider): The service
            provider fixture.
        cost_lt (int): The upper bound cost to filter by.
        cost_gt (int): The lower bound cost to filter by.
        expected_providers (set[str]): The expected provider names to get back over the
            API.
    """

    params = {"cost_lt": cost_lt, "cost_gt": cost_gt}
    params = {k: v for k, v in params.items() if v is not None}
    response = test_client.post("/v1_0/service-providers", json=params)

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")

    json_response = response.json()
    matching_service_providers = json_response["service_providers"]

    # get the service providers and check it
    providers = {provider["name"] for provider in matching_service_providers}
    if providers != expected_providers:
        pytest.fail("Did not get back the expected service providers from the API.")


@pytest.mark.parametrize(
    "reviews_lt,reviews_gt,expected_providers",
    [
        (4, 1, {"Dean Greene"}),
        (5, 2.5, {"John Smith"}),
        (5, 1, {"Dean Greene", "John Smith"}),
    ],
)
def test_list_service_providers_review_filter(
    test_client: TestClient,
    create_multiple_service_provider_reviews_in_db: models.Reviews,
    reviews_lt: float,
    reviews_gt: float,
    expected_providers: set[str],
):
    """Test that the API returns a list of service providers filtered by review.

    Args:
        test_client (TestClient): The test client fixture.
        create_multiple_service_provider_reviews_in_db (models.Reviews): The service
            provider reviews fixture.
        reviews_lt (float): The upper bound review to filter by.
        reviews_gt (float): The lower bound review to filter by.
        expected_providers (set[str]): The expected provider names to get back over the
            API.
    """

    params = {"reviews_lt": reviews_lt, "reviews_gt": reviews_gt}
    params = {k: v for k, v in params.items() if v is not None}
    response = test_client.post("/v1_0/service-providers", json=params)

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")

    json_response = response.json()
    matching_service_providers = json_response["service_providers"]

    # get the service providers and check it
    providers = {provider["name"] for provider in matching_service_providers}
    if providers != expected_providers:
        pytest.fail("Did not get back the expected service provider from the API.")


@pytest.mark.parametrize(
    "availability,expected_providers",
    [
        (
            [
                {
                    "from_date": date(2020, 1, 1).isoformat(),
                    "to_date": date(2021, 12, 28).isoformat(),
                }
            ],
            {"John Smith"},
        ),
        (
            [
                {
                    "from_date": date(2022, 1, 1).isoformat(),
                    "to_date": date(2023, 1, 1).isoformat(),
                }
            ],
            {"Dean Greene"},
        ),
        (
            [
                {
                    "from_date": date(2020, 1, 1).isoformat(),
                    "to_date": date(2023, 1, 1).isoformat(),
                }
            ],
            {"John Smith", "Dean Greene"},
        ),
    ],
)
def test_list_service_providers_availability_filter(
    test_client: TestClient,
    create_multiple_service_provider_reviews_in_db: models.Reviews,
    availability: list[str],
    expected_providers: set[str],
):
    """Test that the API returns a list of service providers filtered by availability.

    Args:
        test_client (TestClient): The test client fixture.
        create_multiple_service_provider_reviews_in_db (models.Reviews): The service
            provider reviews fixture.
        availability (list[str]): The availability to filter by.
        expected_providers (set[str]): The expected provider names to get back over the
            API.
    """

    params = {"availability": availability}
    response = test_client.post("/v1_0/service-providers", json=params)

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")

    json_response = response.json()
    matching_service_providers = json_response["service_providers"]

    # get the service providers and check it
    providers = {provider["name"] for provider in matching_service_providers}
    if providers != expected_providers:
        pytest.fail("Did not get back the expected service providers from the API.")


@pytest.mark.parametrize(
    "min_rating,skills,expected_days,budget,availability,expected_providers",
    [
        (
            1,
            ["plumbing", "SEO"],
            3,
            5000,
            [
                {
                    "from_date": date(2020, 1, 1).isoformat(),
                    "to_date": date(2024, 12, 28).isoformat(),
                }
            ],
            {"John Smith"},
        ),
        (
            1,
            ["plumbing", "SEO"],
            3,
            7000,
            [
                {
                    "from_date": date(2020, 1, 1).isoformat(),
                    "to_date": date(2024, 12, 28).isoformat(),
                }
            ],
            {"John Smith", "Dean Greene"},
        ),
        (
            1,
            ["plumbing", "SEO"],
            3,
            7000,
            [
                {
                    "from_date": date(2020, 1, 1).isoformat(),
                    "to_date": date(2021, 5, 1).isoformat(),
                },
            ],
            {"John Smith"},
        ),
    ],
)
def test_can_get_recommended_service_providers(
    test_client: TestClient,
    create_multiple_service_provider_reviews_in_db: models.Reviews,
    min_rating: int,
    skills: list[str],
    expected_days: int,
    budget: int,
    availability: list[str],
    expected_providers: set[str],
):
    """Test that the API returns a list of recommended service providers according
    to the given parameters.

    Args:
        test_client (TestClient): The test client fixture.
        create_multiple_service_provider_reviews_in_db (models.Reviews): The service
            provider reviews fixture.
        min_rating (int): The upper bound rating to filter by.
        skills (list[str]): The skills to filter by.
        expected_days (int): The expected days to complete the project.
        budget (int): The budget of the project.
        availability (list[str]): The availability to filter by.
        expected_providers (set[str]): The expected provider names to get back over the
            API.
    """

    payload = {
        "expected_job_duration_in_days": expected_days,
        "job_budget_in_pence": budget,
        "skills": skills,
        "availability": availability,
        "minimum_review_rating": min_rating,
    }
    response = test_client.post("/v1_0/service-providers/recommend", json=payload)

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")

    json_response = response.json()
    matching_service_providers = json_response["service_providers"]

    # get the service providers and check it
    providers = {provider["name"] for provider in matching_service_providers}
    if providers != expected_providers:
        pytest.fail("Did not get back the expected service providers from the API.")


def test_pagintation(
    test_client: TestClient,
    create_multiple_service_provider_reviews_in_db: models.Reviews,
):
    """Test that the API returns a list of service providers that can be paginated.

    Args:
        test_client (TestClient): The test client fixture.
        create_multiple_service_provider_reviews_in_db (models.Reviews): The service
            provider reviews fixture.
    """

    response = test_client.post(
        "/v1_0/service-providers", params={"page": 1, "page_size": 1}, json={}
    )
    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")
    json_response = response.json()
    if len(json_response["service_providers"]) != 1:
        pytest.fail("Did not get the expected number of service providers")

    # get the second page
    response = test_client.post(
        "/v1_0/service-providers", params={"page": 2, "page_size": 1}, json={}
    )
    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")
    json_response = response.json()
    if len(json_response["service_providers"]) != 1:
        pytest.fail(
            "Did not get the expected number of service providers for the second page."
        )
