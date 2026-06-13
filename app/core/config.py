# app/core/config.py

import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "event_svc")
EVENTS_COLLECTION = os.getenv("EVENTS_COLLECTION", "events")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8080").rstrip("/")
AUTH_REGISTER_ORGANIZER_URL = f"{AUTH_SERVICE_URL}/auth/signup/organizer"
