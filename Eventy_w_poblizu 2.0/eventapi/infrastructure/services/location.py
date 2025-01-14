"""Module containing location repository abstractions."""

from typing import Iterable
from eventapi.core.domain.location import Location, LocationIn
from eventapi.core.repositories.ilocation import ILocationRepository
from eventapi.infrastructure.services.ilocation import ILocationService
from fastapi import HTTPException

class LocationService(ILocationService):
    """An abstract class representing protocol of location repository."""

    _repository: ILocationRepository

    def __init__(self, repository: ILocationRepository) -> None:
        """The initializer of the `location service`.

        Args:
            repository (ILocationRepository): The reference to the repository.
        """

        self._repository = repository

    async def get_all_locations(self) -> Iterable[Location]:
        """The abstract getting all locations from the data storage.

        Returns:
            Iterable[Location]: Locations in the data storage.
        """
        return await self._repository.get_all_locations()

    async def get_by_id(self, location_id: int) -> Location | None:
        """The abstract getting location by provided id.

        Args:
            location_id (int): The id of the location.

        Returns:
            Location | None: The location details.
        """
        return await self._repository.get_by_id(location_id)

    async def get_by_coordinates(
        self,
        latitude: float,
        longitude: float,
        radius: float
    ) -> Iterable[Location]:
        """The abstract getting locations by radius around given coordinates.

        Args:
            latitude (float): The geographical latitude.
            longitude (float): The geographical longitude.
            radius (float): The radius to search.

        Returns:
            Iterable[Location]: The resulting locations.
        """
        return await self._repository.get_by_coordinates(latitude, longitude, radius)

    async def add_location(self, data: LocationIn) -> None:
        """The abstract adding a new location to the data storage.

        Args:
            data (LocationIn): The details of the new location.
        """



        return await self._repository.add_location(data)

    async def update_location(
            self,
            location_id: int,
            data: LocationIn
    ) -> Location | None:
        """Aktualizuje dane lokalizacji po przeprowadzeniu walidacji.

        Args:
            location_id (int): ID lokalizacji.
            data (LocationIn): Nowe dane lokalizacji.

        Returns:
            Location | None: Zaktualizowana lokalizacja lub None.
        """

        # Pobierz istniejącą lokalizację
        existing_location = await self._repository.get_by_id(location_id)
        if not existing_location:
            raise HTTPException(status_code=404, detail="Location not found")

        # Sprawdź, czy współrzędne zostały zmienione
        coordinates_changed = (
                existing_location.latitude != data.latitude or
                existing_location.longitude != data.longitude
        )

        # Jeśli współrzędne się zmieniają, sprawdź ich unikalność
        if coordinates_changed:
            conflicting_locations = await self._repository.get_by_coordinates(
                latitude=data.latitude,
                longitude=data.longitude,
                radius=0
            )
            for loc in conflicting_locations:
                if loc.id != location_id:
                    raise HTTPException(status_code=400, detail="Location with these coordinates already exists")

        # Sprawdź, czy jakiekolwiek dane się zmieniają
        if (
                existing_location.name == data.name and
                existing_location.latitude == data.latitude and
                existing_location.longitude == data.longitude and
                existing_location.address == data.address  # Sprawdzenie adresu
        ):
            raise HTTPException(status_code=400, detail="No changes detected")

        # Wykonaj aktualizację
        return await self._repository.update_location(location_id, data)

    async def delete_location(self, location_id: int) -> bool:
        """The abstract removing a location from the data storage.

        Args:
            location_id (int): The id of the location.

        Returns:
            bool: Success of the operation.
        """
        return await self._repository.delete_location(location_id)
