from uuid import UUID
from datetime import date

import orjson
from pydantic import validator, root_validator, BaseModel


class BaseSchema(BaseModel):
    """A base schema class that all other schemas inherit from.

    Contains some useful config such as the JSON encoder that can appropriately
    encode UUIDs & dates.
    """

    class Config:
        def orjson_dumps(v, *, default):
            # orjson.dumps returns bytes, to match standard json.dumps we need to decode
            return orjson.dumps(v, default=default).decode()

        orm_mode = True
        arbitrary_types_allowed = True
        json_dumps = orjson_dumps
        allow_population_by_field_name = True


class ErrorResponse(BaseSchema):
    """A schema used to represent an error response.

    This schema is consistently used throughout the API to represent errors.
    This should allow for easy parsing of errors by clients.

    Args:
        error (str): The error message.
    """

    error: str


class ServiceProviderAvailabilitySchema(BaseSchema):
    """Availability of a service provider

    Validates that the start date is before the end date and
    that valid iso dates are provided.

    Args:
        from_date (date): The start date of the availability.
        to_date (date): The end date of the availability.
    """

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


class NewServiceProviderInSchema(BaseSchema):
    """Schema for new service provider requests.

    This schema is used to validate the request body of the
    POST & PUT service-provider endpoints.

    Args:
        name (str): The name of the service provider.
        skills (list): A list of skills that the service provider has.
        cost_in_pence (int): The cost of the service provider per day.
        availability (list): A list of availability ranges that the service provider
            has.
    """

    name: str
    skills: list[str]
    cost_in_pence: int
    availability: list[ServiceProviderAvailabilitySchema]


class ServiceProviderSchema(BaseSchema):
    """Schema for service provider that has been inserted into the DB.

    Args:
        id (UUID): The ID of the service provider.
        name (str): The name of the service provider.
        skills (list): A list of skills that the service provider has.
        cost_in_pence (int): The cost of the service provider per day.
        availability (list): A list of availability ranges that the service provider
            has.
        review_rating (float): The average review rating of the service provider.
    """

    id: UUID
    name: str
    skills: list[str]
    cost_in_pence: int
    availability: list[ServiceProviderAvailabilitySchema]
    review_rating: float


class NewServiceProviderReview(BaseSchema):
    """Schema for new service provider review requests.

    Validates that the rating is between 0 and 5.

    Args:
        rating (float): The rating of the service provider.
    """

    rating: float

    @validator("rating")
    def rating_must_be_between_0_and_5(cls, v):
        """Checks that the rating is between 0 and 5."""
        if v < 0 or v > 5:
            raise ValueError("Rating must be between 0 and 5")
        return v


class ServiceProviderReview(BaseSchema):
    """Response schema for new service provider review.

    Represents a review that has been inserted into the DB.

    Args:
        rating (float): The rating given for the service provider.
        user_id (UUID): The ID of the user that created the review.
    """

    rating: float
    user_id: UUID


class ServiceProvidersList(BaseSchema):
    """Schema for a list of service providers.

    Args:
        service_providers (list): A list of service providers.
    """

    service_providers: list[ServiceProviderSchema]
