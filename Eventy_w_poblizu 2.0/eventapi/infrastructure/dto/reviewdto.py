from pydantic import BaseModel, ConfigDict, UUID4, Field
from typing import Optional
from asyncpg import Record


class ReviewDTO(BaseModel):
    """Model representing a DTO for reviews."""
    id: int
    content: Optional[str]
    rating: int = Field(..., ge=1, le=5)
    event_id: int
    user_id: UUID4

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
    )

    @classmethod
    def from_record(cls, record: Record) -> "ReviewDTO":
        """Create a ReviewDTO from a database record."""
        record_dict = dict(record)

        missing_fields = []
        for field in ["id", "rating", "event_id", "user_id",]:
            if record_dict.get(field) is None:
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(f"Missing required fields for ReviewDTO: {', '.join(missing_fields)}")

        return cls(
            id=record_dict["id"],
            content=record_dict.get("content"),
            rating=record_dict["rating"],
            event_id=record_dict["event_id"],
            user_id=record_dict["user_id"],
        )