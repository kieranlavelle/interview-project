"""Module to hold all of the endpoints that return collections of
service providers."""

from http import HTTPStatus

import structlog
from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlalchemy.orm import Session

from service_provider_api.api import schemas
from service_provider_api.api.dependencies import (
    ListFilterParams,
    ServiceProviderRecommendationParams,
    get_db,
)
from service_provider_api.core.repositories.service_provider import (
    ServiceProviderRepository,
)

router = APIRouter(prefix="/service-providers")
log = structlog.get_logger()


@router.get("/", responses={HTTPStatus.OK: {"model": schemas.ServiceProviderSchema}})
@version(1, 0)
def search_service_provider(
    params: ListFilterParams = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    """Endpoint to search for service providers.

    Args:
        params (ListFilterParams): The query parameters to filter the search.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the service providers that matched
        the filters provided by the user in the `params` argument.
    """

    log.info("Searching for service providers", params=params)
    service_providers = ServiceProviderRepository.list(db, params)
    return schemas.ServiceProvidersList(
        service_providers=[s.as_dict() for s in service_providers]
    )


@router.get(
    "/recommend", responses={HTTPStatus.OK: {"model": schemas.ServiceProviderSchema}}
)
@version(1, 0)
def recommend_service_provider(
    params: ServiceProviderRecommendationParams = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    """Endpoint to recommend a service provider based on filters.

    Args:
        params (ServiceProviderRecommendationParams): The query parameters to
            filter the search by.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the service provider that matched
        the filters provided by the user in the `params` argument. This is
        ordered according to the most relevant service provider first.
    """

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
