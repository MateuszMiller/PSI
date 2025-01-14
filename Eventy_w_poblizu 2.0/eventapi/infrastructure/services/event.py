"""Module containing continent service implementation."""

from typing import Iterable
from datetime import timezone, datetime

from eventapi.core.domain.event import Event, EventBroker
from eventapi.core.repositories.ievent import IEventRepository
from eventapi.infrastructure.services.ievent import IEventService
from geopy.distance import geodesic

class EventService(IEventService):
    """A class implementing the airport service."""

    _repository: IEventRepository

    def __init__(self, repository: IEventRepository) -> None:
        """The initializer of the `event service`.

        Args:
            repository (IEventRepository): The reference to the repository.
        """

        self._repository = repository

    async def get_all_events(self) -> Iterable[Event]:
        """The method getting all events from the repository.

        Returns:
            Iterable[Event]: All events.
        """

        return await self._repository.get_all_events()

    async def get_by_id(self, event_id: int) -> Event | None:
        """The abstract getting event by provided id.

        Args:
            event_id (int): The id of the event.

        Returns:
            Event | None: The event details.
        """

        return await self._repository.get_by_id(event_id)

    async def get_by_location(self, location_id: int) -> Iterable[Event]:
        """The method getting events by raduis of the provided location.

        Args:
            location_id: int: id of location

        Returns:
            Iterable[Event]: The result event collection.
        """

        return await self._repository.get_by_location(location_id)

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
        return await self._repository.get_by_date_range(start_date, end_date)

    async def get_recommended_events(
            self,
            latitude: float,
            longitude: float,
            radius: float
    ) -> Iterable[Event]:
        """Retrieve recommended events based on location and radius."""
        events = await self._repository.get_all_events()

        user_location = (latitude, longitude)
        recommended_events = []

        for event in events:
            if event.location.latitude is not None and event.location.longitude is not None:
                event_location = (event.location.latitude, event.location.longitude)
                distance = geodesic(user_location, event_location).kilometers

                if distance <= radius:
                    recommended_events.append(event)

        return recommended_events

    async def add_event(self, data: EventBroker) -> None:
        """The method adding a new event to the repository.

        Args:
            data (EventBroker): The details of the new event.
        """
        data.start_time = data.start_time.replace(
            tzinfo=timezone.utc) if data.start_time.tzinfo is None else data.start_time.astimezone(timezone.utc)
        data.end_time = data.end_time.replace(
            tzinfo=timezone.utc) if data.end_time.tzinfo is None else data.end_time.astimezone(timezone.utc)

        return await self._repository.add_event(data)



    async def update_event(self, event_id: int, data: EventBroker) -> Event | None:
        """The abstract updating event data in the data storage.

        Args:
            event_id (int): The id of the event.
            data (EventIn): The updated event details.

        Returns:
            Event | None: The updated event details.
        """
        return await self._repository.update_event(event_id, data)

    async def delete_event(self, event_id: int) -> bool:
        """The abstract removing an event from the data storage.

        Args:
            event_id (int): The id of the event.

        Returns:
            bool: Success of the operation.
        """
        return await self._repository.delete_event(event_id)

    async def get_by_user(self, user_id: int) -> Iterable[Event]:
        """The method getting events by user who added them.

        Args:
            user_id (int): The id of the user.

        Returns:
            Iterable[Event]: The event collection.
        """
        return await self._repository.get_by_user(user_id)

