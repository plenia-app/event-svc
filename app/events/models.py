# app/events/models.py

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class DayTimeRange(BaseModel):
    date: datetime
    start_time: datetime
    end_time: datetime


class Organizer(BaseModel):
    user_id: str
    email: Optional[str] = None
    role: str = "organizer"


class GeoLocation(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None


class Event(BaseModel):
    id: Optional[str] = None

    name: str
    description: Optional[str] = None

    start_date: datetime
    end_date: datetime

    location_name: Optional[str] = None
    geo_location: Optional[GeoLocation] = None

    created_by: str

    organizers: List[Organizer] = []

    daily_time_ranges: List[DayTimeRange] = []

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
