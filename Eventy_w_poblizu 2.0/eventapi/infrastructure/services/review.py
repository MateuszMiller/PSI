from typing import Iterable
from eventapi.core.domain.review import Review, ReviewIn
from eventapi.core.repositories.ireview import IReviewRepository
from eventapi.infrastructure.services.ireview import IReviewService
from pydantic import UUID4


class ReviewService(IReviewService):
    """Concrete implementation of IReviewService."""

    def __init__(self, repository: IReviewRepository):
        """Initialize the service with a review repository."""
        self.review_repository = repository

    async def get_all_reviews(self) -> Iterable[Review]:
        """Retrieve all reviews."""
        return await self.review_repository.get_all_reviews()

    async def get_review_by_id(self, review_id: int) -> Review | None:
        """Retrieve a specific review by ID."""
        return await self.review_repository.get_by_id(review_id)

    async def get_reviews_by_user(self, user_id: UUID4) -> Iterable[Review]:
        """Retrieve all reviews created by a specific user."""
        return await self.review_repository.get_by_user(user_id)

    async def get_reviews_by_event(self, event_id: int) -> Iterable[Review]:
        """Retrieve all reviews associated with a specific event."""
        return await self.review_repository.get_by_event_id(event_id)

    async def get_reviews_by_rating(self, rating: int) -> Iterable[Review]:
        """Retrieve all reviews with a specific rating."""
        return await self.review_repository.get_by_rating(rating)

    async def create_review(self, data: ReviewIn) -> Review:
        """Create a new review."""
        return await self.review_repository.add_review(data)

    async def update_review(self, review_id: int, data: ReviewIn) -> Review | None:
        """Update an existing review."""
        return await self.review_repository.update_review(review_id, data)

    async def delete_review(self, review_id: int) -> bool:
        """Delete a review."""
        return await self.review_repository.delete_review(review_id)