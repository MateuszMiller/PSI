"""A module containing DTO models for country."""


from pydantic import BaseModel, ConfigDict  # type: ignore
from typing import Optional
from eventapi.core.domain.location import Location


class LocationDTO(BaseModel):
    """A model representing DTO for location data."""
    name: str
    latitude: float
    longitude: float
    address: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
    )