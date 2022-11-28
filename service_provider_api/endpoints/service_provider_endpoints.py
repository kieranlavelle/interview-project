from http import HTTPStatus

from fastapi import APIRouter

from service_provider_api.schemas.base import ErrorResponse
from service_provider_api.schemas.service_provider.service_provider import (
    ServiceProviderSchema,
)
from service_provider_api.schemas.service_provider.new_service_provider import (
    NewServiceProviderInSchema,
)

router = APIRouter("/service-provider")


@router.post(
    "",
    models={
        HTTPStatus.CREATED: {"model": ServiceProviderSchema},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def create_service_provider(provider: NewServiceProviderInSchema) -> dict:
    pass


@router.put("/{service_provider_id}")
async def update_service_provider(service_provider_id: str) -> dict:
    pass


@router.delete("/{service_provider_id}")
async def delete_service_provider(service_provider_id: str) -> dict:
    pass
