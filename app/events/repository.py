# app/events/repository.py

from app.core.database import db
from app.core.config import EVENTS_COLLECTION
from bson import ObjectId
from datetime import datetime


class EventRepository:

    def __init__(self):
        self.collection = db[EVENTS_COLLECTION]

    async def insert_event(self, event: dict):
        result = await self.collection.insert_one(event)
        return str(result.inserted_id)

    async def find_by_id(self, event_id: str):
        if not ObjectId.is_valid(event_id):
            return None

        return await self.collection.find_one({"_id": ObjectId(event_id)})

    async def update_event(self, event_id: str, update: dict):
        update["updated_at"] = datetime.utcnow()
        await self.collection.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": update}
        )

    async def add_organizer(self, event_id: str, organizer: dict):
        return await self.add_organizers(event_id, [organizer])

    async def add_organizers(self, event_id: str, organizers: list[dict]):
        if not ObjectId.is_valid(event_id):
            return False

        if not organizers:
            return True

        result = await self.collection.update_one(
            {"_id": ObjectId(event_id)},
            {
                "$push": {"organizers": {"$each": organizers}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        return result.modified_count == 1
