# app/events/service.py

from datetime import datetime
from uuid import uuid4

import httpx

from app.core.auth_client import register_organizer, register_speaker
from app.core.config import SPEECH_DELETE_URL
from app.events.repository import EventRepository


class EventService:

    def __init__(self):
        self.repo = EventRepository()

    async def create_event(self, data: dict, creator_id: str):

        event = {
            **data,
            "created_by": creator_id,
            "organizers": [
                {
                    "user_id": creator_id,
                    "role": "owner"
                }
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        return await self.repo.insert_event(event)

    def serialize_event(self, event: dict):
        return {
            "id": str(event["_id"]),
            "name": event["name"],
            "description": event.get("description"),
            "start_date": event["start_date"],
            "end_date": event["end_date"],
            "location_name": event.get("location_name"),
            "geo_location": event.get("geo_location"),
            "created_by": event["created_by"],
            "organizers": event.get("organizers", []),
            "stands": event.get("stands", []),
            "company_speakers": event.get("company_speakers", []),
            "created_at": event.get("created_at"),
            "updated_at": event.get("updated_at"),
        }

    async def list_events(self, user_id: str | None = None):
        events = await self.repo.list_events(user_id=user_id)
        return [self.serialize_event(event) for event in events]

    async def get_event(self, event_id: str):
        event = await self.repo.find_by_id(event_id)
        if event is None:
            return None
        return self.serialize_event(event)

    async def delete_event(self, event_id: str):
        event = await self.repo.find_by_id(event_id)
        if event is None:
            return None

        speech_ids = [
            speaker["speech"]["speech_id"]
            for speaker in event.get("company_speakers", [])
            if speaker.get("speech") and speaker["speech"].get("speech_id")
        ]
        speech_cleanup = {
            "deleted_speeches": 0,
            "deleted_materials": 0,
            "deleted_live_sessions": 0,
        }
        if speech_ids:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.request(
                    "DELETE",
                    SPEECH_DELETE_URL,
                    json={"speech_ids": speech_ids},
                )
                response.raise_for_status()
                speech_cleanup.update(response.json())

        deleted = await self.repo.delete_by_id(event_id)
        if not deleted:
            return False

        return {
            "event_id": event_id,
            "deleted_stands": len(event.get("stands", [])),
            "deleted_company_speakers": len(event.get("company_speakers", [])),
            "deleted_organizers": len(event.get("organizers", [])),
            "deleted_speeches": speech_cleanup["deleted_speeches"],
            "deleted_materials": speech_cleanup["deleted_materials"],
            "deleted_live_sessions": speech_cleanup["deleted_live_sessions"],
        }

    async def add_organizers(self, event_id: str, organizers):
        event = await self.repo.find_by_id(event_id)
        if event is None:
            return None

        existing_emails = {
            organizer.get("email") or organizer.get("user_id")
            for organizer in event.get("organizers", [])
        }
        seen_emails = set()
        skipped = []
        organizers_to_add = []

        for organizer_request in organizers:
            email = organizer_request.email
            if email in existing_emails or email in seen_emails:
                skipped.append(email)
                continue

            seen_emails.add(email)
            await register_organizer(email)
            organizers_to_add.append({
                "user_id": email,
                "email": email,
                "role": organizer_request.role
            })

        added = [organizer["email"] for organizer in organizers_to_add]
        saved = await self.repo.add_organizers(event_id, organizers_to_add)
        if not saved:
            return False

        return {
            "added": added,
            "skipped": skipped,
        }

    async def add_stand(self, event_id: str, stand_request):
        event = await self.repo.find_by_id(event_id)
        if event is None:
            return None

        stand = {
            "id": str(uuid4()),
            "event_id": event_id,
            "company_id": stand_request.company_id,
            "company_name": stand_request.company_name,
            "contact_email": stand_request.contact_email,
            "stand_name": stand_request.stand_name,
            "description": stand_request.description,
            "status": "requested",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        saved = await self.repo.add_stand(event_id, stand)
        if not saved:
            return False
        return stand

    async def update_stand_status(self, event_id: str, stand_id: str, status: str):
        event = await self.repo.find_by_id(event_id)
        if event is None:
            return None

        saved = await self.repo.update_stand_status(event_id, stand_id, status)
        if not saved:
            return False

        updated = await self.repo.find_by_id(event_id)
        stands = updated.get("stands", []) if updated else []
        return next((stand for stand in stands if stand.get("id") == stand_id), False)

    async def add_company_speaker(self, event_id: str, speaker_request):
        event = await self.repo.find_by_id(event_id)
        if event is None:
            return None

        await register_speaker(
            email=speaker_request.email,
            first_name=speaker_request.first_name,
            last_name=speaker_request.last_name,
        )

        speaker = {
            "id": str(uuid4()),
            "event_id": event_id,
            "company_id": speaker_request.company_id,
            "company_name": speaker_request.company_name,
            "email": speaker_request.email,
            "first_name": speaker_request.first_name,
            "last_name": speaker_request.last_name,
            "title": speaker_request.title,
            "bio": speaker_request.bio,
            "confirmed": False,
            "speech": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        saved = await self.repo.add_company_speaker(event_id, speaker)
        if not saved:
            return False
        return speaker

    async def confirm_company_speaker(self, event_id: str, speaker_id: str, confirmation):
        event = await self.repo.find_by_id(event_id)
        if event is None:
            return None

        speech = {
            "speech_id": confirmation.speech_id,
            "title": confirmation.title,
            "description": confirmation.description,
            "source_language": confirmation.source_language,
            "target_languages": confirmation.target_languages,
            "materials_count": confirmation.materials_count,
        }

        saved = await self.repo.confirm_company_speaker(event_id, speaker_id, speech)
        if not saved:
            return False

        updated = await self.repo.find_by_id(event_id)
        speakers = updated.get("company_speakers", []) if updated else []
        return next((speaker for speaker in speakers if speaker.get("id") == speaker_id), False)
