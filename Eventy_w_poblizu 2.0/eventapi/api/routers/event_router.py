"""A module containing continent endpoints."""

from typing import Iterable

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from datetime import timezone, datetime
from pydantic import ValidationError, UUID4
from uuid import uuid4

from eventapi.infrastructure.services.event import EventService
from eventapi.infrastructure.utils import consts
from eventapi.container import Container
from eventapi.core.domain.event import Event, EventIn, EventBroker
from eventapi.infrastructure.dto.eventdto import EventDTO
from eventapi.infrastructure.services.ievent import IEventService

from sqlalchemy import select
from eventapi.db import location_table, database

bearer_scheme = HTTPBearer()

router = APIRouter()



@router.post("/create", response_model=Event, status_code=201)
@inject
async def create_event(
        event: EventIn,
        service: IEventService = Depends(Provide[Container.event_service]),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = credentials.credentials
    token_payload = jwt.decode(
        token,
        key=consts.SECRET_KEY,
        algorithms=[consts.ALGORITHM],
    )
    user_uuid = token_payload.get("sub")

    if not user_uuid:
        raise HTTPException(status_code=403, detail="Unauthorized")

    query = select(location_table).where(location_table.c.id == event.location_id)
    location = await database.fetch_one(query)

    if not location:
        raise HTTPException(
            status_code=400,
            detail=f"Location with id {event.location_id} does not exist"
        )

    # WALIDACJA DATETIME
    try:
        if event.start_time.tzinfo is None:
            event.start_time = event.start_time.replace(tzinfo=timezone.utc)
        else:
            event.start_time = event.start_time.astimezone(timezone.utc)

        if event.end_time.tzinfo is None:
            event.end_time = event.end_time.replace(tzinfo=timezone.utc)
        else:
            event.end_time = event.end_time.astimezone(timezone.utc)

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {str(e)}")

    extended_event_data = EventBroker(
        user_id=user_uuid,
        **event.model_dump(),
    )
    new_event = await service.add_event(extended_event_data)

    return new_event.model_dump() if new_event else {}

@router.get("/all", response_model=Iterable[EventDTO], status_code=200)
@inject
async def get_all_events(
        service: IEventService = Depends(Provide[Container.event_service]),
) -> Iterable:
    """An endpoint for getting all events.

    Args:
        service (IEventService, optional): The injected service dependency.

    Returns:
        Iterable: The event attributes collection.
    """

    events = await service.get_all_events()

    return events

@router.get("/recommendations", response_model=Iterable[Event], status_code=200)
@inject
async def get_recommended_events(
        latitude: float = Query(..., description="Latitude of the user's location"),
        longitude: float = Query(..., description="Longitude of the user's location"),
        radius: float = Query(50.0, description="Search radius in kilometers"),
        service: IEventService = Depends(Provide[Container.event_service]),
) -> Iterable[Event]:
    """
    Retrieve recommended events based on user's location and search radius.

    Args:
        latitude (float): Latitude of the user's location.
        longitude (float): Longitude of the user's location.
        radius (float): Search radius in kilometers.
        service (IEventService, optional): Injected service for event operations.

    Returns:
        Iterable[Event]: List of recommended events.
    """
    # Logowanie otrzymanych parametrów (na potrzeby debugowania)
    print(f"Received parameters: latitude={latitude}, longitude={longitude}, radius={radius}")

    # Pobranie polecanych wydarzeń z serwisu
    recommended_events = await service.get_recommended_events(latitude, longitude, radius)

    # Logowanie liczby zwróconych wydarzeń
    print(f"Number of recommended events: {len(recommended_events)}")

    # Zwracanie danych w odpowiednim formacie
    return [event.model_dump() for event in recommended_events]

@router.get(
    "/{event_id}",
    response_model=EventDTO,
    status_code=200,
)
@inject
async def get_events_by_id(
        event_id: int,
        service: IEventService = Depends(Provide[Container.event_service]),
) -> Iterable:
    """An endpoint for getting event by id.

    Args:
        event_id (int): The id of the event.
        service (IEventService, optional): The injected service dependency.

    Returns:
        Iterable: The event details collection.
    """

    if event := await service.get_by_id(event_id):
        return event.model_dump()

    raise HTTPException(status_code=404, detail="Event not found")


@router.get(
    "{event_id}",
    response_model=EventDTO,
    status_code=200,
)
@inject
async def get_by_date_range(
        start_date: datetime,
        end_date: datetime,
        service: IEventService = Depends(Provide[Container.event_service]),
) -> Iterable:
    """An endpoint for getting event within a date range.

        Args:
            start_date (datetime): Start date of the range.
            end_date (datetime): End date of the range.
            service (IEventService, optional): The injected service dependency.

        Returns:
            Iterable: The event details collection.
        """
    start_date = start_date.replace(tzinfo=timezone.utc) if start_date.tzinfo is None else start_date
    end_date = end_date.replace(tzinfo=timezone.utc) if end_date.tzinfo is None else end_date

    if event := await service.get_by_date_range(start_date, end_date):
        return event

    raise HTTPException(status_code=404, detail="Event not found")

@router.get(
    "/user/{user_id}",
    response_model=Iterable[Event],
    status_code=200,
)
@inject
async def get_events_by_user(
        user_id: UUID4,
        service: IEventService = Depends(Provide[Container.event_service]),
) -> Iterable:
    """An endpoint for getting events by user who added them.

        Args:
            user_id (uuid): The uuid of the user.
            service (IEventService, optional): The injected service dependency.

        Returns:
            Iterable: The event details collection.
        """
    events = await service.get_by_user(user_id)

    if not events:
        raise HTTPException(status_code=404, detail=f"No events found for user id {user_id}")

    return events

@router.get(
    "/location/{location_id}",
    response_model=Iterable[Event],
    status_code=200,
)
@inject
async def get_events_by_location(
    location_id: int,
    service: IEventService = Depends(Provide[Container.event_service]),
) -> Iterable:
    """An endpoint for getting events by location_id.

    Args:
        location_id (int): The id of the location.
        service (IEventService, optional): The injected service dependency.

    Returns:
        Iterable: The event details collection.
    """

    events = await service.get_by_location(location_id)

    if not events:
        raise HTTPException(status_code=404, detail=f"No events found for location id {location_id}")

    return events


@router.put("/{event_id}", response_model=Event, status_code=201)
@inject
async def update_event(
        event_id: int,
        updated_event: EventIn,
        service: IEventService = Depends(Provide[Container.event_service]),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """An endpoint for updating event data.

    Args:
        event_id (int): The id of the event.
        updated_event (EventIn): The updated event details.
        service (IEventService, optional): The injected service dependency.
        credentials (HTTPAuthorizationCredentials, optional): The credentials.

    Raises:
        HTTPException: 403 if user is not authorized.
        HTTPException: 404 if event does not exist.

    Returns:
        dict: The updated event details.
    """

    token = credentials.credentials
    token_payload = jwt.decode(
        token,
        key=consts.SECRET_KEY,
        algorithms=[consts.ALGORITHM],
    )
    user_uuid = token_payload.get("sub")

    if not user_uuid:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Sprawdzenie, czy wydarzenie istnieje
    event_data = await service.get_by_id(event_id=event_id)
    if not event_data:
        raise HTTPException(status_code=404, detail="Event not found")

    # Sprawdzenie, czy użytkownik jest właścicielem wydarzenia
    if str(event_data.user_id) != user_uuid:
        raise HTTPException(status_code=403, detail="You are not allowed to update this event")

    # Rozszerzenie danych aktualizacji o ID użytkownika
    extended_updated_event = EventBroker(
        user_id=user_uuid,
        **updated_event.model_dump(),
    )

    # Weryfikacja konfliktów czasowych przed aktualizacją
    conflicting_events = await service.get_conflicting_events(
        location_id=extended_updated_event.location_id,
        start_time=extended_updated_event.start_time,
        end_time=extended_updated_event.end_time,
        exclude_event_id=event_id,
    )
    if conflicting_events:
        raise HTTPException(
            status_code=400,
            detail="Cannot update event. Overlapping events exist for the same location."
        )

    # Aktualizacja wydarzenia
    updated_event_data = await service.update_event(
        event_id=event_id,
        data=extended_updated_event,
    )
    return updated_event_data.model_dump() if updated_event_data else {}


@router.delete("/{event_id}", status_code=204)
@inject
async def delete_event(
        event_id: int,
        service: IEventService = Depends(Provide[Container.event_service]),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials
    token_payload = jwt.decode(token, key=consts.SECRET_KEY, algorithms=[consts.ALGORITHM])
    user_uuid = token_payload.get("sub")

    if not user_uuid:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Sprawdzenie, czy wydarzenie istnieje i należy do zalogowanego użytkownika
    event = await service.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.user_id != user_uuid:
        raise HTTPException(status_code=403, detail="You can only delete your own events")

    # Usuwanie wydarzenia
    await service.delete_event(event_id)

