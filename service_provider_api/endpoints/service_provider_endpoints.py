from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Response, Header
from botocore.exceptions import ClientError

from service_provider_api.schemas.base import ErrorResponse
from service_provider_api.schemas.service_provider.service_provider import (
    ServiceProviderSchema,
)
from service_provider_api.schemas.service_provider.new_service_provider import (
    NewServiceProviderInSchema,
)
from service_provider_api.repositories.service_provider import (
    ServiceProviderRepository,
    ServiceProviderAlreadyExists,
)

router = APIRouter("/service-provider")


@router.post(
    "",
    models={
        HTTPStatus.CREATED: {"model": ServiceProviderSchema},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def create_service_provider(
    provider: NewServiceProviderInSchema, response: Response, user_id: UUID = Header()
) -> dict:

    try:
        new_service_provider = ServiceProviderRepository.new(provider, user_id)
        return ServiceProviderSchema(**new_service_provider.as_dict())
    except ServiceProviderAlreadyExists:
        response.status_code = HTTPStatus.CONFLICT
        return ErrorResponse(message="A service provider with that name already exists")
    except ClientError:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return ErrorResponse(message="There was an error creating the service provider")


@router.put("/{service_provider_id}")
async def update_service_provider(service_provider_id: str) -> dict:
    pass


@router.delete("/{service_provider_id}")
async def delete_service_provider(service_provider_id: str) -> dict:
    pass
