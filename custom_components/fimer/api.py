from __future__ import annotations

import base64
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import aiohttp

_LOGGER = logging.getLogger(__name__)


class FimerApi:
    """Async API client for FIMER Aurora Vision."""

    def __init__(self, username: str, password: str, session: aiohttp.ClientSession):
        self._username = username
        self._password = password
        self._session = session

        self._token = None

    def _auth_header(self) -> dict:
        auth = f"{self._username}:{self._password}"
        encoded = base64.b64encode(auth.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    async def authenticate(self) -> None:
        """Placeholder authentication step (depends on FIMER API)."""
        # In real API: token endpoint call
        self._token = "mock-token"

    async def get_plant_data(self, plant_id: str) -> dict:
        """Fetch plant/inverter data."""
        url = f"https://api.fimer.com/plants/{plant_id}/data"

        headers = {
            **self._auth_header(),
            "Accept": "application/json",
        }

        async with self._session.get(url, headers=headers, timeout=20) as resp:
            if resp.status != 200:
                text = await resp.text()
                _LOGGER.error("API error %s: %s", resp.status, text)
                raise Exception(f"API error: {resp.status}")

            return await resp.json()

    def parse_timestamp(self, ts: str) -> datetime:
        """Parse API timestamp."""
        return datetime.fromisoformat(ts).astimezone(ZoneInfo("UTC"))
