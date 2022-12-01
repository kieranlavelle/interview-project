"""Module to hold the service provider repo,
and all of the classes and methods relevant to it.."""

from typing import Optional
from uuid import UUID, uuid4

import structlog
from psycopg2.extras import DateRange
from sqlalchemy import exc
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from service_provider_api.api import schemas
from service_provider_api.api.dependencies import ListFilterParams
from service_provider_api.core.utils import list_pairs
from service_provider_api.database import models

log = structlog.get_logger()


class FailedToCreateServiceProvider(Exception):
    """Raised when a service provider cannot be created."""

    pass


class FailedToUpdateServiceProvider(Exception):
    """Raised when a service provider cannot be updated."""

    pass


class ServiceProviderNotFound(Exception):
    """Raised when a service provider cannot be found."""

    pass


class FailedToDeleteServiceProvider(Exception):
    """Raised when a service provider cannot be deleted."""

    pass


class ServiceProviderRepository:
    """Repository for service providers.

    This class aims to provide an easy to user interface which abstracts
    database operations for service providers.
    """

    @staticmethod
    def new(
        provider: schemas.NewServiceProviderInSchema, user_id: UUID, db: Session
    ) -> models.ServiceProvider:
        """Creates a new service provider in the database.

        Args:
            provider (NewServiceProviderInSchema): The service provider to create.
            user_id (UUID): The user id of the user creating the service provider.
            db (Session): The database connection.

        Returns:
            ServiceProvider: The newly created service provider.

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

            session_provider = ServiceProviderRepository._insert_service_provider(
                service_provider, provider, db
            )

            # save our changes to the db
            db.commit()
            db.refresh(session_provider)

            return session_provider
        except exc.SQLAlchemyError as e:
            raise FailedToCreateServiceProvider from e

    @staticmethod
    def get(
        service_provider_id: UUID, db: Session, user_id: Optional[UUID] = None
    ) -> models.ServiceProvider:
        """Gets a service provider from the database.

        Args:
            service_provider_id (UUID): The ID of the service provider to get.
            db (Session): The database connection.
            user_id (Optional[UUID], optional): The user id of the user getting the service provider. Defaults to None.

        Returns:
            ServiceProvider: The service provider identified by the ID.

        Raises:
            ServiceProviderNotFound: If the service provider could not be found.
        """

        if user_id:
            # we want to make sure the calling user owns this service provider resource
            # if the user_id has been provided. This check is mainly used for a get
            # before an update or delete.
            service_provider = (
                db.query(models.ServiceProvider)
                .filter(
                    models.ServiceProvider.id == service_provider_id,
                    models.ServiceProvider.user_id == user_id,
                )
                .first()
            )
        else:
            service_provider = (
                db.query(models.ServiceProvider)
                .filter(models.ServiceProvider.id == service_provider_id)
                .first()
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

        Returns:
            None

        Raises:
            FailedToDeleteServiceProvider: If the service provider could not be deleted."""

        try:
            service_provider = ServiceProviderRepository.get(
                service_provider_id, db, user_id
            )
            if not service_provider:
                # the service provider does not exist, or the user does not own it
                raise ServiceProviderNotFound

            # save our changes to the db
            db.delete(service_provider)
            db.commit()

        except exc.SQLAlchemyError as e:
            raise FailedToDeleteServiceProvider from e

    @staticmethod
    def put(
        updated_service_provider: schemas.ServiceProviderSchema,
        service_provider_id: UUID,
        user_id: UUID,
        db: Session,
    ) -> models.ServiceProvider:
        """Updates a service provider in the database.

        Args:
            updated_service_provider (ServiceProviderSchema): The updated service provider
            service_provider_id (UUID): The ID of the service provider to update.
            user_id (UUID): The user id of the user making the request. They must own the service provider.
            db (Session): The database session

        Returns:
            ServiceProvider (models.ServiceProvider): The updated service provider.

        Raises:
            ServiceProviderNotFound: If the service provider is not found in the database
            FailedToUpdateServiceProvider: If the service provider fails to update
        """

        # for this, sql-alchemy will automatically handle using transactions
        # which is needed as this is a multi-step operation

        try:
            service_provider = ServiceProviderRepository.get(
                service_provider_id, db, user_id
            )
            if not service_provider:
                raise ServiceProviderNotFound()

            # this is a put, so we delete everything and then re-insert it in a transaction
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
            db.commit()
            db.refresh(service_provider)
            return service_provider

        except exc.SQLAlchemyError as e:
            raise FailedToUpdateServiceProvider from e

    @staticmethod
    def list(
        db: Session,
        filters: ListFilterParams,
    ) -> list[models.ServiceProvider]:
        """Gets all service providers from the database.

        Args:
            db (Session): The database session.
            filters (ListFilterParams): The filters to apply to the query.

        Returns:
            list[models.ServiceProvider]: A list of service providers.

        Raises:
            exc.SQLAlchemyError: If the query fails.
        """

        offset = ServiceProviderRepository._calculate_offset(
            filters.page, filters.page_size
        )

        # create all of the conditions for the query
        conditions = ServiceProviderRepository._generate_conditions_for_listing(filters)
        service_providers_query = ServiceProviderRepository._perform_joins_for_listing(
            filters, db
        )
        service_providers_query = service_providers_query.filter(*conditions)
        service_providers = (
            service_providers_query.offset(offset).limit(filters.page_size).all()
        )

        return service_providers

    #######################
    ### private methods ###
    #######################

    @staticmethod
    def _calculate_offset(page: int, page_size: int) -> int:
        """Calculates the offset for a query.

        Args:
            page (int): The page number.
            page_size (int): The page size.

        Returns:
            int: The offset.
        """

        return (page - 1) * page_size

    @staticmethod
    def _perform_joins_for_listing(filters: ListFilterParams, db: Session):
        """Performs the joins for the search query.

        Args:
            filters (ListFilterParams): The filters to apply to the query.
            query (Query): The query to perform the joins on.

        Returns:
            Query: The query with the joins performed.
        """

        query = db.query(models.ServiceProvider).order_by(
            models.ServiceProvider.cost_in_pence.desc()
        )

        # add the review conditions if there are any reviews
        if (
            db.query(models.Reviews)
            .filter(models.Reviews.service_provider_id == models.ServiceProvider.id)
            .count()
        ):
            query = (
                (
                    query.join(models.Reviews)
                    .having(func.avg(models.Reviews.rating) >= filters.reviews_gt)
                    .having(func.avg(models.Reviews.rating) <= filters.reviews_lt)
                )
                .group_by(models.ServiceProvider.id)
                .order_by(func.avg(models.Reviews.rating).desc())
            )

        # relationship filters have to work using joins as sqlalchemy doesn't support
        # filtering on relationships with the in_ operator
        if filters.skills:
            query = query.join(models.Skills).filter(
                models.Skills.skill.in_(filters.skills)
            )

        for lower, upper in list_pairs(filters.availability):
            the_daterange = DateRange(lower, upper)
            query = query.join(models.Availability).filter(
                models.Availability.availability.contained_by(the_daterange)
            )

        return query

    @staticmethod
    def _generate_conditions_for_listing(filters: ListFilterParams) -> list:
        conditions = []
        if filters.name:
            conditions.append(models.ServiceProvider.name == filters.name)
        if filters.cost_gt is not None:
            conditions.append(models.ServiceProvider.cost_in_pence > filters.cost_gt)
        if filters.cost_lt is not None:
            conditions.append(models.ServiceProvider.cost_in_pence < filters.cost_lt)
        return conditions

    @staticmethod
    def _insert_service_provider(
        service_provider: models.ServiceProvider,
        service_provider_schema: schemas.ServiceProviderSchema,
        db: Session,
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
                    availability=DateRange(
                        availability.from_date, availability.to_date
                    ),
                )
            )

        return service_provider
