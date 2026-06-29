from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import FimerApi
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class FimerCoordinator(DataUpdateCoordinator):
    """Coordinator voor FIMER Aurora Vision."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: FimerApi,
    ):
        self.api = api

        super().__init__(
            hass,
            _LOGGER,
            name="FIMER Aurora Vision",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Haal alle gegevens op."""

        try:
            return await self.hass.async_add_executor_job(
                self._fetch_data
            )

        except Exception as err:
            raise UpdateFailed(f"Fout tijdens ophalen data: {err}") from err

    def _fetch_data(self):
        """Alle API-calls gebeuren hier."""

        data = {}

        #
        # PV Vermogen
        #
        try:
            data["generation_power"] = self.api.generation_power()
        except Exception as err:
            _LOGGER.warning("Generation Power mislukt: %s", err)
            data["generation_power"] = None

        #
        # Netvermogen
        #
        try:
            data["grid_power"] = self.api.grid_power()
        except Exception as err:
            _LOGGER.warning("Grid Power mislukt: %s", err)
            data["grid_power"] = None

        #
        # Batterijvermogen
        #
        try:
            data["battery_power"] = self.api.battery_power()
        except Exception as err:
            _LOGGER.warning("Battery Power mislukt: %s", err)
            data["battery_power"] = None

        #
        # Opbrengst vandaag
        #
        try:
            data["generation_energy_today"] = (
                self.api.generation_energy_today()
            )
        except Exception as err:
            _LOGGER.warning("Generation Energy mislukt: %s", err)
            data["generation_energy_today"] = None

        return data