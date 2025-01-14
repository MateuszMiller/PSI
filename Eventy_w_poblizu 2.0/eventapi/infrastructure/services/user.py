"""A module containing user service."""

from pydantic import UUID4

from eventapi.core.domain.user import UserIn
from eventapi.core.repositories.iuser import IUserRepository
from eventapi.infrastructure.dto.userdto import UserDTO
from eventapi.infrastructure.dto.tokendto import TokenDTO
from eventapi.infrastructure.services.iuser import IUserService
from eventapi.infrastructure.utils.password import verify_password
from eventapi.infrastructure.utils.token import generate_user_token
from fastapi import HTTPException

class UserService(IUserService):
    """An abstract class for user service."""

    _repository: IUserRepository

    def __init__(self, repository: IUserRepository) -> None:
        self._repository = repository

    async def register_user(self, user: UserIn) -> UserDTO | None:
        """A method registering a new user.

        Args:
            user (UserIn): The user input data.

        Returns:
            UserDTO | None: The user DTO model.
        """

        return await self._repository.register_user(user)

    async def authenticate_user(self, user: UserIn) -> TokenDTO | None:
        """Uwierzytelnianie użytkownika."""

        # Pobranie użytkownika po e-mailu
        if user_data := await self._repository.get_by_email(user.email):
            # Debug: Sprawdzenie wprowadzonego hasła i hasła w bazie


            # Weryfikacja hasła
            if verify_password(user.password, user_data.password):
                user_role = user_data.role
                token_details = generate_user_token(user_data.id, user_role)
                return TokenDTO(token_type="Bearer", **token_details)


        raise HTTPException(status_code=401, detail="Provided incorrect credentials")

    async def get_by_uuid(self, uuid: UUID4) -> UserDTO | None:
        """A method getting user by UUID.

        Args:
            uuid (UUID5): The UUID of the user.

        Returns:
            UserDTO | None: The user data, if found.
        """

        return await self._repository.get_by_uuid(uuid)

    async def get_by_email(self, email: str) -> UserDTO | None:
        """A method getting user by email.

        Args:
            email (str): The email of the user.

        Returns:
            UserDTO | None: The user data, if found.
        """

        return await self.get_by_email(email)
