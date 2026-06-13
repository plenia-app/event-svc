# app/events/schemas.py

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class GeoLocationInput(BaseModel):
    latitude: float = Field(
        ...,
        description="Latitude in decimal degrees.",
        example=45.4642,
    )
    longitude: float = Field(
        ...,
        description="Longitude in decimal degrees.",
        example=9.1900,
    )
    address: Optional[str] = Field(
        None,
        description="Human-readable address for the event location.",
        example="Piazza del Duomo, Milano",
    )

    class Config:
        schema_extra = {
            "example": {
                "latitude": 45.4642,
                "longitude": 9.1900,
                "address": "Piazza del Duomo, Milano",
            }
        }


class CreateEventRequest(BaseModel):
    creator_id: str = Field(
        ...,
        description=(
            "User id of the event creator. The creator is stored as the "
            "event owner."
        ),
        example="user_123",
    )

    name: str = Field(
        ...,
        description="Public event name.",
        example="Plenia Community Meetup",
    )
    description: Optional[str] = Field(
        None,
        description="Optional event description.",
        example="An evening meetup for the Plenia community.",
    )

    start_date: datetime = Field(
        ...,
        description="Event start date and time in ISO 8601 format.",
        example="2026-07-01T18:00:00Z",
    )
    end_date: datetime = Field(
        ...,
        description="Event end date and time in ISO 8601 format.",
        example="2026-07-01T21:00:00Z",
    )

    location_name: Optional[str] = Field(
        None,
        description="Display name of the event location.",
        example="Milano Innovation Hub",
    )
    geo_location: Optional[GeoLocationInput] = Field(
        None,
        description="Optional geographic coordinates for the event location.",
    )

    class Config:
        schema_extra = {
            "example": {
                "creator_id": "user_123",
                "name": "Plenia Community Meetup",
                "description": "An evening meetup for the Plenia community.",
                "start_date": "2026-07-01T18:00:00Z",
                "end_date": "2026-07-01T21:00:00Z",
                "location_name": "Milano Innovation Hub",
                "geo_location": {
                    "latitude": 45.4642,
                    "longitude": 9.1900,
                    "address": "Piazza del Duomo, Milano",
                },
            }
        }


class CreateEventResponse(BaseModel):
    event_id: str = Field(
        ...,
        description="MongoDB ObjectId of the created event.",
        example="665f0f4a9a4e6b9a1f4c2d33",
    )

    class Config:
        schema_extra = {
            "example": {
                "event_id": "665f0f4a9a4e6b9a1f4c2d33",
            }
        }


class OrganizerInput(BaseModel):
    email: str = Field(
        ...,
        description=(
            "Organizer email address. It is also used as the organizer user id."
        ),
        example="organizer@example.com",
    )
    role: str = Field(
        "organizer",
        description="Role assigned to the organizer for this event.",
        example="organizer",
    )

    class Config:
        schema_extra = {
            "example": {
                "email": "organizer@example.com",
                "role": "organizer",
            }
        }


class AddOrganizersRequest(BaseModel):
    organizers: List[OrganizerInput] = Field(
        ...,
        min_length=1,
        description=(
            "Organizers to add to the event. Duplicate emails are skipped."
        ),
    )

    class Config:
        schema_extra = {
            "example": {
                "organizers": [
                    {
                        "email": "organizer@example.com",
                        "role": "organizer",
                    },
                    {
                        "email": "host@example.com",
                        "role": "host",
                    },
                ]
            }
        }


class AddOrganizersResponse(BaseModel):
    event_id: str = Field(
        ...,
        description="MongoDB ObjectId of the updated event.",
        example="665f0f4a9a4e6b9a1f4c2d33",
    )
    organizer_ids: List[str] = Field(
        ...,
        description="Emails of organizers successfully added to the event.",
        example=["organizer@example.com", "host@example.com"],
    )
    skipped: List[str] = Field(
        default_factory=list,
        description=(
            "Emails skipped because they already existed or were duplicated "
            "in the request."
        ),
        example=["existing@example.com"],
    )

    class Config:
        schema_extra = {
            "example": {
                "event_id": "665f0f4a9a4e6b9a1f4c2d33",
                "organizer_ids": ["organizer@example.com", "host@example.com"],
                "skipped": ["existing@example.com"],
            }
        }


class ErrorResponse(BaseModel):
    detail: str = Field(
        ...,
        description="Error description.",
        example="Event not found",
    )

    class Config:
        schema_extra = {
            "example": {
                "detail": "Event not found",
            }
        }
