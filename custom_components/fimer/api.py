from __future__ import annotations

import base64
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from aiohttp import ClientResponseError, ClientSession
from yarl import URL

_LOGGER = logging.getLogger(__name__)


class FimerApi:
    """Async Aurora Vision API."""

    AUTH_URL = "https://m.auroravision.net"
    API_URL = "https://www.auroravision.net"

    def __init__(
        self,
        session: ClientSession,
        username: str,
        password: str,
        plant_id: str,
    ) -> None:
        self._session = session
        self._username = username
        self._password = password
        self._plant_id = plant_id
        self._token: str | None = None

    async def login(self) -> None:
        """Authenticate."""

        auth = base64.b64encode(
            f"{self._username}:{self._password}".encode()
        ).decode()

        headers = {
            "Authorization": f"Basic {auth}",
            "Accept": "application/json",
        }

        async with self._session.get(
            f"{self.AUTH_URL}/ums/v1/login",
            headers=headers,
        ) as response:

            response.raise_for_status()

            data = await response.json()

        self._token = data["token"]

        self._session.cookie_jar.update_cookies(
            {
                "token.auroravision.net": self._token,
            },
            response_url=URL(self.API_URL),
        )

        _LOGGER.debug("Aurora Vision login successful")

    def _today(self) -> tuple[str, str]:

        tz = ZoneInfo("Europe/Amsterdam")

        now = datetime.now(tz)

        start = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        end = now.replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=0,
        )

        return (
            start.isoformat(timespec="seconds"),
            end.isoformat(timespec="seconds"),
        )

    async def _request(
        self,
        path: str,
        params: dict,
    ) -> list:

        if self._token is None:
            await self.login()

        headers = {
            "Accept": "application/json",
            "Referer": "https://www.auroravision.net/eview/",
            "User-Agent": "Home Assistant",
        }

        url = f"{self.API_URL}{path}"

        try:

            async with self._session.get(
                url,
                params=params,
                headers=headers,
            ) as response:

                if response.status == 401:
                    raise ClientResponseError(
                        response.request_info,
                        response.history,
                        status=401,
                    )

                response.raise_for_status()

                return await response.json()

        except ClientResponseError as err:

            if err.status != 401:
                raise

            _LOGGER.debug("Token expired, logging in again")

            await self.login()

            async with self._session.get(
                url,
                params=params,
                headers=headers,
            ) as response:

                response.raise_for_status()

                return await response.json()

    async def telemetry(
        self,
        category: str,
        metric: str,
        afx: str = "Last",
    ) -> list:

        sdt, edt = self._today()

        params = {
            "agp": "All",
            "afx": afx,
            "sdt": sdt,
            "edt": edt,
        }

        return await self._request(
            f"/telemetry/v1/plants/{self._plant_id}/{category}/{metric}",
            params,
        )

    async def kpi(
        self,
        metric: str,
        afx: str = "Last",
    ) -> list:

        sdt, edt = self._today()

        params = {
            "agp": "All",
            "afx": afx,
            "sdt": sdt,
            "edt": edt,
        }

        return await self._request(
            f"/kpi/v1/plants/{self._plant_id}/kpi/{metric}",
            params,
        )

    async def get_power(
        self,
        metric: str,
    ) -> float | None:

        data = await self.telemetry(
            "power",
            metric,
        )

        if not data:
            return None

        return float(data[0]["value"])

    async def get_energy(
        self,
        metric: str,
        delta: bool = False,
    ) -> float | None:

        data = await self.telemetry(
            "energy",
            metric,
            afx="Delta" if delta else "Last",
        )

        if not data:
            return None

        return float(data[-1]["value"])

    async def get_kpi(
        self,
        metric: str,
    ) -> float | None:

        data = await self.kpi(metric)

        if not data:
            return None

        return float(data[0]["value"])

    async def get_data(self) -> dict:

        return {
            "generation_power": await self.get_power("GenerationPower"),
            "grid_power": await self.get_power("GridPower"),
            "battery_power": await self.get_power("StoragePower"),
            "generation_energy_today": await self.get_energy(
                "GenerationEnergy",
                delta=True,
            ),
            "generation_energy_total": await self.get_energy(
                "GenerationEnergy",
            ),
        }
