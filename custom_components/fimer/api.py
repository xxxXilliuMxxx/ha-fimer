from __future__ import annotations

import base64
from datetime import datetime
from zoneinfo import ZoneInfo

import requests


class FimerApi:
    def __init__(
        self,
        username: str,
        password: str,
        plant_id: str,
    ):
        self._username = username
        self._password = password
        self._plant_id = plant_id

        self._auth_url = "https://m.auroravision.net"
        self._api_url = "https://www.auroravision.net"

        self._session = requests.Session()
        self._token = None

    def login(self):
        """Login op Aurora Vision."""

        auth = base64.b64encode(
            f"{self._username}:{self._password}".encode()
        ).decode()

        headers = {
            "Authorization": f"Basic {auth}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = self._session.get(
            f"{self._auth_url}/ums/v1/login",
            headers=headers,
            timeout=20,
        )

        response.raise_for_status()

        data = response.json()

        self._token = data["token"]

        # Telemetry gebruikt een cookie i.p.v. Authorization header
        self._session.cookies.set(
            "token.auroravision.net",
            self._token,
            domain="www.auroravision.net",
        )

    def _today(self):
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

    def _telemetry(
        self,
        category: str,
        metric: str,
        afx: str = "Last",
    ):
        if self._token is None:
            self.login()

        sdt, edt = self._today()

        params = {
            "agp": "All",
            "afx": afx,
            "sdt": sdt,
            "edt": edt,
        }

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.auroravision.net/eview/",
            "User-Agent": "Home Assistant",
        }

        response = self._session.get(
            f"{self._api_url}/telemetry/v1/plants/{self._plant_id}/{category}/{metric}",
            params=params,
            headers=headers,
            timeout=20,
        )

        # Token verlopen?
        if response.status_code == 401:
            self.login()

            response = self._session.get(
                f"{self._api_url}/telemetry/v1/plants/{self._plant_id}/{category}/{metric}",
                params=params,
                headers=headers,
                timeout=20,
            )

        response.raise_for_status()

        return response.json()

    #
    # Power sensors
    #

    def generation_power(self):
        data = self._telemetry("power", "GenerationPower")

        if not data:
            return None

        return data[0]["value"]

    def grid_power(self):
        data = self._telemetry("power", "GridPower")

        if not data:
            return None

        return data[0]["value"]

    def battery_power(self):
        data = self._telemetry("power", "StoragePower")

        if not data:
            return None

        return data[0]["value"]

    #
    # Energy sensors
    #

    def generation_energy_today(self):
        data = self._telemetry(
            "energy",
            "GenerationEnergy",
            afx="Delta",
        )

        if not data:
            return None

        return data[-1]["value"]