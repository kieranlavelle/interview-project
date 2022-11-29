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
