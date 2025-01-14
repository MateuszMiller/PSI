"""Module containing event repository abstractions."""

from abc import ABC, abstractmethod
from typing import Iterable, Any
from datetime import datetime
from eventapi.core.domain.event import EventBroker
from pydantic import UUID4

class IEventRepository(ABC):
    """An abstract class representing protocol of event repository."""

    @abstractmethod
    async def get_all_events(self) -> Iterable[Any]:
        """The abstract getting all events from the data storage.

        Returns:
            Iterable[Event]: Events in the data storage.
        """

    @abstractmethod
    async def get_by_id(self, event_id: int) -> Any | None:
        """The abstract getting event by provided id.

        Args:
            event_id (int): The id of the event.

        Returns:
            Event | None: The event details.
        """

    @abstractmethod
    async def get_by_location(
        self,
        location_id: int
    ) -> Iterable[Any]:
        """The abstract getting events by location.

        Args:
            location_id: ide of location

        Returns:
            Iterable[Any]: The result event collection.
        """

    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Iterable[Any]:
        """The abstract getting events within a date range.

        Args:
            start_date (datetime): Start date of the range.
            end_date (datetime): End date of the range.

        Returns:
            Iterable[Event]: Events in the specified range.
        """

    @abstractmethod
    async def add_event(self, data: EventBroker) -> Any | None:
        """The abstract adding a new event to the data storage.

        Args:
            data (EventIn): The details of the new event.
        """

    @abstractmethod
    async def update_event(self, event_id: int, data: EventBroker) -> Any | None:
        """The abstract updating event data in the data storage.

        Args:
            event_id (int): The id of the event.
            data (EventIn): The updated event details.

        Returns:
            Event | None: The updated event details.
        """

    @abstractmethod
    async def delete_event(self, event_id: int) -> bool:
        """The abstract removing an event from the data storage.

        Args:
            event_id (int): The id of the event.

        Returns:
            bool: Success of the operation.
        """
    async def get_by_user(self, user_id: UUID4) -> Iterable[Any]:
        """The method getting events by user who added them.

        Args:
            user_id (UUID4): The UUID of the user.

        Returns:
            Iterable[Event]: The event collection.
        """
