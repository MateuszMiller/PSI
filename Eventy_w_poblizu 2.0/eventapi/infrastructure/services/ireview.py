from abc import ABC, abstractmethod
from typing import Iterable, Any
from eventapi.core.domain.review import Review, ReviewIn
from pydantic import UUID4


class IReviewService(ABC):
    """Abstract interface for review-related services."""

    @abstractmethod
    async def get_all_reviews(self) -> Iterable[Review]:
        """Retrieve all reviews."""

    @abstractmethod
    async def get_review_by_id(self, review_id: int) -> Review | None:
        """Retrieve a specific review by ID."""

    @abstractmethod
    async def get_reviews_by_user(self, user_id: UUID4) -> Iterable[Review]:
        """Retrieve all reviews created by a specific user."""

    @abstractmethod
    async def get_reviews_by_event(self, event_id: int) -> Iterable[Review]:
        """Retrieve all reviews associated with a specific event."""

    @abstractmethod
    async def get_reviews_by_rating(self, rating: int) -> Iterable[Review]:
        """Retrieve all reviews with a specific rating."""

    @abstractmethod
    async def create_review(self, data: ReviewIn) -> Review:
        """Create a new review."""

    @abstractmethod
    async def update_review(self, review_id: int, data: ReviewIn) -> Review | None:
        """Update an existing review."""

    @abstractmethod
    async def delete_review(self, review_id: int) -> bool:
        """Delete a review."""