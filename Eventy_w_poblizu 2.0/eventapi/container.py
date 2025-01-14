"""Module providing containers injecting dependencies."""

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Singleton

from eventapi.infrastructure.repositories.user import UserRepository
from eventapi.infrastructure.repositories.eventdb import \
    EventRepository
from eventapi.infrastructure.repositories.locationdb import \
    LocationRepository
from eventapi.infrastructure.repositories.reviewdb import ReviewRepository

from eventapi.infrastructure.services.event import EventService
from eventapi.infrastructure.services.location import LocationService
from eventapi.infrastructure.services.user import UserService
from eventapi.infrastructure.services.review import ReviewService


class Container(DeclarativeContainer):
    """Container class for dependency injecting purposes."""
    location_repository = Singleton(LocationRepository)
    event_repository = Singleton(EventRepository)
    user_repository = Singleton(UserRepository)
    review_repository = Singleton(ReviewRepository)

    location_service = Factory(
        LocationService,
        repository=location_repository,
    )

    event_service = Factory(
        EventService,
        repository=event_repository,
    )
    user_service = Factory(
        UserService,
        repository=user_repository,
    )
    review_service = Factory(
        ReviewService,
        repository=review_repository,
    )
