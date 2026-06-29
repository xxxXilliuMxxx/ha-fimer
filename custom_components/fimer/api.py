"""Async API client for FIMER Aurora Vision."""

from __future__ import annotations

from datetime import datetime

import aiohttp

from .const import (
    LOGIN_URL,
    BASE_URL,
    AGP,
    AFX_LAST,
)


class AuthenticationError(Exception):
    """Authentication failed."""


class TwoFactorRequired(Exception):
    """Raised when Aurora Vision requires a second authentication step."""


class FimerApi:

    def __init__(self, session: aiohttp.ClientSession, username: str, password: str):
        self._session = session
        self._username = username
        self._password = password

        self._token = None
        self._plant_id = None

    @property
    def plant_id(self):
        return self._plant_id

    async def login(self):
        """Login to Aurora Vision."""

        auth = aiohttp.BasicAuth(self._username, self._password)

        async with self._session.get(
            LOGIN_URL,
            auth=auth,
            headers={"Accept": "application/json"},
        ) as response:

            if response.status == 401:
                raise AuthenticationError()

            if response.status == 403:
                raise TwoFactorRequired()

            response.raise_for_status()

            data = await response.json()

        self._token = data["token"]

        #
        # Aurora Vision gebruikt een cookie.
        #
        self._session.cookie_jar.update_cookies(
            {
                "token.auroravision.net": self._token
            }
        )

        return data

    async def discover_plant(self):
        """
        Wordt later ingevuld.

        Hier halen we automatisch plantEntityID op.
        """

        raise NotImplementedError()

    async def generation_power(self):

        if self._plant_id is None:
            raise RuntimeError("Plant not discovered")

        today = datetime.now().astimezone()

        sdt = today.strftime("%Y-%m-%dT00:00:00%z")
        edt = today.strftime("%Y-%m-%dT23:59:59%z")

        sdt = sdt[:-2] + ":" + sdt[-2:]
        edt = edt[:-2] + ":" + edt[-2:]

        url = (
            f"{BASE_URL}/telemetry/v1/plants/"
            f"{self._plant_id}/power/GenerationPower"
        )

        params = {
            "agp": AGP,
            "afx": AFX_LAST,
            "sdt": sdt,
            "edt": edt,
        }

        async with self._session.get(
            url,
            params=params,
            headers={
                "Accept": "application/json",
            },
        ) as response:

            response.raise_for_status()

            return await response.json()
