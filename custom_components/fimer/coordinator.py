from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import FimerApi
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class FimerCoordinator(DataUpdateCoordinator):
    """Coordinator for FIMER data."""

    def __init__(self, hass: HomeAssistant, api: FimerApi, plant_id: str):
        super().__init__(
            hass,
            _LOGGER,
            name="Fimer Coordinator",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

        self.api = api
        self.plant_id = plant_id

    async def _async_update_data(self):
        try:
            data = await self.api.get_plant_data(self.plant_id)
            return data
        except Exception as err:
            raise UpdateFailed(f"Fimer update failed: {err}") from err
