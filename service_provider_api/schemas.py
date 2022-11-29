from uuid import UUID
from datetime import date

import orjson
from pydantic import validator, root_validator, BaseModel


class BaseSchema(BaseModel):
    class Config:
        def orjson_dumps(v, *, default):
            # orjson.dumps returns bytes, to match standard json.dumps we need to decode
            return orjson.dumps(v, default=default).decode()

        orm_mode = True
        arbitrary_types_allowed = True
        json_dumps = orjson_dumps
        allow_population_by_field_name = True


class ErrorResponse(BaseSchema):
    error: str


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


class NewServiceProviderInSchema(BaseSchema):
    """Schema for new service provider requests."""

    name: str
    skills: list[str]
    cost_in_pence: int
    availability: list[ServiceProviderAvailabilitySchema]


class ServiceProviderSchema(BaseSchema):
    """Schema for new service provider requests."""

    id: UUID
    name: str
    skills: list[str]
    cost_in_pence: int
    availability: list[ServiceProviderAvailabilitySchema]
    review_rating: float


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
