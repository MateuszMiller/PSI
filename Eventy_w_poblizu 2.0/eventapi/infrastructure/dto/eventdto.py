"""A module containing DTO models for output events."""

from typing import Optional
from asyncpg import Record  # type: ignore
from pydantic import UUID4, BaseModel, ConfigDict, validator
from datetime import timezone, datetime
from eventapi.infrastructure.dto.locationdto import LocationDTO


class EventDTO(BaseModel):
    """A model representing DTO for airport data."""
    id: int
    name: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    location: LocationDTO
    max_participants: Optional[int] = None
    user_id: UUID4

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
    )

    @validator("start_time", "end_time", pre=True, always=True)
    def set_timezone(cls, value):
        if value is None:
            return None  # Obsługa braku daty
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    @classmethod
    def from_record(cls, record: Record) -> "EventDTO":
        record_dict = dict(record)

        # Logowanie danych lokalizacji
        print(f"Location mapping: {record_dict}")

        # Obsługa brakującego `location_name`
        location_name = record_dict.get("location_name")
        if location_name is None:
            raise ValueError("Location name is missing in the database record.")

        return cls(
            id=record_dict.get("id"),
            name=record_dict.get("name"),
            description=record_dict.get("description"),
            start_time=record_dict.get("start_time"),
            end_time=record_dict.get("end_time"),
            location=LocationDTO(
                id=record_dict.get("location_id"),
                name=location_name,
                latitude=record_dict.get("latitude"),
                longitude=record_dict.get("longitude"),
                address=record_dict.get("address"),
            ),
            max_participants=record_dict.get("max_participants"),
            user_id=record_dict.get("user_id"),
        )
