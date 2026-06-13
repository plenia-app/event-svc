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

    async def delete_by_id(self, event_id: str):
        if not ObjectId.is_valid(event_id):
            return False

        result = await self.collection.delete_one({"_id": ObjectId(event_id)})
        return result.deleted_count == 1

    async def list_events(self, user_id: str | None = None):
        query = {}
        if user_id:
            query = {
                "$or": [
                    {"created_by": user_id},
                    {"organizers.user_id": user_id},
                    {"organizers.email": user_id},
                ]
            }

        cursor = self.collection.find(query).sort("start_date", 1)
        return await cursor.to_list(length=200)

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

    async def add_stand(self, event_id: str, stand: dict):
        if not ObjectId.is_valid(event_id):
            return False

        result = await self.collection.update_one(
            {"_id": ObjectId(event_id)},
            {
                "$push": {"stands": stand},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count == 1

    async def update_stand_status(self, event_id: str, stand_id: str, status: str):
        if not ObjectId.is_valid(event_id):
            return False

        now = datetime.utcnow()
        result = await self.collection.update_one(
            {
                "_id": ObjectId(event_id),
                "stands.id": stand_id,
            },
            {
                "$set": {
                    "stands.$.status": status,
                    "stands.$.updated_at": now,
                    "updated_at": now,
                }
            }
        )
        return result.modified_count == 1

    async def add_company_speaker(self, event_id: str, speaker: dict):
        if not ObjectId.is_valid(event_id):
            return False

        result = await self.collection.update_one(
            {"_id": ObjectId(event_id)},
            {
                "$push": {"company_speakers": speaker},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count == 1

    async def confirm_company_speaker(self, event_id: str, speaker_id: str, speech: dict):
        if not ObjectId.is_valid(event_id):
            return False

        now = datetime.utcnow()
        result = await self.collection.update_one(
            {
                "_id": ObjectId(event_id),
                "company_speakers.id": speaker_id,
            },
            {
                "$set": {
                    "company_speakers.$.confirmed": True,
                    "company_speakers.$.speech": speech,
                    "company_speakers.$.confirmed_at": now,
                    "company_speakers.$.updated_at": now,
                    "updated_at": now,
                }
            }
        )
        return result.modified_count == 1
