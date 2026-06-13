# app/core/config.py

import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "event_svc")
EVENTS_COLLECTION = os.getenv("EVENTS_COLLECTION", "events")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:3001").rstrip("/")
AUTH_REGISTER_ORGANIZER_URL = f"{AUTH_SERVICE_URL}/auth/signup/organizer"
AUTH_REGISTER_SPEAKER_URL = f"{AUTH_SERVICE_URL}/auth/signup/speaker"

SPEECH_SERVICE_URL = os.getenv("SPEECH_SERVICE_URL", "http://localhost:3003").rstrip("/")
SPEECH_DELETE_URL = f"{SPEECH_SERVICE_URL}/internal/speeches"
