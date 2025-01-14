"""A module containing continent endpoints."""

from typing import Iterable
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt

from eventapi.container import Container
from eventapi.core.domain.location import Location, LocationIn
from eventapi.infrastructure.services.ilocation import ILocationService
from eventapi.api.routers.user_router import get_current_user  # Import the existing method
from eventapi.api.utils.enums import UserRole
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from eventapi.infrastructure.utils import consts
from eventapi.infrastructure.utils.token import decode_access_token

router = APIRouter()
bearer_scheme = HTTPBearer()

@router.post("/create", response_model=Location, status_code=201)
@inject
async def create_location(
    location: LocationIn,
    service: ILocationService = Depends(Provide[Container.location_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Create a location, restricted to admins.
    """
    # Decode the token and check the role
    token = credentials.credentials
    payload = decode_access_token(token)
    role = payload.get("role")
    if role.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    # Call the service method to add the location
    created_location = await service.add_location(location)

    # Handle the case when add_location returns None
    if created_location is None:
        raise HTTPException(status_code=400, detail="Location creation failed")

    # Convert Location object to dict and return it
    return created_location.dict()


router.get("/", response_model=Iterable[Location], status_code=200)
@inject
async def get_all_locations(
    service: ILocationService = Depends(Provide[Container.location_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Iterable[dict]:
    """
    Get all locations, available for logged-in users.

    Args:
        service (ILocationService): The location service dependency.
        credentials (HTTPAuthorizationCredentials): The credentials for authorizing the user.

    Returns:
        Iterable[dict]: A list or generator of all locations.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    print(f"Decoded payload: {payload}")  # Debug: Sprawdzenie danych tokena

    locations = await service.get_all_locations()
    # Zwrócenie listy, jeśli wymagane przez serializator JSON
    return (location.model_dump() for location in locations)


@router.get("/{location_id}", response_model=Location, status_code=200)
@inject
async def get_location_by_id(
    location_id: int,
    service: ILocationService = Depends(Provide[Container.location_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),  # Dodano token
) -> dict:
    """
    Get a location by its ID, available for logged-in users.

    Args:
        location_id (int): The ID of the location to fetch.
        service (ILocationService): The location service dependency.
        credentials (HTTPAuthorizationCredentials): The credentials for authorizing the user.

    Returns:
        dict: The location details.
    """

    # Decode the token and verify it belongs to a logged-in user
    token = credentials.credentials
    payload = decode_access_token(token)

    location = await service.get_by_id(location_id=location_id)
    if location:
        return location.model_dump()

    raise HTTPException(status_code=404, detail="Location not found")

@router.put("/{location_id}", response_model=Location, status_code=201)
@inject
async def update_location(
    location_id: int,
    updated_location: LocationIn,
    service: ILocationService = Depends(Provide[Container.location_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Update a location with given id and data.

    Args:
        location_id (int): The id of the location to update.
        updated_location (LocationIn): The new data for the location.
        service (ILocationService): The location service dependency.
        credentials (HTTPAuthorizationCredentials): The credentials for authorizing the user.

    Returns:
        dict: The updated location.
    """
    # Decode the token and check the role
    token = credentials.credentials
    payload = decode_access_token(token)
    role = payload.get("role")
    print(f"User role from token: {role}")  # Debug
    if role.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    if await service.get_by_id(location_id=location_id):
        new_updated_location = await service.update_location(
            location_id=location_id,
            data=updated_location,
        )
        return new_updated_location.model_dump() if new_updated_location else {}

    raise HTTPException(status_code=404, detail="Location not found")


@router.delete("/{location_id}", status_code=204)
@inject
async def delete_location(
    location_id: int,
    service: ILocationService = Depends(Provide[Container.location_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),  # Dodano token
) -> None:
    """
    Delete a location with given id.

    Args:
        location_id (int): The id of the location to delete.
        service (ILocationService): The location service dependency.
        credentials (HTTPAuthorizationCredentials): The credentials for authorizing the user.
    Returns:
        None: Deletes the location or raises an error if not found.
    """

    # Decode the token and check the role
    token = credentials.credentials
    payload = decode_access_token(token)
    role = payload.get("role")
    if role.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    if await service.get_by_id(location_id=location_id):
        await service.delete_location(location_id)
        return

    raise HTTPException(status_code=404, detail="Location not found")