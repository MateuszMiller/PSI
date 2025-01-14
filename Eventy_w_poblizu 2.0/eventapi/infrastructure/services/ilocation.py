"""Module containing location repository abstractions."""

from abc import ABC, abstractmethod
from typing import Iterable
from eventapi.core.domain.location import Location, LocationIn


class ILocationService(ABC):
    """An abstract class representing protocol of location repository."""

    @abstractmethod
    async def get_all_locations(self) -> Iterable[Location]:
        """The abstract getting all locations from the data storage.

        Returns:
            Iterable[Location]: Locations in the data storage.
        """

    @abstractmethod
    async def get_by_id(self, location_id: int) -> Location | None:
        """The abstract getting location by provided id.

        Args:
            location_id (int): The id of the location.

        Returns:
            Location | None: The location details.
        """

    @abstractmethod
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

    @abstractmethod
    async def add_location(self, data: LocationIn) -> Location | None:
        """The abstract adding a new location to the data storage.

        Args:
            data (LocationIn): The details of the new location.
        """

    @abstractmethod
    async def update_location(
        self,
        location_id: int,
        data: LocationIn
    ) -> Location | None:
        """The abstract updating location data in the data storage.

        Args:
            location_id (int): The id of the location.
            data (LocationIn): The updated location details.

        Returns:
            Location | None: The updated location details.
        """

    @abstractmethod
    async def delete_location(self, location_id: int) -> bool:
        """The abstract removing a location from the data storage.

        Args:
            location_id (int): The id of the location.

        Returns:
            bool: Success of the operation.
        """
