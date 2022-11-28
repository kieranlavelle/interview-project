"""Module to contain schemas for new service provider requests."""

from pydantic import validator

from service_provider_api.schemas.base import BaseSchema
from service_provider_api.schemas.service_provider.service_provider_availability import (
    ServiceProviderAvailabilitySchema,
)


class NewServiceProviderInSchema(BaseSchema):
    """Schema for new service provider requests."""

    name: str
    skills: list[str]
    cost_in_pence: int
    availability: list[ServiceProviderAvailabilitySchema]
    review_rating: float

    @validator("review_rating")
    def validate_rating_is_between_0_and_5(cls, value: float) -> float:
        """Validate that the review rating is between 0 and 5."""
        if value < 0 or value > 5:
            raise ValueError("Review rating must be between 0 and 5.")
        return value
