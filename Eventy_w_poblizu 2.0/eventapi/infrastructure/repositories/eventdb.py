"""Module containing airport repository implementation."""
from datetime import timezone, datetime
from typing import Any, Iterable
from pydantic import UUID4
from asyncpg import Record  # type: ignore
from sqlalchemy import select, join, and_, or_
from fastapi import HTTPException
from sqlalchemy.sql import func

from eventapi.core.repositories.ievent import IEventRepository
from eventapi.core.domain.event import Event, EventBroker
from eventapi.db import (
    event_table,
    location_table,
    review_table,
    user_table,
    database,
)
from eventapi.infrastructure.dto.eventdto import EventDTO


class EventRepository(IEventRepository):
    """A class representing continent DB repository."""

    async def get_all_events(self) -> Iterable[Any]:
        query = (
            select(
                event_table.c.id,
                event_table.c.name,
                event_table.c.description,
                event_table.c.start_time,
                event_table.c.end_time,
                location_table.c.latitude.label("latitude"),
                location_table.c.longitude.label("longitude"),
                location_table.c.id.label("location_id"),
                location_table.c.name.label("location_name"),
                event_table.c.max_participants,
                event_table.c.user_id,
            )
            .select_from(
                join(
                    event_table,
                    location_table,
                    event_table.c.location_id == location_table.c.id
                )
            )
            .order_by(event_table.c.name.asc())
        )

        events = await database.fetch_all(query)

        # Logowanie wyników
        for event in events:
            print(f"Fetched event: {event}")

        return [EventDTO.from_record(event) for event in events]

        # Logowanie wyników
        for event in events:
            print(f"Fetched event: {event}")

        return [EventDTO.from_record(event) for event in events]

    async def get_by_location(self, location_id: int) -> Iterable[Any]:
        """The method getting events assigned to particular location.

        Args:
            location_id (int): The id of the location.

        Returns:
            Iterable[Any]: Events assigned to a location.
        """

        query = (
            select(event_table)
            .where(event_table.c.location_id == location_id)
            .order_by(event_table.c.name.asc())
        )
        events = await database.fetch_all(query)

        return [Event(**dict(event)) for event in events]

    async def get_by_id(self, event_id: int) -> Any | None:
        """The method getting event by provided id.

        Args:
            event_id (int): The id of the event.

        Returns:
            Any | None: The event details.
        """

        query = (
            select(event_table, location_table)
            .select_from(
                join(
                    event_table,
                    location_table,
                    event_table.c.location_id == location_table.c.id  # Poprawny warunek
                )
            )
            .where(event_table.c.id == event_id)
            .order_by(event_table.c.name.asc())
        )
        event = await database.fetch_one(query)

        return EventDTO.from_record(event) if event else None

    async def get_by_date_range(
            self,
            start_date: datetime,
            end_date: datetime
    ) -> Iterable[Any]:
        # Konwersja na offset-aware datetime (UTC)
        start_date = start_date.replace(tzinfo=timezone.utc) if start_date.tzinfo is None else start_date.astimezone(timezone.utc)
        end_date = end_date.replace(tzinfo=timezone.utc) if end_date.tzinfo is None else end_date.astimezone(timezone.utc)

        query = (
            select(event_table)
            .where(event_table.c.start_date <= start_date)
            .where(event_table.c.end_date > end_date)
        )
        return await database.fetch_all(query)

    async def get_by_user(self, user_id: UUID4) -> Iterable[Any]:
        """The method getting airports by user who added them.

        Args:
            user_id (int): The id of the user.

        Returns:
            Iterable[Any]: The airport collection.
        """

        return []

    from sqlalchemy.sql import func

    async def get_events_within_radius(
            self, latitude: float, longitude: float, radius: float
    ) -> Iterable[Event]:
        """
        Retrieve events within a certain radius from a given location.

        Args:
            latitude (float): Latitude of the user's location.
            longitude (float): Longitude of the user's location.
            radius (float): Search radius in kilometers.

        Returns:
            Iterable[Event]: Events within the specified radius.
        """
        earth_radius_km = 6371  # Earth's radius in kilometers

        # Haversine formula for calculating distance between two lat/lon points
        query = (
            select(
                event_table.c.id,
                event_table.c.name,
                event_table.c.start_time,
                event_table.c.end_time,
                location_table.c.latitude.label("location_lat"),
                location_table.c.longitude.label("location_lon"),
            )
            .select_from(
                join(event_table, location_table, event_table.c.location_id == location_table.c.id)
            )
            .where(
                func.acos(
                    func.sin(func.radians(latitude)) * func.sin(func.radians(location_table.c.latitude)) +
                    func.cos(func.radians(latitude)) * func.cos(func.radians(location_table.c.latitude)) *
                    func.cos(func.radians(location_table.c.longitude) - func.radians(longitude))
                ) * earth_radius_km <= radius
            )
        )
        events = await database.fetch_all(query)
        return [Event(**dict(event)) for event in events]

    async def add_event(self, data: EventBroker) -> Any | None:
        """The method adding new event to the data storage.

            Args:
                data (EventBroker): The details of the new event.

            Returns:
                Event: Full details of the newly added event.

        """
        print(f"Start Time: {data.start_time}, End Time: {data.end_time}")
        data.start_time = data.start_time.replace(
            tzinfo=timezone.utc) if data.start_time.tzinfo is None else data.start_time.astimezone(timezone.utc)
        data.end_time = data.end_time.replace(
            tzinfo=timezone.utc) if data.end_time.tzinfo is None else data.end_time.astimezone(timezone.utc)

        # Sprawdzanie konfliktów czasowych dla danego location_id
        conflict_query = (
            select(event_table)
            .where(
                and_(
                    event_table.c.location_id == data.location_id,
                    or_(
                        and_(event_table.c.start_time <= data.start_time, event_table.c.end_time > data.start_time),
                        and_(event_table.c.start_time < data.end_time, event_table.c.end_time >= data.end_time),
                        and_(event_table.c.start_time >= data.start_time, event_table.c.end_time <= data.end_time)
                    )
                )
            )
        )

        conflicting_events = await database.fetch_all(conflict_query)
        if conflicting_events:
            raise HTTPException(
                status_code=400,
                detail="Event cannot be created. Overlapping events exist for the same location."
            )

        # Dodanie nowego wydarzenia, jeśli nie ma konfliktów
        query = event_table.insert().values(**data.model_dump())
        new_event_id = await database.execute(query)
        new_event = await self._get_by_id(new_event_id)

        return Event(**dict(new_event)) if new_event else None

    async def update_event(
            self,
            event_id: int,
            data: EventBroker,
    ) -> Any | None:
        """The method updating event data in the data storage.

        Args:
            event_id (int): The id of the event.
            data (EventBroker): The details of the updated event.

        Returns:
            Any | None: The updated event details.

        Raises:
            HTTPException: If the location_id does not exist in the locations table,
                           or if overlapping events exist for the same location.
        """

        # Sprawdzenie, czy location_id istnieje
        location_check_query = select(location_table).where(location_table.c.id == data.location_id)
        location = await database.fetch_one(location_check_query)
        if not location:
            raise HTTPException(
                status_code=400,
                detail=f"Location with id {data.location_id} does not exist."
            )

        # Pobranie istniejących wydarzeń dla tej samej lokalizacji
        existing_events_query = select(event_table).where(
            and_(
                event_table.c.location_id == data.location_id,
                event_table.c.id != event_id  # Wykluczamy bieżące wydarzenie
            )
        )
        existing_events = await database.fetch_all(existing_events_query)

        # Walidacja nakładania się czasów
        for existing_event in existing_events:
            if (
                    existing_event["start_time"] < data.end_time
                    and existing_event["end_time"] > data.start_time
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Cannot update event with id {event_id}. "
                        "Overlapping events detected for the same location."
                    )
                )

        # Kontynuacja aktualizacji wydarzenia
        if self._get_by_id(event_id):
            query = (
                event_table.update()
                .where(event_table.c.id == event_id)
                .values(**data.model_dump())
            )
            await database.execute(query)

            event = await self._get_by_id(event_id)

            return Event(**dict(event)) if event else None

        raise HTTPException(
            status_code=404,
            detail=f"Event with id {event_id} does not exist."
        )

    async def delete_event(self, event_id: int) -> bool:
        """The method updating removing event from the data storage.

        Args:
            event_id (int): The id of the event.

        Returns:
            bool: Success of the operation.
        """

        if self._get_by_id(event_id):
            query = event_table \
                .delete() \
                .where(event_table.c.id == event_id)
            await database.execute(query)

            return True

        return False

    async def _get_by_id(self, event_id: int) -> Record | None:
        """A private method getting event from the DB based on its ID.

        Args:
            event_id (int): The ID of the event.

        Returns:
            Any | None: Event record if exists.
        """

        query = (
            event_table.select()
            .where(event_table.c.id == event_id)
            .order_by(event_table.c.name.asc())
        )

        return await database.fetch_one(query)