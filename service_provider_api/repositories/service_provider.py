from uuid import uuid4, UUID

import psycopg2
from psycopg2.extras import DateRange

from service_provider_api.utils.database import get_connecton
from service_provider_api.models.database.service_provider import (
    INSERT_SERVICE_PROVIDER,
    INSERT_SERVICE_PROVIDER_AVAILABILITY,
    INSERT_SERVICE_PROVIDER_SKILL,
    SELECT_SERVICE_PROVIDER,
    DELETE_SERVICE_PROVIDER,
)
from service_provider_api.models.service_provider import ServiceProviderModel
from service_provider_api.schemas.service_provider.service_provider import (
    ServiceProviderSchema,
)
from service_provider_api.schemas.service_provider.new_service_provider import (
    NewServiceProviderInSchema,
)

# TODO: Add logging


class FailedToCreateServiceProvider(Exception):
    pass


class ServiceProviderNotFound(Exception):
    pass


class ServiceProviderRepository:
    @staticmethod
    def new(
        provider: NewServiceProviderInSchema, user_id: UUID
    ) -> ServiceProviderModel:

        service_provider = ServiceProviderModel(
            id=uuid4(),
            user_id=user_id,
            name=provider.name,
            skills=provider.skills,
            cost_in_pence=provider.cost_in_pence,
            availability=provider.availability,
            review_rating=provider.review_rating,
        )

        # create a transaction and insert all of the data we need to
        # to create a new service provder.
        try:
            with get_connecton() as connection:
                cursor = connection.cursor()

                # insert the service provider
                ServiceProviderRepository._insert_service_provider(
                    cursor, service_provider, user_id
                )

        except psycopg2.DatabaseError as error:
            raise FailedToCreateServiceProvider from error

        return service_provider

    @staticmethod
    def get(service_provider_id: str, user_id: UUID) -> ServiceProviderModel:
        with get_connecton() as connection:
            cursor = connection.cursor()
            cursor.execute(
                SELECT_SERVICE_PROVIDER, {"id": service_provider_id, "user_id": user_id}
            )

            # TODO: handle the case where the service provider does not exist
            results = cursor.fetchone()

        if results is None:
            raise ServiceProviderNotFound()

        return ServiceProviderModel(
            id=results["id"],
            user_id=results["user_id"],
            name=results["name"],
            skills=results["skills"],
            cost_in_pence=results["cost_in_pence"],
            availability=[
                {"from_date": daterange.lower, "to_date": daterange.upper}
                for daterange in results["availability"]
            ],
            review_rating=results["review_rating"],
        )

    @staticmethod
    def put(
        updated_service_provider: ServiceProviderSchema, user_id: UUID
    ) -> ServiceProviderModel:

        service_provider = ServiceProviderModel(
            id=updated_service_provider.id,
            user_id=user_id,
            name=updated_service_provider.name,
            skills=updated_service_provider.skills,
            cost_in_pence=updated_service_provider.cost_in_pence,
            availability=updated_service_provider.availability,
            review_rating=updated_service_provider.review_rating,
        )

        # this is a put, so we delete everything and then re-insert it
        with get_connecton() as connection:
            cursor = connection.cursor()

            # TODO: we should check it exists.
            # TODO: we should add a user_id to it
            # this first command is a delete if exists...
            cursor.execute(
                DELETE_SERVICE_PROVIDER,
                {"id": updated_service_provider.id, "user_id": user_id},
            )

            # insert the service provider
            ServiceProviderRepository._insert_service_provider(
                cursor, service_provider, user_id
            )

        return service_provider

    ### private methods
    @staticmethod
    def _insert_service_provider(
        cursor, service_provider: ServiceProviderModel, user_id: UUID
    ):
        cursor.execute(
            INSERT_SERVICE_PROVIDER,
            {
                "id": service_provider.id,
                "user_id": user_id,
                "name": service_provider.name,
                "cost_in_pence": service_provider.cost_in_pence,
                "review_rating": service_provider.review_rating,
            },
        )

        # insert the service-providers skills
        for skill in service_provider.skills:
            cursor.execute(
                INSERT_SERVICE_PROVIDER_SKILL,
                {
                    "service_provider_id": service_provider.id,
                    "skill": skill,
                },
            )

        # insert the service-providers availability
        for availability in service_provider.availability:
            cursor.execute(
                INSERT_SERVICE_PROVIDER_AVAILABILITY,
                {
                    "service_provider_id": service_provider.id,
                    "availability": DateRange(
                        availability.from_date, availability.to_date
                    ),
                },
            )
