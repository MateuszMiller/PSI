from typing import Iterable, Any
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException, status
from eventapi.core.domain.review import Review, ReviewIn
from eventapi.core.repositories.ireview import IReviewRepository
from eventapi.db import review_table, event_table, database


class ReviewRepository(IReviewRepository):
    """A class representing the review DB repository."""

    async def get_all_reviews(self) -> Iterable[Any]:
        """Retrieve all reviews."""
        query = select(review_table)
        reviews = await database.fetch_all(query)
        return [Review(**dict(row)) for row in reviews]

    async def get_by_id(self, review_id: int) -> Review | None:
        """Retrieve a review by its ID."""
        query = select(review_table).where(review_table.c.id == review_id)
        review = await database.fetch_one(query)
        return Review(**dict(review)) if review else None

    async def get_by_rating(self, rating: int) -> Iterable[Any]:
        """Retrieve reviews with a specific rating."""
        query = select(review_table).where(review_table.c.rating == rating)
        reviews = await database.fetch_all(query)
        return [Review(**dict(row)) for row in reviews]

    async def get_by_user(self, user_id: str) -> Iterable[Any]:
        """Retrieve reviews created by a specific user."""
        query = select(review_table).where(review_table.c.user_id == user_id)
        reviews = await database.fetch_all(query)
        return [Review(**dict(row)) for row in reviews]

    async def get_by_event_id(self, event_id: int) -> Iterable[Any]:
        """Retrieve reviews associated with a specific event."""
        # Log the incoming event_id for debugging
        print(f"[DEBUG] Fetching reviews for event_id: {event_id} (type: {type(event_id)})")

        # Correct the query to filter by event_id
        query = select(review_table).where(review_table.c.event_id == event_id)
        print(f"[DEBUG] SQL Query: {query}")

        # Execute the query and log raw results
        reviews = await database.fetch_all(query)
        print(f"[DEBUG] Raw results from DB: {reviews}")

        # Check if no reviews were found
        if not reviews:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No reviews found for event with ID {event_id}",
            )

        # Map results to Review objects and log them
        mapped_reviews = [Review(**dict(row)) for row in reviews]
        print(f"[DEBUG] Mapped reviews: {mapped_reviews}")

        return mapped_reviews

    async def add_review(self, data: ReviewIn) -> Review | None:
        # Validate event_id exists directly in this method
        query = select(event_table).where(event_table.c.id == data.event_id)
        event = await database.fetch_one(query)
        if not event:
            raise HTTPException(status_code=400, detail="Invalid event_id")

        # Validate rating
        if data.rating < 1:
            raise HTTPException(status_code=400, detail="Rating must be greater than or equal to 1")

        # Insert the review into the database
        query = review_table.insert().values(
            content=data.content,
            rating=data.rating,
            event_id=data.event_id,
            user_id=data.user_id,
        ).returning(review_table)
        review_id = await database.execute(query)
        return await self.get_by_id(review_id)

    async def update_review(self, review_id: int, data: ReviewIn) -> Review | None:
        """Update an existing review."""
        query = (
            review_table.update()
            .where(review_table.c.id == review_id)
            .values(
                content=data.content,
                rating=data.rating,
                event_id=data.event_id,
            )
        )
        await database.execute(query)
        return await self.get_by_id(review_id)

    async def delete_review(self, review_id: int) -> bool:
        """Delete a review."""
        query = review_table.delete().where(review_table.c.id == review_id)
        await database.execute(query)
        return True
