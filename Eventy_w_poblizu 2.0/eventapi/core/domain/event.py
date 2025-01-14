"""Module containing event-related domain models."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, UUID4


class EventIn(BaseModel):
    """Model representing event's DTO attributes."""
    name: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    location_id: Optional[int] = None
    max_participants: Optional[int] = None


class EventBroker(EventIn):
    """A broker class including user in the model."""
    user_id: UUID4


class Event(EventIn):
    """Model representing event's attributes in the database."""
    id: int

    model_config = ConfigDict(from_attributes=True, extra="ignore")
