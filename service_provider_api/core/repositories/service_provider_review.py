"""Module to hold the service provider review repo,
and all of the classes and methods relevant to it.."""

from uuid import UUID

import structlog
from sqlalchemy import exc
from sqlalchemy.orm import Session

from service_provider_api.api import schemas
from service_provider_api.core.repositories.service_provider import (
    ServiceProviderRepository,
)
from service_provider_api.database import models

log = structlog.get_logger()


class FailedToCreateReview(Exception):
    """Raised when a review cannot be created."""

    pass


class ServiceProviderReviewRepository:
    """Repository for service provider reviews.

    This class aims to provide an easy to user interface which abstracts
    database operations for service provider reviews.
    """

    @staticmethod
    def new(
        service_provider_id: UUID,
        review: schemas.NewServiceProviderReview,
        user_id: UUID,
        db: Session,
    ) -> models.ServiceProvider:
        """Create a new service provider review.

        Args:
            service_provider_id (UUID): The ID of the service provider to review.
            review (NewServiceProviderReview): The review to create.
            user_id (UUID): The ID of the user creating the review.
            db (Session): The database session.

        Returns:
            ServiceProvider: The service provider with the new review.

        Raises:
            FailedToCreateReview: If the review could not be created.
        """

        try:
            # check the service provider exists
            service_provider = ServiceProviderRepository.get(service_provider_id, db)
            if not service_provider:
                raise FailedToCreateReview("Service provider not found")
            log.info(
                "service provider found", service_provider=service_provider.as_dict()
            )

            # create the service provider review
            service_provider_review = models.Reviews(
                service_provider_id=service_provider_id,
                user_id=user_id,
                rating=review.rating,
            )

            # add the review to the database
            db.add(service_provider_review)
            db.commit()
            db.refresh(service_provider_review)
            return service_provider_review

        except exc.SQLAlchemyError as e:
            log.error("Failed to create service provider review", error=e)
            raise FailedToCreateReview(
                "An error occurred creating the service provider review"
            ) from e
