"""This module holds all of the Database models used by SQLAlchemy.

These models also act as the data models for the application.
"""

from uuid import uuid4

from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import DATERANGE, UUID
from sqlalchemy.orm import relationship

from service_provider_api.database.database import Base


class ServiceProvider(Base):
    """Model for a service provider.

    This model represents the service provider in the database.
    It's also used as the data model for the application.

    Attributes:
        id (UUID): The ID of the service provider.
        user_id (UUID): The ID of the user who created the service provider.
        name (str): The name of the service provider.
        cost_in_pence (int): The cost of the service provider in pence.
        skills (List[ServiceProviderSkill]): The skills of the service provider.
        availability (List[ServiceProviderAvailability]): The availability of the service provider.
        review_rating (List[ServiceProviderReviewRating]): The review ratings of the service provider.
    """

    __tablename__ = "service_providers"

    id = Column("id", UUID(as_uuid=True), primary_key=True)
    user_id = Column("user_id", UUID(as_uuid=True), nullable=False)
    name = Column("name", String)
    cost_in_pence = Column("cost_in_pence", Integer)

    skills = relationship(
        "Skills", backref="service_provider", cascade="all, delete-orphan"
    )
    availability = relationship(
        "Availability", backref="service_provider", cascade="all, delete-orphan"
    )
    review_rating = relationship(
        "Reviews", backref="service_provider", cascade="all, delete-orphan"
    )

    def _calculate_review_rating(self) -> float:
        """Calculate the average review rating for the service provider.

        Args:
            None

        Returns:
            float: The average review rating for the service provider.
        """

        if len(self.review_rating):
            return sum(r.rating for r in self.review_rating) / len(self.review_rating)
        return 0.0

    def as_dict(self) -> dict:
        """Return the service provider as a dictionary.

        This representation is used for logging, and for passing
        the model into the API response. It transforms the SQLAlchemy
        model into a dictionary and does some calculations to get
        the average review rating.

        Args:
            None

        Returns:
            dict: The service provider as a dictionary.
        """

        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "cost_in_pence": self.cost_in_pence,
            "skills": [skill.skill for skill in self.skills],
            "availability": [
                availability.as_dict() for availability in self.availability
            ],
            "review_rating": self._calculate_review_rating(),
        }


class Reviews(Base):
    """Model to hold a review for a service provider.

    Attributes:
        id (UUID): The ID of the review.
        service_provider_id (UUID): The ID of the service provider being reviewed.
        user_id (UUID): The ID of the user who created the review.
        rating (float): The rating of the service provider.
    """

    __tablename__ = "reviews"

    id = Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column("user_id", UUID(as_uuid=True), nullable=False)
    service_provider_id = Column(
        "service_provider_id", UUID(as_uuid=True), ForeignKey("service_providers.id")
    )
    rating = Column("rating", Float)


class Skills(Base):
    """Model to hold a skill for a service provider.

    Attributes:
        id (UUID): The ID of the skill.
        service_provider_id (UUID): The ID of the service provider who has the skill.
        skill (str): The skill of the service provider.
    """

    __tablename__ = "skills"

    id = Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4)
    service_provider_id = Column(
        "service_provider_id", UUID(as_uuid=True), ForeignKey("service_providers.id")
    )
    skill = Column("skill", String)


class Availability(Base):
    """Model to hold the availability of a service provider.

    Attributes:
        id (UUID): The ID of the availability.
        service_provider_id (UUID): The ID of the service provider who has the availability.
        availability (DATERANGE): The availability of the service provider.
    """

    __tablename__ = "availability"

    id = Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4)
    service_provider_id = Column(
        "service_provider_id", UUID(as_uuid=True), ForeignKey("service_providers.id")
    )
    availability = Column("availability", DATERANGE)

    def as_dict(self) -> dict:
        """Return the availability as a dictionary.

        Transforms the postgres DATERANGE into a dictionary.

        Args:
            None

        Returns:
            dict: The availability as a dictionary.
        """

        return {
            "from_date": self.availability.lower,
            "to_date": self.availability.upper,
        }
