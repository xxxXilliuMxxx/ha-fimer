from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL


@dataclass(frozen=True, kw_only=True)
class FimerSensorDescription(SensorEntityDescription):
    key: str


SENSORS: tuple[FimerSensorDescription, ...] = (
    FimerSensorDescription(
        key="generation_power",
        name="Generation Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    FimerSensorDescription(
        key="grid_power",
        name="Grid Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    FimerSensorDescription(
        key="battery_power",
        name="Battery Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    FimerSensorDescription(
        key="generation_energy_today",
        name="Generation Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    FimerSensorDescription(
        key="generation_energy_total",
        name="Generation Total",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        FimerSensor(
            coordinator,
            entry,
            description,
        )
        for description in SENSORS
    )


class FimerSensor(
    CoordinatorEntity,
    SensorEntity,
):
    """FIMER sensor."""

    entity_description: FimerSensorDescription

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        description: FimerSensorDescription,
    ) -> None:

        super().__init__(coordinator)

        self.entity_description = description

        self._attr_unique_id = (
            f"{entry.entry_id}_{description.key}"
        )

        self._attr_has_entity_name = True

    @property
    def native_value(self):

        return self.coordinator.data.get(
            self.entity_description.key
        )

    @property
    def device_info(self):
        return {
            "identifiers": {
                (
                    DOMAIN,
                    "aurora_vision",
                )
            },
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "name": "FIMER Aurora Vision",
        }
