"""Module containing user-related domain models."""

from pydantic import BaseModel, ConfigDict, UUID4
from eventapi.api.utils.enums import UserRole

class UserIn(BaseModel):
    """Model representing user's DTO attributes."""
    username: str
    email: str
    password: str

class User(UserIn):
    """Model representing user's attributes in the database."""
    id: UUID4
    role: UserRole = UserRole.USER
    model_config = ConfigDict(from_attributes=True, extra="ignore")