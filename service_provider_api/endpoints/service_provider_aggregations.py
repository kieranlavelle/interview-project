from http import HTTPStatus

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from service_provider_api.dependencies import get_db, ListFilterParams, ServiceProviderRecomendationParams
from service_provider_api.repositories.service_provider import (
    ServiceProviderRepository,
)
from service_provider_api import schemas

router = APIRouter(prefix="/service-providers")
log = structlog.get_logger()


@router.get("/list", responses={HTTPStatus.OK: {"model": schemas.ServiceProviderSchema}})
async def search_service_provider(
    params: ListFilterParams = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    log.info("Searching for service providers", params=params)
    service_providers = ServiceProviderRepository.list(db, params)
    return schemas.ServiceProvidersList(service_providers=[s.as_dict() for s in service_providers])


@router.get("/recommend", responses={HTTPStatus.OK: {"model": schemas.ServiceProviderSchema}})
async def search_service_provider(
    params: ServiceProviderRecomendationParams = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    log.info("Searching for recommended service providers", params=params)
    service_providers = ServiceProviderRepository.list(db, params)
    return schemas.ServiceProvidersList(service_providers=[s.as_dict() for s in service_providers])
