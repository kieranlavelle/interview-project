"""Module to hold all of the endpoints that return collections of
service providers."""

from http import HTTPStatus

import structlog
from fastapi import APIRouter, Depends, Query
from fastapi_versioning import version
from sqlalchemy.orm import Session

from service_provider_api.api import schemas
from service_provider_api.api.dependencies import (
    get_db,
)
from service_provider_api.core.repositories.service_provider import (
    ServiceProviderRepository,
)

router = APIRouter(prefix="/service-providers")
log = structlog.get_logger()


@router.post("/", responses={HTTPStatus.OK: {"model": schemas.ServiceProviderSchema}})
@version(1, 0)
def search_service_provider(
    params: schemas.ServiceProviderListFilterParams,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> dict:
    """Endpoint to search for service providers.

    Args:
        params (ListFilterParams): The body used to filter the search.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the service providers that matched
        the filters provided by the user in the `params` argument.
    """

    log.info("Searching for service providers", params=params)
    service_providers = ServiceProviderRepository.list(db, params, page, page_size)
    return schemas.ServiceProvidersList(
        service_providers=[s.as_dict() for s in service_providers]
    )


@router.post(
    "/recommend", responses={HTTPStatus.OK: {"model": schemas.ServiceProviderSchema}}
)
@version(1, 0)
def recommend_service_provider(
    params: schemas.ServiceProviderRecommendationParams,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> dict:
    """Endpoint to recommend a service provider based on filters.

    Args:
        params (ServiceProviderRecommendationParams): The request body used
            to filter the search.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the service provider that matched
        the filters provided by the user in the `params` argument. This is
        ordered according to the most relevant service provider first.
    """

    log.info("Searching for recommended service providers", params=params)

    max_cost_per_day = params.job_budget_in_pence / params.expected_job_duration_in_days
    filters = schemas.ServiceProviderListFilterParams(
        reviews_gt=params.minimum_review_rating,
        skills=params.skills,
        cost_lt=max_cost_per_day,
        availability=params.availability,
    )

    service_providers = ServiceProviderRepository.list(db, filters, page, page_size)
    return schemas.ServiceProvidersList(
        service_providers=[s.as_dict() for s in service_providers]
    )
