from uuid import uuid4

from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, DATERANGE
from sqlalchemy import Column, Integer, Float, String, ForeignKey

from service_provider_api.utils.database import Base


class ServiceProvider(Base):
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
        if len(self.review_rating):
            return sum(r.rating for r in self.review_rating) / len(self.review_rating)
        return 0.0

    def as_dict(self) -> dict:
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
    __tablename__ = "reviews"

    id = Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column("user_id", UUID(as_uuid=True), nullable=False)
    service_provider_id = Column(
        "service_provider_id", UUID(as_uuid=True), ForeignKey("service_providers.id")
    )
    rating = Column("rating", Float)


class Skills(Base):
    __tablename__ = "skills"

    id = Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4)
    service_provider_id = Column(
        "service_provider_id", UUID(as_uuid=True), ForeignKey("service_providers.id")
    )
    skill = Column("skill", String)


class Availability(Base):
    __tablename__ = "availability"

    id = Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4)
    service_provider_id = Column(
        "service_provider_id", UUID(as_uuid=True), ForeignKey("service_providers.id")
    )
    availability = Column("availability", DATERANGE)

    def as_dict(self) -> dict:
        return {
            "from_date": self.availability.lower,
            "to_date": self.availability.upper,
        }
