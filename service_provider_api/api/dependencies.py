"""Module containing functions and classes that are used
as FastAPI dependencies."""

from typing import Optional
from datetime import date

from fastapi import Query
from pydantic.dataclasses import dataclass
from pydantic import root_validator, validator
from sqlalchemy.orm import Session

from service_provider_api.database.database import SessionLocal
from service_provider_api.core.utils import list_pairs


def get_db() -> Session:
    """Dependency used to inject a database session into a route.

    Returns:
        Session: A database session.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@dataclass
class ServiceProviderRecomendationParams:
    """A class used to represent the parameters used to filter recommended
    service providers.

    A class has been used as there are multiple parameters that need to be
    validated together & because there are a large number of parameters.

    Args:
        page (int, optional): The page number to return. Defaults to 1.
        page_size (int, optional): The number of results to return per page.
            Defaults to 10.
        expected_job_duration_in_days (int, optional): The expected duration
            of the job in days. Defaults to 1.
        job_budget_in_pence (int, optional): The maximum budget for the job.
        skills (list, optional): A list of skills that the service provider has.
        minimum_review_rating (float, optional): The minimum review rating.
    """

    page: int = Query(default=1, ge=1)
    page_size: int = Query(default=10, ge=1)
    expected_job_duration_in_days: int = Query(default=1, ge=1)
    job_budget_in_pence: int = Query(ge=1)
    skills: list[str] = Query()
    availability: list[date] = Query()
    minimum_review_rating: Optional[float] = Query(default=0, le=5, ge=0)

    # validate the availability ranges
    @validator("availability")
    def validate_availability_ranges(cls, v):

        if v is None:
            return v

        if len(v) % 2 != 0:
            raise ValueError("availability must be a csv list of tuples")

        for date_from, date_to in list_pairs(v):
            if date_from >= date_to:
                raise ValueError("date_from must come before date_to")

        return v


@dataclass
class ListFilterParams:
    """A class used to represent the parameters used to filter listed
    service providers.

    A class has been used as there are multiple parameters that need to be
    validated together & because there are a large number of parameters.

    Args:
        page (int, optional): The page number to return. Defaults to 1.
        page_size (int, optional): The number of results to return per page.
            Defaults to 10.

        reviews_lt (int, optional): The maximum average review of the service provider.
        reviews_gt (int, optional): The minimum average review of the service provider.
        name (str, optional): The name of the service provider to filter by.
        skills (list, optional): A list of skills that the service provider needs.
        cost_gt (int, optional): The minimum cost of the service provider.
        cost_lt (int, optional): The maximum cost of the service provider.
        availability (list, optional): A list of dates ranges that the service provider
            has to be available.
    """

    page: int = Query(default=1, ge=1)
    page_size: int = Query(default=10, ge=1)
    reviews_gt: float = Query(default=0, ge=0, le=5)
    reviews_lt: float = Query(default=5, le=5, ge=0)
    name: Optional[str] = None
    skills: Optional[list[str]] = Query(default=None)
    cost_gt: Optional[int] = None
    cost_lt: Optional[int] = None
    availability: Optional[list[date]] = Query(default=None)

    @root_validator
    def validate_cost_ranges(cls, values):
        cost_gt = values.get("cost_gt")
        cost_lt = values.get("cost_lt")
        if cost_gt is not None and cost_lt is not None:
            if cost_lt <= cost_gt:
                raise ValueError("cost_gt must be less than cost_lt")
        return values

    @root_validator
    def validate_review_ranges(cls, values):
        reviews_gt = values.get("reviews_gt")
        reviews_lt = values.get("reviews_lt")
        if reviews_lt <= reviews_gt:
            raise ValueError("reviews_gt must be less than reviews_lt")
        return values

    # validate the availability ranges
    @validator("availability")
    def validate_availability_ranges(cls, v):

        if v is None:
            return v

        if len(v) % 2 != 0:
            raise ValueError("availability must be a csv list of tuples")

        for date_from, date_to in list_pairs(v):
            if date_from >= date_to:
                raise ValueError("date_from must come before date_to")

        return v
