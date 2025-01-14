from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import UUID4

from eventapi.infrastructure.services.ireview import IReviewService
from eventapi.infrastructure.services.review import ReviewService
from eventapi.infrastructure.dto.reviewdto import ReviewDTO
from eventapi.core.domain.review import ReviewIn, ReviewBroker, Review
from eventapi.container import Container
from eventapi.infrastructure.utils import consts
from jose import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from dependency_injector.wiring import inject, Provide

bearer_scheme = HTTPBearer()

router = APIRouter()

# Dependency injection: ReviewService
def get_review_service() -> ReviewService:
    return Container.review_service()


@router.get("/create", response_model=List[ReviewDTO])
async def get_all_reviews(service: ReviewService = Depends(get_review_service)):
    """Retrieve all reviews."""
    return await service.get_all_reviews()


@router.get("/review/{review_id}", response_model=ReviewDTO)
async def get_review_by_id(review_id: int, service: ReviewService = Depends(get_review_service)):
    """Retrieve a review by its ID."""
    review = await service.get_review_by_id(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )
    return review


@router.get("/user/{user_id}", response_model=List[ReviewDTO])
async def get_reviews_by_user(
    user_id: UUID4,  # Zmieniono z int na UUID4
    service: ReviewService = Depends(get_review_service),
):
    """Retrieve all reviews by a specific user."""
    return await service.get_reviews_by_user(user_id)


@router.get("/event/{event_id}", response_model=List[ReviewDTO])
async def get_reviews_by_event(event_id: int, service: ReviewService = Depends(get_review_service)):
    """Retrieve all reviews for a specific event."""
    return await service.get_reviews_by_event(event_id)


@router.post("/create", response_model=ReviewDTO, status_code=status.HTTP_201_CREATED)
async def create_review(
    data: ReviewIn,
    service: ReviewService = Depends(get_review_service),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials
    token_payload = jwt.decode(
        token,
        key=consts.SECRET_KEY,
        algorithms=[consts.ALGORITHM],
    )
    user_uuid = token_payload.get("sub")

    if not user_uuid:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Extend data with user_id
    extended_review_data = ReviewBroker(user_id=user_uuid, **data.model_dump())
    return await service.create_review(extended_review_data)

@router.put("/update/{review_id}", response_model=Review)
@inject
async def update_review(
        review_id: int,
        updated_review: ReviewIn,
        service: IReviewService = Depends(Provide[Container.review_service]),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Update a review. Only the owner of the review can perform this operation.

    Args:
        review_id (int): ID of the review to update.
        updated_review (ReviewIn): The updated review data.
        service (IReviewService): Review service.
        credentials (HTTPAuthorizationCredentials): User credentials.

    Returns:
        dict: Updated review details.
    """
    # Decode token and retrieve user UUID
    token = credentials.credentials
    token_payload = jwt.decode(token, key=consts.SECRET_KEY, algorithms=[consts.ALGORITHM])
    user_uuid = token_payload.get("sub")

    if not user_uuid:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Check if review exists and belongs to the user
    review = await service.get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if str(review.user_id) != user_uuid:
        raise HTTPException(status_code=403, detail="You are not allowed to update this review")

    # Update review
    updated_review_data = await service.update_review(review_id, ReviewBroker(user_id=user_uuid, **updated_review.model_dump()))
    return updated_review_data.model_dump() if updated_review_data else {}

@router.delete("/delete/{review_id}", status_code=204)
@inject
async def delete_review(
        review_id: int,
        service: IReviewService = Depends(Provide[Container.review_service]),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """
    Delete a review. Only the owner of the review can perform this operation.

    Args:
        review_id (int): ID of the review to delete.
        service (IReviewService): Review service.
        credentials (HTTPAuthorizationCredentials): User credentials.

    Raises:
        HTTPException: If the review is not found or the user is not authorized.
    """
    # Decode token and retrieve user UUID
    token = credentials.credentials
    token_payload = jwt.decode(token, key=consts.SECRET_KEY, algorithms=[consts.ALGORITHM])
    user_uuid = token_payload.get("sub")

    if not user_uuid:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Check if review exists and belongs to the user
    review = await service.get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if str(review.user_id) != user_uuid:
        raise HTTPException(status_code=403, detail="You are not allowed to delete this review")

    # Delete review
    await service.delete_review(review_id)
