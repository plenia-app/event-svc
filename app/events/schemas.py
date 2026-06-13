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


class DeleteEventResponse(BaseModel):
    event_id: str = Field(
        ...,
        description="MongoDB ObjectId of the deleted event.",
        example="665f0f4a9a4e6b9a1f4c2d33",
    )
    deleted_stands: int = Field(0, description="Embedded stand requests removed with the event.")
    deleted_company_speakers: int = Field(0, description="Embedded company speakers removed with the event.")
    deleted_organizers: int = Field(0, description="Organizer links removed with the event.")
    deleted_speeches: int = Field(0, description="Confirmed speech-svc speeches removed with the event.")
    deleted_materials: int = Field(0, description="Speech material records removed with the event.")
    deleted_live_sessions: int = Field(0, description="Speech live session records removed with the event.")

    class Config:
        schema_extra = {
            "example": {
                "event_id": "665f0f4a9a4e6b9a1f4c2d33",
                "deleted_stands": 2,
                "deleted_company_speakers": 3,
                "deleted_organizers": 1,
                "deleted_speeches": 2,
                "deleted_materials": 4,
                "deleted_live_sessions": 1,
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


class EventOrganizerOut(BaseModel):
    user_id: str
    email: Optional[str] = None
    role: str


class StandRequest(BaseModel):
    company_id: str
    company_name: str
    contact_email: str
    stand_name: str
    description: Optional[str] = None


class StandOut(StandRequest):
    id: str
    event_id: str
    status: str
    created_at: datetime
    updated_at: datetime


class CompanySpeakerRequest(BaseModel):
    company_id: str
    company_name: str
    email: str
    first_name: str
    last_name: str
    title: Optional[str] = None
    bio: Optional[str] = None


class SpeakerSpeechInfo(BaseModel):
    speech_id: str
    title: str
    description: Optional[str] = None
    source_language: str = "it"
    target_languages: List[str] = Field(default_factory=list)
    materials_count: int = 0


class CompanySpeakerConfirmRequest(SpeakerSpeechInfo):
    pass


class CompanySpeakerOut(CompanySpeakerRequest):
    id: str
    event_id: str
    confirmed: bool = False
    speech: Optional[SpeakerSpeechInfo] = None
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None


class EventOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    location_name: Optional[str] = None
    geo_location: Optional[GeoLocationInput] = None
    created_by: str
    organizers: List[EventOrganizerOut] = Field(default_factory=list)
    stands: List[StandOut] = Field(default_factory=list)
    company_speakers: List[CompanySpeakerOut] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
