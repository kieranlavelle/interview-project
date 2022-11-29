from typing import Optional
from datetime import date
import itertools

from fastapi import Query
from pydantic.dataclasses import dataclass
from pydantic import Field, root_validator, validator

from service_provider_api.utils.database import SessionLocal


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def list_pairs(sequence):
    if not sequence:
        return []
    it = iter(sequence)
    return zip(it, it)


@dataclass
class ServiceProviderRecomendationParams:
    page: int = Query(default=1, ge=1)
    page_size: int = Query(default=10, ge=1)
    expected_job_duration_in_days: int = Query(default=1, ge=1)
    job_budget_in_pence: int = Query(ge=1)
    skills: list[str] = Query()
    availability: list[date] = Query()
    minimum_review_rating: Optional[float] = Query(default=5, le=5, ge=0)

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
