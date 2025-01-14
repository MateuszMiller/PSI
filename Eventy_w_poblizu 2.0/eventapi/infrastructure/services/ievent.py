"""Module containing event repository abstractions."""

from abc import ABC, abstractmethod
from typing import Iterable
from datetime import datetime
from eventapi.core.domain.event import Event, EventBroker


class IEventService(ABC):
    """An abstract class representing protocol of event repository."""

    @abstractmethod
    async def get_all_events(self) -> Iterable[Event]:
        """The abstract getting all events from the data storage.

        Returns:
            Iterable[Event]: Events in the data storage.
        """

    @abstractmethod
    async def get_by_id(self, event_id: int) -> Event | None:
        """The abstract getting event by provided id.

        Args:
            event_id (int): The id of the event.

        Returns:
            Event | None: The event details.
        """

    @abstractmethod
    async def get_by_location(
        self,
        location_id: int) -> Iterable[Event]:
        """The abstract getting events assigned to particular location.

        Args:
            location_id: (int): id of location
        Returns:
            Iterable[Event]: Events assigned to the location.
        """

    @abstractmethod
    async def get_by_date_range(
            self,
            start_date: datetime,
            end_date: datetime
    ) -> Iterable[Event]:
        """The abstract getting events within a date range.

        Args:
            start_date (datetime): Start date of the range.
            end_date (datetime): End date of the range.

        Returns:
            Iterable[Event]: Events in the specified range.
        """

    @abstractmethod
    async def get_by_user(self, user_id: int) -> Iterable[Event]:
        """The method getting events by user who added them.

        Args:
            user_id (int): The id of the user.

        Returns:
            Iterable[Event]: The event collection.
        """

    @abstractmethod
    async def get_recommended_events(
            self,
            latitude: float,
            longitude: float,
            radius: float
    ) -> Iterable[Event]:
        """The abstract adding a new event to the data storage.

                Args:
                    latitude (float): latitude of user
                    longitude (float): logtitute of user
                    radius (float): radius for location around user
                """

    @abstractmethod
    async def add_event(self, data: EventBroker) -> Event | None:
        """The abstract adding a new event to the data storage.

        Args:
            data (EventIn): The details of the new event.
        """

    @abstractmethod
    async def update_event(self, event_id: int, data: EventBroker) -> Event | None:
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

    @abstractmethod
    async def get_recommended_events(
            self,
            latitude: float,
            longitude: float,
            radius: float
    ) -> Iterable[Event]:
        """
        Retrieve recommended events based on location and radius.

        :param latitude: Latitude of the user location
        :param longitude: Longitude of the user location
        :param radius: Search radius in kilometers
        :return: List of recommended events
        """


