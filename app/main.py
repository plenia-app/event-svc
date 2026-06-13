# app/main.py

from fastapi import FastAPI
from app.events.router import router as events_router

app = FastAPI(
    title="Plenia Event Service",
    version="1.0.0"
)

app.include_router(events_router)
