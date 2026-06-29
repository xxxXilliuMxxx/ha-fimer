from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


SENSORS = {
    "current_power": {
        "name": "Current Power",
        "unit": "W",
    },
    "daily_energy": {
        "name": "Daily Energy",
        "unit": "kWh",
    },
    "total_energy": {
        "name": "Total Energy",
        "unit": "kWh",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        FimerSensor(coordinator, key, description)
        for key, description in SENSORS.items()
    ]

    async_add_entities(entities)


class FimerSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, key, description):

        super().__init__(coordinator)

        self._key = key
        self._attr_name = description["name"]
        self._attr_native_unit_of_measurement = description["unit"]
        self._attr_unique_id = f"fimer_{key}"

    @property
    def native_value(self):

        return self.coordinator.data.get(self._key)

    @property
    def available(self):

        return self.coordinator.last_update_success
