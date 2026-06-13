# app/core/auth_client.py

import httpx

from app.core.config import AUTH_REGISTER_ORGANIZER_URL, AUTH_REGISTER_SPEAKER_URL

DEFAULT_REGISTRATION_PASSWORD = "password"
USER_ALREADY_EXISTS_MESSAGE = "user already exists"


def _organizer_names_from_email(email: str) -> tuple[str, str]:
    local_part = email.split("@", 1)[0].strip()
    if not local_part:
        return "Organizer", "User"

    normalized = local_part.replace(".", " ").replace("_", " ").replace("-", " ")
    parts = [part.capitalize() for part in normalized.split() if part]
    if not parts:
        return "Organizer", "User"
    if len(parts) == 1:
        return parts[0], "User"
    return parts[0], " ".join(parts[1:])


async def register_organizer(email: str) -> httpx.Response:
    first_name, last_name = _organizer_names_from_email(email)

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            AUTH_REGISTER_ORGANIZER_URL,
            json={
                "email": email,
                "password": DEFAULT_REGISTRATION_PASSWORD,
                "first_name": first_name,
                "last_name": last_name,
            },
        )

    if response.is_error and USER_ALREADY_EXISTS_MESSAGE in response.text.lower():
        return response

    response.raise_for_status()
    return response


async def register_speaker(email: str, first_name: str, last_name: str) -> httpx.Response:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            AUTH_REGISTER_SPEAKER_URL,
            json={
                "email": email,
                "password": DEFAULT_REGISTRATION_PASSWORD,
                "first_name": first_name,
                "last_name": last_name,
            },
        )

    if response.is_error and USER_ALREADY_EXISTS_MESSAGE in response.text.lower():
        return response

    response.raise_for_status()
    return response
