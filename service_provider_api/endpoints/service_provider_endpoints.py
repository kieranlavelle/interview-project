from http import HTTPStatus
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.orm import Session

from service_provider_api.dependencies import get_db
from service_provider_api.repositories.service_provider import FailedToCreateServiceProvider, ServiceProviderRepository
from service_provider_api.schemas.base import ErrorResponse
from service_provider_api.schemas.service_provider.new_service_provider import NewServiceProviderInSchema
from service_provider_api.schemas.service_provider.service_provider import ServiceProviderSchema

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


@router.put("/{service_provider_id}")
async def update_service_provider(service_provider_id: str) -> dict:
    pass


@router.delete("/{service_provider_id}")
async def delete_service_provider(service_provider_id: str) -> dict:
    pass
