# app/events/schemas.py

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class GeoLocationInput(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None


class CreateEventRequest(BaseModel):
    creator_id: str

    name: str
    description: Optional[str] = None

    start_date: datetime
    end_date: datetime

    location_name: Optional[str] = None
    geo_location: Optional[GeoLocationInput] = None


class CreateEventResponse(BaseModel):
    event_id: str


class OrganizerInput(BaseModel):
    email: str
    role: str = "organizer"


class AddOrganizersRequest(BaseModel):
    organizers: List[OrganizerInput] = Field(min_length=1)


class AddOrganizersResponse(BaseModel):
    event_id: str
    organizer_ids: List[str]
    skipped: List[str] = Field(default_factory=list)
