from uuid import UUID

from pydantic import validator

from service_provider_api.schemas.base import BaseSchema


class NewServiceProviderReview(BaseSchema):
    """Schema for new service provider review requests."""

    rating: float

    @validator("rating")
    def rating_must_be_between_0_and_5(cls, v):
        if v < 0 or v > 5:
            raise ValueError("Rating must be between 0 and 5")
        return v


class ServiceProviderReview(BaseSchema):
    """Schema for new service provider review requests."""

    rating: float
    user_id: UUID
