from fastapi import APIRouter, HTTPException, Depends, Request, Security
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from passlib.context import CryptContext
from pydantic import UUID4
from eventapi.core.domain.user import UserIn, User
from eventapi.core.repositories.iuser import IUserRepository
from eventapi.infrastructure.dto.tokendto import TokenDTO
from eventapi.infrastructure.repositories.user import UserRepository
from eventapi.infrastructure.services.iuser import IUserService
from eventapi.infrastructure.utils.token import generate_user_token, decode_access_token
from eventapi.infrastructure.utils.password import verify_password
from eventapi.infrastructure.utils.consts import (
    SECRET_KEY,
    ALGORITHM,
    EXPIRATION_MINUTES
)
from dependency_injector.wiring import Provide, inject
from eventapi.container import Container
from eventapi.api.utils.enums import UserRole
from eventapi.infrastructure.dto.userdto import UserDTO
router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = EXPIRATION_MINUTES  # Spójny czas wygaśnięcia

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

# Helper function to authenticate user
@inject
async def authenticate_user(
        username: str,
        password: str,
        user_repository: IUserRepository = Depends(Provide[Container.user_repository])
):
    user = await user_repository.get_by_username(username)
    print(f"User from DB: {user}")
    if not user:
        print(f"User {username} not found")
        return None

    print(f"Entered password: {password}")
    print(f"Stored hash in DB: {user.password}")

    if not verify_password(password, user.password):
        print(f"Invalid password for user {username}")
        return None

    return user

@router.get("/users/me", response_model=User)
@inject
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    user_repository: IUserRepository = Depends(Provide[Container.user_repository])
):
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token or user not found")

    user = await user_repository.get_by_uuid(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user



# Endpoint to get all users
@router.get("/users", response_model=List[User])
@inject
async def get_all_users(
    user_repository: IUserRepository = Depends(Provide[Container.user_repository])
):
    users = await user_repository.get_all_users()
    return users


# Endpoint to get user by uuid
@router.get("/users/{user_id}", response_model=User)
@inject
async def get_user_by_id(
    user_id: UUID4,
    user_repository: IUserRepository = Depends(Provide[Container.user_repository])
):
    print(f"Fetching user with ID: {user_id}")
    user = await user_repository.get_by_uuid(user_id)
    if not user:
        print(f"User with ID {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    print(f"User found: {user}")
    return user


# Endpoint to create new user
@router.post("/users", response_model=UserDTO)
@inject
async def create_user(
    user_data: UserIn,
    user_repository: IUserRepository = Depends(Provide[Container.user_repository])
):
    # Sprawdzenie czy użytkownik istnieje
    existing_user = await user_repository.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="User with this email already exists")

    # Hashowanie hasła
    user_data.password = pwd_context.hash(user_data.password)


    # Przygotowanie danych użytkownika
    user_data_with_role = user_data.dict()
    user_data_with_role["role"] = UserRole.USER


    # Rejestracja użytkownika
    new_user = await user_repository.register_user(UserIn(**user_data_with_role))
    return new_user


# Endpoint to update user
@router.put("/users/{user_id}", response_model=User)
@inject
async def update_user(
    user_id: UUID4,
    user_data: UserIn,
    user_repository: IUserRepository = Depends(Provide[Container.user_repository])
):
    user_data.password = pwd_context.hash(user_data.password)
    updated_user = await user_repository.update_user(user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


# Endpoint to delete user
@router.delete("/users/{user_id}", status_code=200)
@inject
async def delete_user(
    user_id: UUID4,
    user_repository: IUserRepository = Depends(Provide[Container.user_repository])
):
    success = await user_repository.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {"detail": "User successfully deleted"}


# Token generation endpoint
@router.post("/token", response_model=TokenDTO, status_code=200)
@inject
async def login_user(
    user: UserIn,
    service: IUserService = Depends(Provide[Container.user_service]),
) -> dict:
    """A router coroutine for authenticating users.

    Args:
        user (UserIn): The user input data.
        service (IUserService, optional): The injected user service.

    Returns:
        dict: The token DTO details.
    """

    if token_details := await service.authenticate_user(user):
        print("user confirmed")
        return token_details.model_dump()

    raise HTTPException(
        status_code=401,
        detail="Provided incorrect credentials",
    )