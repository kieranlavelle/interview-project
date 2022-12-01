"""Module containing functions and classes that are used
as FastAPI dependencies."""

from typing import Optional
from datetime import date

from fastapi import Query
from pydantic.dataclasses import dataclass
from pydantic import root_validator, validator
from sqlalchemy.orm import Session

from service_provider_api.database.database import SessionLocal


def get_db() -> Session:
    """Dependency used to inject a database session into a route.

    Returns:
        Session: A database session.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
