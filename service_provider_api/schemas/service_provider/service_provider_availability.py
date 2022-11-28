from datetime import date

from service_provider_api.schemas.base import BaseSchema
from pydantic import root_validator


class ServiceProviderAvailabilitySchema(BaseSchema):
    """Availability of a service provider"""

    from_date: date
    to_date: date

    @root_validator
    def validate_dates(cls, values: dict) -> dict:
        """Checks that the from date is before the to date."""

        # pydatinc will validate that these exist, and are dates
        from_date = values.get("from_date")
        to_date = values.get("to_date")

        if from_date > to_date:
            raise ValueError("From date must be before to date.")

        return values
