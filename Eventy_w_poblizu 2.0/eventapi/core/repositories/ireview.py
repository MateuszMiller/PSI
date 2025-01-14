"""Module containing event repository abstractions."""

from abc import ABC, abstractmethod
from typing import Iterable, Any
from datetime import datetime
from eventapi.core.domain.review import Review, ReviewIn
from pydantic import UUID4


class IReviewRepository(ABC):
    """An abstract class representing protocol of event repository."""

    @abstractmethod
    async def get_all_reviews(self) -> Iterable[Any]:
        """The abstract getting all reviews from the data storage.

        Returns:
            Iterable[Any]: Reviews in the data storage.
        """

    @abstractmethod
    async def get_by_id(self, review_id: int) -> Any | None:
        """The abstract getting review by provided id.

        Args:
            review_id (int): The id of the review.

        Returns:
            Any | None: The review details.
        """

    @abstractmethod
    async def get_by_rating(self, rating: int) -> Any | None:
        """The abstract getting review by rating.

        Args:
            rating (int): The rating.

        Returns:
            Any | None: All rating provided.
        """

    @abstractmethod
    async def get_by_user(self, user: UUID4) -> Iterable[Any]:
        """The abstract getting reviews placed by particular user.

        Args:
            user UUID1: user whose reviews we want to see

        Returns:
            Iterable[Any]: Reviews by provided user
        """

    @abstractmethod
    async def get_by_event_id(self, event_id: int) -> Iterable[Any]:
        """The abstract getting reviews of particular event.

        Args:
            event_id (int): event witch reviews we want to see

        Returns:
            Iterable[Any]: Reviews by event
        """

    @abstractmethod
    async def add_review(self, data: ReviewIn) -> Any | None:do
        """The abstract adding a new event to the data storage.

        Args:
            data (EventIn): The details of the new event.
        """

    @abstractmethod
    async def update_review(self, review_id: int, data: ReviewIn) -> Any | None:
        """The abstract updating event data in the data storage.

        Args:
            review_id (int): The id of the review.
            data (ReviewIn): The updated review details.

        Returns:
            Any | None: The updated review details.
        """

    @abstractmethod
    async def delete_review(self, review_id: int) -> bool:
        """The abstract removing an event from the data storage.

        Args:
            review_id (int): The id of the event.

        Returns:
            bool: Success of the operation.
        """
