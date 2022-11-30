from uuid import UUID
from http import HTTPStatus
from datetime import date

import pytest
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from service_provider_api.database import models
from service_provider_api.api import schemas


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
        f"/v1_0/service-provider/{create_service_provider_in_db.id}",
        json=payload,
        headers={"user-id": str(user_id)},
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


def test_cant_update_service_provider_we_dont_own(
    test_client: TestClient,
    create_service_provider_in_db: models.ServiceProvider,
    service_provider: schemas.NewServiceProviderInSchema,
) -> None:

    # change the name on the service provider
    service_provider.name = "New Name"

    payload = jsonable_encoder(service_provider)
    response = test_client.put(
        f"/v1_0/service-provider/{create_service_provider_in_db.id}",
        json=payload,
        headers={"user-id": "00000000-0000-0000-0000-000000000000"},
    )

    # check we get the correct status code back
    if response.status_code != HTTPStatus.NOT_FOUND:
        pytest.fail("Managed to update a service provider we don't own")


def test_can_update_availability(
    test_client: TestClient,
    create_service_provider_in_db: models.ServiceProvider,
    service_provider: schemas.NewServiceProviderInSchema,
    user_id: UUID,
    db_connection: Session,
):

    # change the name on the service provider
    service_provider.availability = [
        {
            "from_date": date(2019, 1, 1),
            "to_date": date(2019, 12, 31),
        }
    ]

    payload = jsonable_encoder(service_provider)
    response = test_client.put(
        f"/v1_0/service-provider/{create_service_provider_in_db.id}",
        json=payload,
        headers={"user-id": str(user_id)},
    )

    # check we get the correct status code back
    if response.status_code != HTTPStatus.OK:
        pytest.fail("Could not update the availability of the service provider.")

    # check the service provider is updated in the databse
    service_provider = (
        db_connection.query(models.ServiceProvider)
        .filter(models.ServiceProvider.id == create_service_provider_in_db.id)
        .first()
    )

    if service_provider.availability[0].availability.lower != date(2019, 1, 1):
        pytest.fail("Service provider availability not updated in the database.")
    if service_provider.availability[0].availability.upper != date(2019, 12, 31):
        pytest.fail("Service provider availability not updated in the database.")


def test_can_update_skills(
    test_client: TestClient,
    create_service_provider_in_db: models.ServiceProvider,
    service_provider: schemas.NewServiceProviderInSchema,
    user_id: UUID,
    db_connection: Session,
):
    # change the skills of the service provider
    skills = ["Software Engineering", "Python", "Django", "FastAPI", "SQLAlchemy"]
    service_provider.skills = skills

    payload = jsonable_encoder(service_provider)
    response = test_client.put(
        f"/v1_0/service-provider/{create_service_provider_in_db.id}",
        json=payload,
        headers={"user-id": str(user_id)},
    )

    # check we get the correct status code back
    if response.status_code != HTTPStatus.OK:
        pytest.fail("Could not update the skills of the service provider.")

    # check the service provider is updated in the databse
    service_provider = (
        db_connection.query(models.ServiceProvider)
        .filter(models.ServiceProvider.id == create_service_provider_in_db.id)
        .first()
    )

    service_provider_skills = [s.skill for s in service_provider.skills]
    if service_provider_skills != skills:
        pytest.fail("Service provider skills not updated in the database.")
