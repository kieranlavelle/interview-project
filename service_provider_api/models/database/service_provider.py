from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, A
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
)

Model = declarative_base(name="Model")


class ServiceProviderDBModel(Model):
    __tablename__ = "service_providers"
    id = Column("id", UUID, primary_key=True)
    name = Column("name", String)
    cost_in_pence = Column("cost_in_pence", Integer)
    review_rating = Column("review_rating", Float)


class ServiceProvideSkillsDBModel(Model):
    __tablename__ = "service_provider_skills"
    id = Column("id", UUID, primary_key=True)
    service_provider_id = Column(
        "service_provider_id", UUID, ForeignKey("service_providers.id")
    )
    skill = Column("skill", String)


class ServiceProviderAvailabilityDBModel(Model):
    __tablename__ = "service_provider_availability"
    id = Column("id", UUID, primary_key=True)
    service_provider_id = Column(
        "service_provider_id", UUID, ForeignKey("service_providers.id")
    )
    from_date = Column("from_date", DateTime)
    to_date = Column("to_date", DateTime)
