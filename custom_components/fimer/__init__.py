from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import FimerApi
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_PLANT_ID,
)
from .coordinator import FimerCoordinator

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config):
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
):
    api = FimerApi(
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        entry.data[CONF_PLANT_ID],
    )

    coordinator = FimerCoordinator(hass, api)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
):
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok