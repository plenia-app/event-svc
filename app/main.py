# app/main.py

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.events.router import router as events_router

app = FastAPI(
    title="Plenia Event Service",
    version="1.0.0",
    description=(
        "API for creating events and managing their organizers. "
        "Interactive Swagger documentation is available at `/docs`; "
        "the OpenAPI schema is available at `/openapi.json`."
    ),
    openapi_tags=[
        {
            "name": "Events",
            "description": "Event creation and organizer management endpoints.",
        }
    ],
)

app.include_router(events_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", include_in_schema=False)
async def frontend():
    return FileResponse(Path("app/static/index.html"))
