from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL


SENSORS = [
    (
        "generation_power",
        "Generation Power",
        UnitOfPower.WATT,
        SensorDeviceClass.POWER,
    ),
    (
        "grid_power",
        "Grid Power",
        UnitOfPower.WATT,
        SensorDeviceClass.POWER,
    ),
    (
        "battery_power",
        "Battery Power",
        UnitOfPower.WATT,
        SensorDeviceClass.POWER,
    ),
    (
        "generation_energy_today",
        "Generation Today",
        UnitOfEnergy.KILO_WATT_HOUR,
        SensorDeviceClass.ENERGY,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for key, name, unit, device_class in SENSORS:
        entities.append(
            FimerSensor(
                coordinator,
                entry,
                key,
                name,
                unit,
                device_class,
            )
        )

    async_add_entities(entities)


class FimerSensor(CoordinatorEntity, SensorEntity):

    def __init__(
        self,
        coordinator,
        entry,
        key,
        name,
        unit,
        device_class,
    ):
        super().__init__(coordinator)

        self._key = key

        self._attr_name = name

        self._attr_unique_id = (
            f"{entry.entry_id}_{key}"
        )

        self._attr_native_unit_of_measurement = unit

        self._attr_device_class = device_class

        self._attr_state_class = (
            SensorStateClass.MEASUREMENT
        )

        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    entry.entry_id,
                )
            },
            manufacturer=MANUFACTURER,
            model=MODEL,
            name="FIMER Aurora Vision",
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)