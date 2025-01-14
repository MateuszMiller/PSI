from pydantic import BaseModel, ConfigDict, UUID4
from typing import Optional
class ReviewIn(BaseModel):
    """Model representing location's DTO attributes."""

    content: Optional[str]
    rating: int
    event_id: int

class ReviewBroker(ReviewIn):
    """Broker class for handling user_id internally."""
    user_id: UUID4

class Review(ReviewIn):
    """Model representing location's attributes in the database."""
    id: int
    user_id: UUID4
    model_config = ConfigDict(from_attributes=True, extra="ignore")

