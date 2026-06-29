from __future__ import annotations

import logging

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import FimerApi
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class FimerCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator for Aurora Vision."""

    def __init__(
        self,
        hass,
        api: FimerApi,
    ) -> None:

        super().__init__(
            hass,
            _LOGGER,
            name="FIMER Aurora Vision",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

        self.api = api

    async def _async_update_data(self) -> dict:
        """Fetch data from Aurora Vision."""

        try:
            return await self.api.get_data()

        except Exception:
            _LOGGER.exception("Aurora Vision update failed")
            raise
