from http import HTTPStatus

import structlog
from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlalchemy.orm import Session

from service_provider_api.dependencies import (
    get_db,
    ListFilterParams,
    ServiceProviderRecomendationParams,
)
from service_provider_api.repositories.service_provider import (
    ServiceProviderRepository,
)
from service_provider_api import schemas

router = APIRouter(prefix="/service-providers")
log = structlog.get_logger()


@router.get("/", responses={HTTPStatus.OK: {"model": schemas.ServiceProviderSchema}})
@version(1, 0)
async def search_service_provider(
    params: ListFilterParams = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    log.info("Searching for service providers", params=params)
    service_providers = ServiceProviderRepository.list(db, params)
    return schemas.ServiceProvidersList(
        service_providers=[s.as_dict() for s in service_providers]
    )


@router.get(
    "/recommend", responses={HTTPStatus.OK: {"model": schemas.ServiceProviderSchema}}
)
@version(1, 0)
async def recommend_service_provider(
    params: ServiceProviderRecomendationParams = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    log.info("Searching for recommended service providers", params=params)

    max_cost_per_day = params.job_budget_in_pence / params.expected_job_duration_in_days
    filters = ListFilterParams(
        page=params.page,
        page_size=params.page_size,
        reviews_gt=params.minimum_review_rating,
        skills=params.skills,
        cost_lt=max_cost_per_day,
        availability=params.availability,
    )

    service_providers = ServiceProviderRepository.list(db, filters)
    return schemas.ServiceProvidersList(
        service_providers=[s.as_dict() for s in service_providers]
    )
