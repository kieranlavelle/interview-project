from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ServiceProviderAvailabilityRange(BaseModel):
    """Availability of a service provider"""

    from_date: datetime
    to_date: datetime

    def as_dict(self) -> dict:
        return {
            "from_date": self.from_date,
            "to_date": self.to_date,
        }


class ServiceProviderModel(BaseModel):
    """Service provider model.

    A service provider is a person or company that provides a service. This class
    exposes a method to convert the model to a dictionary, which is formatted for
    displaying data on the front end.
    """

    id: UUID
    name: str
    skills: list[str]
    cost_in_pence: int
    availability: list[ServiceProviderAvailabilityRange]
    review_rating: float

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "skills": self.skills,
            "cost_in_pence": self.cost_in_pence,
            "availability": [dates.as_dict() for dates in self.availability],
            "review_rating": self.review_rating,
        }
