"""A repository for user entity."""

from typing import Iterable, Any
from sqlalchemy import select
from pydantic import UUID4

from eventapi.core.domain.user import UserIn
from eventapi.core.repositories.iuser import IUserRepository
from eventapi.db import database, user_table
from eventapi.api.utils.enums import UserRole
from eventapi.infrastructure.utils.password import hash_password


class UserRepository(IUserRepository):
    """An implementation of repository class for user."""


    async def get_user_id_by_uuid(self, user_uuid: str) -> int | None:
        query = select(user_table.c.id).where(user_table.c.uuid == user_uuid)
        result = await database.fetch_one(query)
        if result:
            return result["id"]  # Zwracamy int, który jest ID użytkownika
        return None

    async def register_user(self, user: UserIn) -> Any | None:
        """Rejestracja użytkownika."""

        # Sprawdzenie, czy użytkownik już istnieje
        if await self.get_by_email(user.email):
            return None


        # Przygotowanie danych do zapisu
        user_data = user.model_dump()
        user_data["role"] = UserRole.USER.value

        query = user_table.insert().values(**user_data)
        new_user_uuid = await database.execute(query)


        return await self.get_by_uuid(new_user_uuid)

    async def get_by_uuid(self, uuid: UUID4) -> Any | None:
        """A method getting user by UUID.

        Args:
            uuid (UUID5): UUID of the user.

        Returns:
            Any | None: The user object if exists.
        """

        query = user_table \
            .select() \
            .where(user_table.c.id == uuid)
        user = await database.fetch_one(query)

        return user

    async def get_by_email(self, email: str) -> Any | None:
        """A method getting user by email.

        Args:
            email (str): The email of the user.

        Returns:
            Any | None: The user object if exists.
        """

        query = user_table \
            .select() \
            .where(user_table.c.email == email)
        user = await database.fetch_one(query)

        return user

    async def get_by_username(self, username: str) -> Any | None:
        query = user_table.select().where(user_table.c.username == username)
        return await database.fetch_one(query)

    async def update_user(self, user_id: UUID4, user_data: UserIn) -> Any | None:
        """A method to update user data.

        Args:
            user_id (UUID5): UUID of the user.
            user_data (UserIn): New data to update the user.

        Returns:
            Any | None: The updated user object or None if the user does not exist.
        """

        # Sprawdzenie, czy użytkownik istnieje
        existing_user = await self.get_by_uuid(user_id)
        if not existing_user:
            return None

        # Aktualizacja danych użytkownika
        query = (
            user_table.update()
            .where(user_table.c.id == user_id)
            .values(**user_data.model_dump())
            .returning(user_table)
        )
        updated_user = await database.fetch_one(query)
        return updated_user

    async def delete_user(self, user_id: UUID4) -> bool:
        """A method to delete user by UUID.

        Args:
            user_id (UUID5): UUID of the user to delete.

        Returns:
            bool: True if the user was deleted, False if the user does not exist.
        """
        existing_user = await self.get_by_uuid(user_id)
        if not existing_user:
            return False  # Zwracamy False, jeśli użytkownik nie istnieje

        query = user_table.delete().where(user_table.c.id == user_id)
        await database.execute(query)  # Wykonaj DELETE bez sprawdzania wyniku

        return True  # Zawsze zwracaj True, jeśli DELETE został wykonany

    async def get_all_users(self) -> Iterable[Any]:
        """A method to get all users.

        Returns:
            Iterable[Any]: Iterable of user objects.
        """
        query = user_table.select()
        result = await database.fetch_all(query)
        return iter(result)