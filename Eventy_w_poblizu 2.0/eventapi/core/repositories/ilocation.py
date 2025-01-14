"""Module containing location repository abstractions."""

from abc import ABC, abstractmethod
from typing import Iterable, Any
from eventapi.core.domain.location import Location, LocationIn


class ILocationRepository(ABC):
    """An abstract class representing protocol of location repository."""

    @abstractmethod
    async def get_all_locations(self) -> Iterable[Any]:
        """The abstract getting all locations from the data storage.

        Returns:
            Iterable[Any]: Locations in the data storage.
        """

    @abstractmethod
    async def get_by_id(self, location_id: int) -> Any | None:
        """The abstract getting location by provided id.

        Args:
            location_id (int): The id of the location.

        Returns:
            Any | None: The location details.
        """

    @abstractmethod
    async def get_by_name(self, location_name: str) -> Any | None:
        """The abstract getting location by provided id.

        Args:
            location_name (str): The name of the location.

        Returns:
            Location | None: The location details.
        """
    @abstractmethod
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

    @abstractmethod
    async def add_location(self, data: LocationIn) -> Any | None:
        """The abstract adding a new location to the data storage.

        Args:
            data (LocationIn): The details of the new location.
        """

    @abstractmethod
    async def update_location(
        self,
        location_id: int,
        data: LocationIn
    ) -> Any | None:
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
