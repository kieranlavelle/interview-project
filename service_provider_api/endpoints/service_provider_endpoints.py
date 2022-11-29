from http import HTTPStatus
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.orm import Session

from service_provider_api.dependencies import get_db
from service_provider_api.repositories.service_provider import (
    FailedToCreateServiceProvider,
    ServiceProviderRepository,
    ServiceProviderNotFound,
)
from service_provider_api.repositories.service_provider_review import (
    FailedToCreateReview,
    ServiceProviderReviewRepository,
)
from service_provider_api.schemas.base import ErrorResponse
from service_provider_api.schemas.service_provider_review import (
    NewServiceProviderReview,
    ServiceProviderReview,
)
from service_provider_api.schemas.new_service_provider import NewServiceProviderInSchema
from service_provider_api.schemas.service_provider import ServiceProviderSchema

router = APIRouter(prefix="/service-provider")
log = structlog.get_logger()


@router.post(
    "",
    responses={
        HTTPStatus.CREATED: {"model": ServiceProviderSchema},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def create_service_provider(
    provider: NewServiceProviderInSchema, response: Response, user_id: UUID = Header(), db: Session = Depends(get_db)
) -> dict:

    try:
        new_service_provider = ServiceProviderRepository.new(provider, user_id, db)
        response.status_code = HTTPStatus.CREATED
        return ServiceProviderSchema(**new_service_provider.as_dict())
    except FailedToCreateServiceProvider:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return ErrorResponse(error="There was an error creating the service provider. Please try again later.")
    except Exception as e:
        log.error("Unexpected error creating service provider", error=e)
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return ErrorResponse(error="There was an error creating the service provider")


@router.post(
    "/{service_provider_id}/review",
    responses={
        HTTPStatus.CREATED: {"model": ServiceProviderReview},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def add_service_provider_review(
    service_provider_id: UUID,
    review: NewServiceProviderReview,
    response: Response,
    user_id: UUID = Header(),
    db: Session = Depends(get_db),
) -> dict:

    try:
        new_review = ServiceProviderReviewRepository.new(service_provider_id, review, user_id, db)
        response.status_code = HTTPStatus.CREATED
        return ServiceProviderReview.from_orm(new_review)
    except FailedToCreateReview:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return ErrorResponse(error="There was an error creating the service provider review. Please try again later.")


@router.get(
    "/{service_provider_id}",
    responses={HTTPStatus.OK: {"model": ServiceProviderSchema}, HTTPStatus.NOT_FOUND: {"model": ErrorResponse}},
)
async def get_service_provider(
    service_provider_id: UUID,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:

    try:
        service_provider = ServiceProviderRepository.get(service_provider_id, db)
        return ServiceProviderSchema(**service_provider.as_dict())
    except ServiceProviderNotFound:
        response.status_code = HTTPStatus.NOT_FOUND
        return ErrorResponse(error="Service provider not found")


@router.put("/{service_provider_id}")
async def update_service_provider(service_provider_id: UUID) -> dict:
    pass


@router.delete("/{service_provider_id}")
async def delete_service_provider(service_provider_id: UUID) -> dict:
    pass
