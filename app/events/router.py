# app/events/router.py

from fastapi import APIRouter, Depends, HTTPException, status
import httpx

from app.events.schemas import AddOrganizersRequest, AddOrganizersResponse, CreateEventRequest, CreateEventResponse
from app.events.service import EventService

router = APIRouter(prefix="/events", tags=["Events"])


def get_service():
    return EventService()


@router.post("", response_model=CreateEventResponse)
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
    status_code=status.HTTP_201_CREATED
)
async def add_organizers(
    event_id: str,
    request: AddOrganizersRequest,
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
