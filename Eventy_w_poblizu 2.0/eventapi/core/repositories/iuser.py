"""Module containing user repository abstractions."""

from abc import ABC, abstractmethod
from typing import Iterable, Any
from eventapi.core.domain.user import User, UserIn
from pydantic import UUID4


class IUserRepository(ABC):
    """An abstract class representing protocol of user repository."""

    @abstractmethod
    async def register_user(self, user: UserIn) -> Any | None:
        """A method registering new user.

        Args:
            user (UserIn): The user input data.

        Returns:
            Any | None: The new user object.
        """

    @abstractmethod
    async def get_by_uuid(self, uuid: UUID4) -> Any | None:
        """A method getting user by UUID.

        Args:
            uuid (UUID5): UUID of the user.

        Returns:
            Any | None: The user object if exists.
        """

    @abstractmethod
    async def get_by_username(self, username: str) -> Any | None:
        """A method getting user by username.

        Args:
            username: str | name of the user.

        Returns:
            Any | None: The user object if exists.
        """

    @abstractmethod
    async def get_by_email(self, email: str) -> Any | None:
        """The abstract getting user by email address.

        Args:
            email (str): The email of the user.

        Returns:
            User | None: The user details.
        """

    @abstractmethod
    async def update_user(self, user_id: UUID4, user_data: UserIn) -> Any | None:
        """A method to update user data.

        Args:
            user_id (UUID5): UUID of the user.
            user_data (UserIn): New data to update the user.

        Returns:
            Any | None: The updated user object or None if the user does not exist.
        """

    @abstractmethod
    async def delete_user(self, user_id: UUID4) -> bool:
        """A method to delete user by UUID.

        Args:
            user_id (UUID5): UUID of the user to delete.

        Returns:
            bool: True if the user was deleted, False if the user does not exist.
        """

    @abstractmethod
    async def get_all_users(self) -> Iterable[Any]:
        """A method to get all users.

        Returns:
            Iterable[Any]: list of all users.
        """