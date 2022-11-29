from uuid import UUID

from service_provider_api.schemas.base import BaseSchema
from service_provider_api.schemas.service_provider.service_provider_availability import (
    ServiceProviderAvailabilitySchema,
)


class ServiceProviderSchema(BaseSchema):
    """Schema for new service provider requests."""

    id: UUID
    name: str
    skills: list[str]
    cost_in_pence: int
    availability: list[ServiceProviderAvailabilitySchema]
    review_rating: list
