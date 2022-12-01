from http import HTTPStatus
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Header, Response
from fastapi_versioning import version
from sqlalchemy.orm import Session

from service_provider_api.api.dependencies import get_db
from service_provider_api.core.repositories.service_provider import (
    FailedToCreateServiceProvider,
    ServiceProviderRepository,
    ServiceProviderNotFound,
)
from service_provider_api.core.repositories.service_provider_review import (
    FailedToCreateReview,
    ServiceProviderReviewRepository,
)
from service_provider_api.api import schemas

router = APIRouter(prefix="/service-provider")
log = structlog.get_logger()


@router.post(
    "",
    responses={
        HTTPStatus.CREATED: {"model": schemas.ServiceProviderSchema},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"model": schemas.ErrorResponse},
    },
)
@version(1, 0)
def create_service_provider(
    provider: schemas.NewServiceProviderInSchema,
    response: Response,
    user_id: UUID = Header(),
    db: Session = Depends(get_db),
) -> dict:
    """Create a new service provider with the schema provided in the request body.

    Args:
        provider (schemas.NewServiceProviderInSchema): The schema to create the
            service provider.
        response (Response): The response object to set the status code.
        user_id (UUID): The user id header of the user creating the service provider.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the service provider that was created.
        dict: A dictionary containing the error message.
    """

    try:
        new_service_provider = ServiceProviderRepository.new(provider, user_id, db)
        response.status_code = HTTPStatus.CREATED
        return schemas.ServiceProviderSchema(**new_service_provider.as_dict())
    except FailedToCreateServiceProvider:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return schemas.ErrorResponse(
            error="There was an error creating the service provider. Please try again later."
        )
    except Exception as e:
        log.error("Unexpected error creating service provider", error=e)
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return schemas.ErrorResponse(
            error="There was an error creating the service provider"
        )


@router.post(
    "/{service_provider_id}/review",
    responses={
        HTTPStatus.CREATED: {"model": schemas.ServiceProviderReview},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"model": schemas.ErrorResponse},
    },
)
@version(1, 0)
def add_service_provider_review(
    service_provider_id: UUID,
    review: schemas.NewServiceProviderReview,
    response: Response,
    user_id: UUID = Header(),
    db: Session = Depends(get_db),
) -> dict:
    """Add a review to a service provider.

    Args:
        service_provider_id (UUID): The id of the service provider to add the
            review to.
        review (schemas.NewServiceProviderReview): The review to add to the
            service provider.
        response (Response): The response object to set the status code.
        user_id (UUID): The user id header of the user creating the review.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the review that was created.
        dict: A dictionary containing the error message.
    """

    try:
        new_review = ServiceProviderReviewRepository.new(
            service_provider_id, review, user_id, db
        )
        response.status_code = HTTPStatus.CREATED
        return schemas.ServiceProviderReview.from_orm(new_review)
    except FailedToCreateReview:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return schemas.ErrorResponse(
            error="There was an error creating the service provider review. Please try again later."
        )
    except Exception as e:
        log.error("Unexpected error creating service provider review", error=e)
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return schemas.ErrorResponse(
            error="There was an error creating the service provider review"
        )


@router.get(
    "/{service_provider_id}",
    responses={
        HTTPStatus.OK: {"model": schemas.ServiceProviderSchema},
        HTTPStatus.NOT_FOUND: {"model": schemas.ErrorResponse},
    },
)
@version(1, 0)
def get_service_provider(
    service_provider_id: UUID,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    """Get a service provider by id.

    Args:
        service_provider_id (UUID): The id of the service provider to get.
        response (Response): The response object to set the status code.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the service provider that was found.
        dict: A dictionary containing the error message.
    """

    try:
        service_provider = ServiceProviderRepository.get(service_provider_id, db)
        return schemas.ServiceProviderSchema(**service_provider.as_dict())
    except ServiceProviderNotFound:
        response.status_code = HTTPStatus.NOT_FOUND
        return schemas.ErrorResponse(error="Service provider not found")
    except Exception as e:
        log.error("Unexpected error getting service provider", error=e)
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return schemas.ErrorResponse(
            error="There was an error getting the service provider"
        )


@router.put(
    "/{service_provider_id}",
    responses={
        HTTPStatus.OK: {"model": schemas.ServiceProviderSchema},
        HTTPStatus.NOT_FOUND: {"model": schemas.ErrorResponse},
    },
)
@version(1, 0)
def update_service_provider(
    service_provider_id: UUID,
    updated_service_provider: schemas.NewServiceProviderInSchema,
    response: Response,
    user_id: UUID = Header(),
    db: Session = Depends(get_db),
) -> dict:
    """Update a service provider.

    This endpoint will only update the service provider if the user who is making
    the request is also the user who created the service provider specified by
    the service_provider_id.

    Args:
        service_provider_id (UUID): The id of the service provider to update.
        updated_service_provider (schemas.NewServiceProviderInSchema): The schema
            to update the service provider with.
        response (Response): The response object to set the status code.
        user_id (UUID): The user id header of the user updating the service provider.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the service provider that was updated.
        dict: A dictionary containing the error message.
    """

    try:
        service_provider = ServiceProviderRepository.put(
            updated_service_provider, service_provider_id, user_id, db
        )
        return schemas.ServiceProviderSchema(**service_provider.as_dict())
    except ServiceProviderNotFound:
        # return 404 if the service provider doesn't exist or the user doesn't own it
        # we don't want to do UNAUTHORIZED here as we don't want to leak information
        response.status_code = HTTPStatus.NOT_FOUND
        return schemas.ErrorResponse(error="Service provider not found")
    except Exception as e:
        log.error("Unexpected error updating service provider", error=e)
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return schemas.ErrorResponse(
            error="There was an error updating the service provider. Please try again later."
        )


@router.delete(
    "/{service_provider_id}",
    responses={
        HTTPStatus.OK: {},
        HTTPStatus.NOT_FOUND: {"Model": schemas.ErrorResponse},
    },
)
@version(1, 0)
def delete_service_provider(
    service_provider_id: UUID,
    response: Response,
    user_id: UUID = Header(),
    db: Session = Depends(get_db),
) -> dict:
    """Delete a service provider.

    This endpoint will only delete the service provider if the user who is making
    the request is also the user who created the service provider specified by
    the service_provider_id.

    Args:
        service_provider_id (UUID): The id of the service provider to delete.
        response (Response): The response object to set the status code.
        user_id (UUID): The user id header of the user deleting the service provider.
        db (Session): The database session.

    Returns:
        dict: An empty dictionary, indicating the service provider was deleted.
        dict: A dictionary containing the error message.
    """

    try:
        ServiceProviderRepository.delete(service_provider_id, user_id, db)
        response.status_code = HTTPStatus.OK
        return {}
    except ServiceProviderNotFound:
        # return 404 if the service provider doesn't exist or the user doesn't own it
        # we don't want to do UNAUTHORIZED here as we don't want to leak information
        response.status_code = HTTPStatus.NOT_FOUND
        return schemas.ErrorResponse(error="Service provider not found")
    except Exception as e:
        log.error("Unexpected error deleting service provider", error=e)
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return schemas.ErrorResponse(
            error="There was an error deleting the service provider. Please try again later."
        )
