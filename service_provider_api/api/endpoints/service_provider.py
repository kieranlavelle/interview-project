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
router_2 = APIRouter(prefix="/service-providers")
log = structlog.get_logger()


@router.post(
    "",
    responses={
        HTTPStatus.CREATED: {"model": schemas.ServiceProviderSchema},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"model": schemas.ErrorResponse},
    },
)
@version(1, 0)
async def create_service_provider(
    provider: schemas.NewServiceProviderInSchema,
    response: Response,
    user_id: UUID = Header(),
    db: Session = Depends(get_db),
) -> dict:

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
async def add_service_provider_review(
    service_provider_id: UUID,
    review: schemas.NewServiceProviderReview,
    response: Response,
    user_id: UUID = Header(),
    db: Session = Depends(get_db),
) -> dict:

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


@router.get(
    "/{service_provider_id}",
    responses={
        HTTPStatus.OK: {"model": schemas.ServiceProviderSchema},
        HTTPStatus.NOT_FOUND: {"model": schemas.ErrorResponse},
    },
)
@version(1, 0)
async def get_service_provider(
    service_provider_id: UUID,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:

    try:
        service_provider = ServiceProviderRepository.get(service_provider_id, db)
        return schemas.ServiceProviderSchema(**service_provider.as_dict())
    except ServiceProviderNotFound:
        response.status_code = HTTPStatus.NOT_FOUND
        return schemas.ErrorResponse(error="Service provider not found")


@router.put(
    "/{service_provider_id}",
    responses={
        HTTPStatus.OK: {"model": schemas.ServiceProviderSchema},
        HTTPStatus.NOT_FOUND: {"model": schemas.ErrorResponse},
    },
)
@version(1, 0)
async def update_service_provider(
    service_provider_id: UUID,
    updated_service_provider: schemas.NewServiceProviderInSchema,
    response: Response,
    user_id: UUID = Header(),
    db: Session = Depends(get_db),
) -> dict:

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


@router.delete(
    "/{service_provider_id}",
    responses={
        HTTPStatus.OK: {},
        HTTPStatus.NOT_FOUND: {"Model": schemas.ErrorResponse},
    },
)
@version(1, 0)
async def delete_service_provider(
    service_provider_id: UUID,
    response: Response,
    user_id: UUID = Header(),
    db: Session = Depends(get_db),
) -> dict:

    try:
        ServiceProviderRepository.delete(service_provider_id, user_id, db)
        response.status_code = HTTPStatus.OK
        return {}
    except ServiceProviderNotFound:
        # return 404 if the service provider doesn't exist or the user doesn't own it
        # we don't want to do UNAUTHORIZED here as we don't want to leak information
        response.status_code = HTTPStatus.NOT_FOUND
        return schemas.ErrorResponse(error="Service provider not found")
