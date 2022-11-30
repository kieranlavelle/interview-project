from http import HTTPStatus
from datetime import date

import pytest
from fastapi.testclient import TestClient

from service_provider_api import models


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
    """Test that the API returns a list of service providers.

    Test that we can get a paginated list of service providers & filters work.
    """

    response = test_client.get("/v1_0/service-providers", params={"name": name})

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")

    json_response = response.json()
    matching_service_providers = json_response["service_providers"]

    # get the first service provider and check it is Dean Greene
    first_service_provider = matching_service_providers[0]
    if first_service_provider["name"] != expected_provider:
        pytest.fail("Service provider name is not correct")


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
    """Test that the API returns a list of service providers.

    Test that we can get a paginated list of service providers & filters work.
    """

    response = test_client.get("/v1_0/service-providers", params={"skills": skills})

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")

    json_response = response.json()
    matching_service_providers = json_response["service_providers"]

    # get the first service provider and check it is Dean Greene
    providers = {provider["name"] for provider in matching_service_providers}
    if providers != expected_providers:
        pytest.fail("Service provider name is not correct")


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
    """Test that the API returns a list of service providers.

    Test that we can get a paginated list of service providers & filters work.
    """

    params = {"cost_lt": cost_lt, "cost_gt": cost_gt}
    params = {k: v for k, v in params.items() if v is not None}
    response = test_client.get("/v1_0/service-providers", params=params)

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")

    json_response = response.json()
    matching_service_providers = json_response["service_providers"]

    # get the service providers and check it
    providers = {provider["name"] for provider in matching_service_providers}
    if providers != expected_providers:
        pytest.fail("Service provider name is not correct")


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
    """Test that the API returns a list of service providers.

    Test that we can get a paginated list of service providers & filters work.
    """

    params = {"reviews_lt": reviews_lt, "reviews_gt": reviews_gt}
    params = {k: v for k, v in params.items() if v is not None}
    response = test_client.get("/v1_0/service-providers", params=params)

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")

    json_response = response.json()
    matching_service_providers = json_response["service_providers"]

    # get the service providers and check it
    providers = {provider["name"] for provider in matching_service_providers}
    if providers != expected_providers:
        pytest.fail("Service provider name is not correct")


@pytest.mark.parametrize(
    "availability,expected_providers",
    [
        (
            [date(2020, 1, 1).isoformat(), date(2021, 12, 28).isoformat()],
            {"John Smith"},
        ),
        ([date(2022, 1, 1).isoformat(), date(2023, 1, 1).isoformat()], {"Dean Greene"}),
        (
            [date(2020, 1, 1).isoformat(), date(2023, 1, 1).isoformat()],
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
    """Test that the API returns a list of service providers.

    Test that we can get a paginated list of service providers & filters work.
    """

    params = {"availability": availability}
    response = test_client.get("/v1_0/service-providers", params=params)

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")

    json_response = response.json()
    matching_service_providers = json_response["service_providers"]

    # get the service providers and check it
    providers = {provider["name"] for provider in matching_service_providers}
    if providers != expected_providers:
        pytest.fail("Did not get the expected service providers")


@pytest.mark.parametrize(
    "min_rating,skills,expected_days,budget,availability,expected_providers",
    [
        (
            1,
            ["plumbing", "SEO"],
            3,
            5000,
            [date(2020, 1, 1).isoformat(), date(2024, 12, 28).isoformat()],
            {"John Smith"},
        ),
        (
            1,
            ["plumbing", "SEO"],
            3,
            7000,
            [date(2020, 1, 1).isoformat(), date(2024, 12, 28).isoformat()],
            {"John Smith", "Dean Greene"},
        ),
        (
            1,
            ["plumbing", "SEO"],
            3,
            7000,
            [date(2020, 1, 1).isoformat(), date(2021, 5, 1).isoformat()],
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

    params = {
        "expected_job_duration_in_days": expected_days,
        "job_budget_in_pence": budget,
        "skills": skills,
        "availability": availability,
        "minimum_review_rating": min_rating,
    }
    response = test_client.get("/v1_0/service-providers/recommend", params=params)

    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")

    json_response = response.json()
    matching_service_providers = json_response["service_providers"]

    # get the service providers and check it
    providers = {provider["name"] for provider in matching_service_providers}
    if providers != expected_providers:
        pytest.fail("Service provider name is not correct")


def test_pagintation(
    test_client: TestClient,
    create_multiple_service_provider_reviews_in_db: models.Reviews,
):

    response = test_client.get(
        "/v1_0/service-providers", params={"page": 1, "page_size": 1}
    )
    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")
    json_response = response.json()
    if len(json_response["service_providers"]) != 1:
        pytest.fail("Did not get the expected number of service providers")

    # get the second page
    response = test_client.get(
        "/v1_0/service-providers", params={"page": 2, "page_size": 1}
    )
    if response.status_code != HTTPStatus.OK:
        pytest.fail("API returned a status code other than 200")
    json_response = response.json()
    if len(json_response["service_providers"]) != 1:
        pytest.fail(
            "Did not get the expected number of service providers for the second page."
        )
