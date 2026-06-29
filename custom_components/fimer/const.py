"""Constants for the FIMER Aurora Vision integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "fimer"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_PLANT_ID = "plant_id"

DEFAULT_SCAN_INTERVAL = timedelta(seconds=60)

MANUFACTURER = "FIMER"
MODEL = "Aurora Vision"

ATTR_GENERATION_POWER = "generation_power"
ATTR_GRID_POWER = "grid_power"
ATTR_BATTERY_POWER = "battery_power"

ATTR_GENERATION_ENERGY_TODAY = "generation_energy_today"
ATTR_GENERATION_ENERGY_TOTAL = "generation_energy_total"

ATTR_GRID_IMPORT_TODAY = "grid_import_today"
ATTR_GRID_EXPORT_TODAY = "grid_export_today"

ATTR_BATTERY_CHARGE_TODAY = "battery_charge_today"
ATTR_BATTERY_DISCHARGE_TODAY = "battery_discharge_today"

ATTR_BATTERY_SOC = "battery_soc"

ATTR_LAST_UPDATE = "last_update"
