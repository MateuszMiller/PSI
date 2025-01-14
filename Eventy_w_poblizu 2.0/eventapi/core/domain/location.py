"""Module containing location-related domain models."""

from pydantic import BaseModel, ConfigDict
from typing import Optional


class LocationIn(BaseModel):
    """Model representing location's DTO attributes."""
    name: str
    latitude: float
    longitude: float
    address: Optional[str] = None


class Location(LocationIn):
    """Model representing location's attributes in the database."""
    id: int

    model_config = ConfigDict(from_attributes=True, extra="ignore")
