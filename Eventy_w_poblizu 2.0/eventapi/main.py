"""Main module of the app"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.exception_handlers import http_exception_handler
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.security import OAuth2

from eventapi.api.routers.event_router import router as event_router
from eventapi.api.routers.location_router import router as location_router
from eventapi.api.routers.user_router import router as user_router
from eventapi.api.routers.review_router import router as review_router
from eventapi.container import Container
from eventapi.db import database, init_db

container = Container()
container.wire(modules=[
    "eventapi.api.routers.event_router",
    "eventapi.api.routers.location_router",
    "eventapi.api.routers.user_router",
    "eventapi.api.routers.review_router",
])


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    """Lifespan function working on app startup."""
    await init_db()
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

# Dodanie HTTPBearer dla lepszego zabezpieczenia
bearer_scheme = HTTPBearer()

# Dodanie routerów
app.include_router(event_router, prefix="/event")
app.include_router(location_router, prefix="/location")
app.include_router(user_router, prefix="/user")
app.include_router(review_router, prefix="/router")

@app.exception_handler(HTTPException)
async def http_exception_handle_logging(
        request: Request,
        exception: HTTPException,
) -> Response:
    """A function handling http exceptions for logging purposes.

    Args:
        request (Request): The incoming HTTP request.
        exception (HTTPException): A related exception.

    Returns:
        Response: The HTTP response.
    """
    return await http_exception_handler(request, exception)

