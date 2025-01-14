from abc import ABC, abstractmethod

from pydantic import UUID4

from eventapi.core.domain.user import UserIn
from eventapi.infrastructure.dto.userdto import UserDTO
from eventapi.infrastructure.dto.tokendto import TokenDTO


class IUserService(ABC):
    """An abstract class for user service."""

    @abstractmethod
    async def register_user(self, user: UserIn) -> UserDTO | None:
        """A method registering a new user.

        Args:
            user (UserIn): The user input data.

        Returns:
            UserDTO | None: The user DTO model.
        """

    @abstractmethod
    async def authenticate_user(self, user: UserIn) -> TokenDTO | None:
        """The method authenticating the user.

        Args:
            user (UserIn): The user data.

        Returns:
            TokenDTO | None: The token details.
        """

    @abstractmethod
    async def get_by_uuid(self, uuid: UUID4) -> UserDTO | None:
        """A method getting user by UUID.

        Args:
            uuid (UUID5): The UUID of the user.

        Returns:
            UserDTO | None: The user data, if found.
        """

    @abstractmethod
    async def get_by_email(self, email: str) -> UserDTO | None:
        """A method getting user by email.

        Args:
            email (str): The email of the user.

        Returns:
            UserDTO | None: The user data, if found.
        """
