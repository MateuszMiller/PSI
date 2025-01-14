"""Module containing continent database repository implementation."""

from typing import Any, Iterable

from asyncpg import Record  # type: ignore
from sqlalchemy import select
from fastapi import HTTPException
from eventapi.core.domain.location import Location, LocationIn
from eventapi.core.repositories.ilocation import ILocationRepository
from eventapi.db import location_table, database


class LocationRepository(ILocationRepository):
    """A class implementing the continent repository."""

    async def get_by_id(self, location_id: int) -> Any | None:
        """The method getting a location from the data storage.

        Args:
            location_id (int): The id of the location.

        Returns:
            Any | None: The location data if exists.
        """

        location = await self._get_by_id(location_id)

        return Location(**dict(location)) if location else None

    async def get_all_locations(self) -> Iterable[Any]:
        """The method getting all locations from the data storage.

        Returns:
            Iterable[Any]: The collection of the all locations.
        """

        query = location_table.select().order_by(location_table.c.name.asc())
        locations = await database.fetch_all(query)

        return [Location(**dict(location)) for location in locations]

    async def get_by_name(self, location_name: str) -> Any | None:
        """The abstract getting location by provided id.

        Args:
            location_name (str): The name of the location.

        Returns:
            Location | None: The location details.
        """

        query = location_table \
            .select() \
            .where(location_table.c.name == location_name) \
            .order_by(location_table.c.name.asc())
        locations = await database.fetch_all(query)

        return [Location(**dict(location)) for location in locations]

    async def get_by_coordinates(
            self,
            latitude: float,
            longitude: float,
            radius: float
    ) -> Iterable[Any]:
        """The abstract getting locations by radius around given coordinates.

        Args:
            latitude (float): The geographical latitude.
            longitude (float): The geographical longitude.
            radius (float): The radius to search.

        Returns:
            Iterable[Location]: The resulting locations.
        """

        query = location_table \
            .select() \
            .where(location_table.c.latitude == latitude and location_table.c.longtitute == longitude) \
            .order_by(location_table.c.name.asc())
        locations = await database.fetch_all(query)

        return [Location(**dict(location)) for location in locations]

    async def add_location(self, data: LocationIn) -> Any | None:
        """The method adding new location to the data storage.

        Args:
            data (LocationIn): The attributes of the location.

        Returns:
            Any | None: The newly created location.
        """

        # Sprawdzenie czy lokalizacja z takimi współrzędnymi już istnieje
        query = select(location_table).where(
            (location_table.c.latitude == data.latitude) &
            (location_table.c.longitude == data.longitude)
        )
        existing_location = await database.fetch_one(query)

        # Jeśli lokalizacja już istnieje, zwróć błąd 400
        if existing_location:
            raise HTTPException(
                status_code=400,
                detail="Location with these coordinates already exists."
            )

        # Wstawienie nowej lokalizacji po pozytywnej walidacji
        query = location_table.insert().values(**data.model_dump())
        new_location_id = await database.execute(query)
        new_location = await self._get_by_id(new_location_id)

        return Location(**dict(new_location)) if new_location else None

    async def update_location(
            self,
            location_id: int,
            data: LocationIn,
    ) -> Any | None:
        """The method updating location data in the data storage.

        Args:
            location_id (int): The location id.
            data (LocationIn): The attributes of the location.

        Returns:
            Any | None: The updated location.
        """

        if self._get_by_id(location_id):
            query = (
                location_table.update()
                .where(location_table.c.id == location_id)
                .values(**data.model_dump())
            )
            await database.execute(query)

            location = await self._get_by_id(location_id)

            return Location(**dict(location)) if location else None

        return None

    async def delete_location(self, location_id: int) -> bool:
        """The method updating removing location from the data storage.

        Args:
            location_id (int): The location id.

        Returns:
            bool: Success of the operation.
        """

        if self._get_by_id(location_id):
            query = location_table \
                .delete() \
                .where(location_table.c.id == location_id)
            await database.execute(query)

            return True

        return False

    async def _get_by_id(self, location_id: int) -> Record | None:
        """A private method getting location from the DB based on its ID.

        Args:
            location_id (int): The ID of the location.

        Returns:
            Any | None: Locations record if exists.
        """

        query = (
            location_table.select()
            .where(location_table.c.id == location_id)
            .order_by(location_table.c.name.asc())
        )

        return await database.fetch_one(query)
