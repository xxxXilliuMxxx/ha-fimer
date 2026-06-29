"""Async API client for FIMER Aurora Vision."""

from __future__ import annotations

import base64
import json
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
    """Aurora Vision API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
    ):
        self._session = session
        self._username = username
        self._password = password

        self._token = None
        self._jwt = None

        self._portfolio_id = None
        self._plant_id = None

    @property
    def plant_id(self):
        return self._plant_id

    @property
    def portfolio_id(self):
        return self._portfolio_id

    async def login(self):
        """Login to Aurora Vision."""

        auth = aiohttp.BasicAuth(
            self._username,
            self._password,
        )

        async with self._session.get(
            LOGIN_URL,
            auth=auth,
            headers={
                "Accept": "application/json",
            },
        ) as response:

            if response.status == 401:
                raise AuthenticationError()

            #
            # Aurora Vision gebruikt mogelijk 2FA.
            #
            if response.status in (403, 412):
                raise TwoFactorRequired()

            response.raise_for_status()

            data = await response.json()

        self._token = data["token"]

        #
        # Cookie voor alle vervolgaanroepen.
        #
        self._session.cookie_jar.update_cookies(
            {
                "token.auroravision.net": self._token
            }
        )

        #
        # Decodeer JWT.
        #
        self._jwt = self._decode_jwt(self._token)

        #
        # Automatisch portfolio bepalen
        #
        self.discover_portfolio()

        #
        # Automatisch plant zoeken
        #
        await self.discover_plant()

        return data

    def _decode_jwt(self, token):
        """Decode JWT without verifying signature."""

        try:

            payload = token.split(".")[1]

            padding = "=" * (-len(payload) % 4)

            payload += padding

            decoded = base64.urlsafe_b64decode(payload)

            return json.loads(decoded)

        except Exception:

            return {}

    @property
    def jwt(self):
        return self._jwt

    def dump_jwt(self):
        """Debug helper."""

        print(json.dumps(self._jwt, indent=2))

    def discover_portfolio(self):
        """Find the first portfolio in the JWT."""

        if self._jwt is None:
            raise RuntimeError("Not logged in")

        try:
            portfolios = self._jwt["prl"]["portfolios"]

            #
            # Neem voorlopig de eerste portfolio.
            #
            self._portfolio_id = next(iter(portfolios.keys()))

            return self._portfolio_id

        except Exception as err:
            raise RuntimeError(
                "Unable to determine portfolio id"
            ) from err

    async def discover_plant(self):
        """Retrieve the first plant from the portfolio."""

        if self._portfolio_id is None:
            self.discover_portfolio()

        url = (
            f"{BASE_URL}/asset/v1/portfolios/"
            f"{self._portfolio_id}/plants"
        )

        params = {
            "includePerformanceProfiles": "true",
            "includePollutionConstants": "true",
        }

        async with self._session.get(
            url,
            params=params,
            headers={
                "Accept": "application/json",
            },
        ) as response:

            response.raise_for_status()

            plants = await response.json()

        if not plants:
            raise RuntimeError("No plants returned")

        #
        # Voor nu kiezen we de eerste plant.
        #
        self._plant_id = str(plants[0]["plantEntityID"])

        return self._plant_id

    async def _telemetry_request(
        self,
        category: str,
        metric: str,
        afx: str = AFX_LAST,
        agp: str = AGP,
    ):
        """Generic telemetry request."""

        if self._plant_id is None:
            raise RuntimeError("Plant not discovered")

        now = datetime.now().astimezone()

        sdt = now.strftime("%Y-%m-%dT00:00:00%z")
        edt = now.strftime("%Y-%m-%dT23:59:59%z")

        sdt = sdt[:-2] + ":" + sdt[-2:]
        edt = edt[:-2] + ":" + edt[-2:]

        url = (
            f"{BASE_URL}/telemetry/v1/plants/"
            f"{self._plant_id}/{category}/{metric}"
        )

        params = {
            "agp": agp,
            "afx": afx,
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

        async def generation_power(self):
        """Current PV power."""

        return await self._telemetry_request(
            "power",
            "GenerationPower",
            afx=AFX_LAST,
        )

        async def generation_energy_today(self):
        """Today's PV production."""

        return await self._telemetry_request(
            "energy",
            "GenerationEnergy",
            afx="Delta",
        )

        async def grid_power(self):
        """Grid power."""

        return await self._telemetry_request(
            "power",
            "GridPower",
            afx=AFX_LAST,
        )

        async def battery_power(self):
        """Battery charge/discharge power."""

        return await self._telemetry_request(
            "power",
            "BatteryPower",
            afx=AFX_LAST,
        )

        async def async_update(self):
        """Read all telemetry."""

        generation = await self.generation_power()
        energy = await self.generation_energy_today()

        try:
            grid = await self.grid_power()
        except Exception:
            grid = None

        try:
            battery = await self.battery_power()
        except Exception:
            battery = None

        return {
            "generation_power": generation,
            "generation_today": energy,
            "grid_power": grid,
            "battery_power": battery,
        }
