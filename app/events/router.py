# app/events/router.py

from fastapi import APIRouter, Depends, HTTPException, Path, status
import httpx

from app.events.schemas import (
    AddOrganizersRequest,
    AddOrganizersResponse,
    CreateEventRequest,
    CreateEventResponse,
    ErrorResponse,
)
from app.events.service import EventService

router = APIRouter(prefix="/events", tags=["Events"])


def get_service():
    return EventService()


@router.post(
    "",
    response_model=CreateEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create event",
    description=(
        "Creates a new event and stores the request `creator_id` as the owner "
        "inside the event organizers list."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "description": "Event created successfully.",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Invalid request body.",
        },
    },
)
async def create_event(
    request: CreateEventRequest,
    service: EventService = Depends(get_service),
):
    event_id = await service.create_event(
        data=request.dict(exclude={"creator_id"}),
        creator_id=request.creator_id
    )

    return CreateEventResponse(
        event_id=event_id,
    )


@router.post(
    "/{event_id}/organizers",
    response_model=AddOrganizersResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add organizers to event",
    description=(
        "Registers each organizer with the auth service and appends new organizers "
        "to the event. Emails that already exist on the event or are duplicated in "
        "the same request are returned in `skipped`."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "description": (
                "Organizers added successfully. Duplicate emails may be "
                "returned in `skipped`."
            ),
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "The event id is invalid or the event does not exist.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "The organizers could not be saved to the event.",
        },
        status.HTTP_502_BAD_GATEWAY: {
            "model": ErrorResponse,
            "description": (
                "Organizer registration failed or the auth service is "
                "unavailable."
            ),
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Invalid request body or path parameter.",
        },
    },
)
async def add_organizers(
    request: AddOrganizersRequest,
    event_id: str = Path(
        ...,
        description="MongoDB ObjectId of the event.",
        example="665f0f4a9a4e6b9a1f4c2d33",
    ),
    service: EventService = Depends(get_service),
):
    try:
        result = await service.add_organizers(
            event_id=event_id,
            organizers=request.organizers,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Organizer registration failed: {exc.response.text}",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Auth service unavailable: {exc}",
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    if result is False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organizers could not be added"
        )

    return AddOrganizersResponse(
        event_id=event_id,
        organizer_ids=result["added"],
        skipped=result["skipped"],
    )
