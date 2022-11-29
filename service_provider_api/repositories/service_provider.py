from uuid import uuid4, UUID
from typing import Optional

from psycopg2.extras import DateRange
from sqlalchemy.orm import Session
from sqlalchemy import exc
import structlog

from service_provider_api import models
from service_provider_api import schemas

log = structlog.get_logger()


class FailedToCreateServiceProvider(Exception):
    pass


class FailedToUpdateServiceProvider(Exception):
    pass


class ServiceProviderNotFound(Exception):
    pass


class FailedToDeleteServiceProvider(Exception):
    pass


class ServiceProviderRepository:
    @staticmethod
    def new(provider: schemas.NewServiceProviderInSchema, user_id: UUID, db: Session) -> models.ServiceProvider:
        """Creates a new service provider in the database.

        Args:
            provider (NewServiceProviderInSchema): The service provider to create.
            user_id (UUID): The user id of the user creating the service provider.
            db (Session): The database connection.

        Raises:
            FailedToCreateServiceProvider: If the service provider could not be created.
        """

        try:
            service_provider_id = uuid4()
            service_provider = models.ServiceProvider(
                id=service_provider_id,
                user_id=user_id,
                name=provider.name,
                cost_in_pence=provider.cost_in_pence,
            )

            with db.begin_nested():
                session_provider = ServiceProviderRepository._insert_service_provider(service_provider, provider, db)

            db.refresh(session_provider)
            return session_provider
        except exc.SQLAlchemyError as e:
            raise FailedToCreateServiceProvider from e

    @staticmethod
    def get(service_provider_id: UUID, db: Session, user_id: Optional[UUID] = None) -> models.ServiceProvider:
        """Gets a service provider from the database.

        Args:
            service_provider_id (UUID): The ID of the service provider to get.
            db (Session): The database connection.
            user_id (Optional[UUID], optional): The user id of the user getting the service provider. Defaults to None.

        Raises:
            ServiceProviderNotFound: If the service provider could not be found.
        """

        if user_id:
            # we want to make sure the calling user owns this service provider resource
            service_provider = (
                db.query(models.ServiceProvider)
                .filter(models.ServiceProvider.id == service_provider_id, models.ServiceProvider.user_id == user_id)
                .first()
            )
        else:
            service_provider = (
                db.query(models.ServiceProvider).filter(models.ServiceProvider.id == service_provider_id).first()
            )

        if not service_provider:
            raise ServiceProviderNotFound

        return service_provider

    @staticmethod
    def delete(service_provider_id: UUID, user_id: UUID, db: Session) -> None:
        """Deletes a service provider from the database.

        Args:
            service_provider_id (UUID): The ID of the service provider to delete.
            user_id (UUID): The ID of the user who owns the service provider.
            db (Session): The database session.

        Raises:
            FailedToDeleteServiceProvider: If the service provider could not be deleted."""

        try:
            service_provider = ServiceProviderRepository.get(service_provider_id, db, user_id)
            if not service_provider:
                # the service provider does not exist, or the user does not own it
                raise ServiceProviderNotFound

            db.delete(service_provider)
            db.commit()

        except exc.SQLAlchemyError as e:
            raise FailedToDeleteServiceProvider from e

    @staticmethod
    def put(
        updated_service_provider: schemas.ServiceProviderSchema, service_provider_id: UUID, user_id: UUID, db: Session
    ) -> models.ServiceProvider:
        """Updates a service provider in the database.

        Args:
            updated_service_provider (ServiceProviderSchema): The updated service provider
            service_provider_id (UUID): The ID of the service provider to update.
            user_id (UUID): The user id of the user making the request. They must own the service provider.
            db (Session): The database session

        Raises:
            ServiceProviderNotFound: If the service provider is not found in the database
            FailedToUpdateServiceProvider: If the service provider fails to update
        """

        try:
            service_provider = ServiceProviderRepository.get(service_provider_id, db, user_id)
            if not service_provider:
                raise ServiceProviderNotFound()

            # this is a put, so we delete everything and then re-insert it in a transaction
            with db.begin_nested():
                db.delete(service_provider)

                service_provider = models.ServiceProvider(
                    id=service_provider_id,
                    user_id=user_id,
                    name=updated_service_provider.name,
                    cost_in_pence=updated_service_provider.cost_in_pence,
                )

                service_provider = ServiceProviderRepository._insert_service_provider(
                    service_provider, updated_service_provider, db
                )

            db.refresh(service_provider)
            return service_provider

        except exc.SQLAlchemyError as e:
            raise FailedToUpdateServiceProvider from e

    @staticmethod
    def list(
        db: Session,
        page: int,
        page_size: int,
        name_filter: Optional[str] = None,
        skills_filter: Optional[str] = None,
        cost_lt_filter: Optional[int] = None,
        cost_gt_filter: Optional[int] = None,
    ) -> list[models.ServiceProvider]:
        """Gets all service providers from the database.

        Args:
            db (Session): The database session.

        Returns:
            list[models.ServiceProvider]: A list of service providers.
        """

        # calculate the offset
        offset = (page - 1) * page_size

        service_providers_query = db.query(models.ServiceProvider)

        # create all of the conditions for the query
        conditions = []
        if name_filter:
            conditions.append(models.ServiceProvider.name == name_filter)
        if cost_gt_filter is not None:
            conditions.append(models.ServiceProvider.cost_in_pence > cost_gt_filter)
        if cost_lt_filter is not None:
            conditions.append(models.ServiceProvider.cost_in_pence < cost_lt_filter)

        # relationship filters have to work using joins as sqlalchemy doesn't support
        # filtering on relationships with the in_ operator
        if skills_filter:
            service_providers_query = service_providers_query.join(models.Skills).filter(
                models.Skills.skill.in_(skills_filter)
            )

        service_providers_query = service_providers_query.filter(*conditions)
        service_providers = service_providers_query.offset(offset).limit(page_size).all()

        return service_providers

    #######################
    ### private methods ###
    #######################
    @staticmethod
    def _insert_service_provider(
        service_provider: models.ServiceProvider, service_provider_schema: schemas.ServiceProviderSchema, db: Session
    ) -> models.ServiceProvider:

        db.add(service_provider)

        # insert the service-providers skills
        for skill in service_provider_schema.skills:
            db.add(models.Skills(service_provider_id=service_provider.id, skill=skill))

        # insert the service-providers availability
        for availability in service_provider_schema.availability:
            db.add(
                models.Availability(
                    service_provider_id=service_provider.id,
                    availability=DateRange(availability.from_date, availability.to_date),
                )
            )
        db.commit()

        return service_provider
