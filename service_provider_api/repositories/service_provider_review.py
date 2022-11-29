from uuid import uuid4, UUID

import structlog
from sqlalchemy.orm import Session
from sqlalchemy import exc

from service_provider_api import models
from service_provider_api import schemas
from service_provider_api.repositories.service_provider import ServiceProviderRepository

log = structlog.get_logger()


class FailedToCreateReview(Exception):
    pass


class ServiceProviderReviewRepository:
    @staticmethod
    def new(
        service_provider_id: UUID, provider: schemas.NewServiceProviderReview, user_id: UUID, db: Session
    ) -> models.ServiceProvider:
        """Create a new service provider review.

        Args:
            service_provider_id (UUID): The ID of the service provider to review.
            provider (NewServiceProviderReview): The review to create.
            user_id (UUID): The ID of the user creating the review.
            db (Session): The database session.

        Raises:
            FailedToCreateReview: If the review could not be created.
        """

        try:
            # check the service provider exists
            service_provider = ServiceProviderRepository.get(service_provider_id, db)
            if not service_provider:
                raise FailedToCreateReview("Service provider not found")

            # create the service provider review
            service_provider_review = models.Reviews(
                id=uuid4(),
                service_provider_id=service_provider_id,
                user_id=user_id,
                rating=provider.rating,
            )
            db.add(service_provider_review)
            db.commit()
            db.refresh(service_provider_review)
            return service_provider_review

        except exc.SQLAlchemyError as e:
            log.error("Failed to create service provider review", error=e)
            raise FailedToCreateReview("An error occurred creating the service provider review") from e
