# app/events/service.py

from datetime import datetime

from app.core.auth_client import register_organizer
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
