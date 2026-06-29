"""Constants for the FIMER Aurora Vision integration."""

from datetime import timedelta

DOMAIN = "fimer"

NAME = "FIMER Aurora Vision"

MANUFACTURER = "FIMER"

UPDATE_INTERVAL = timedelta(seconds=60)

# Config Flow
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_OTP = "otp"

# API URLs
BASE_URL = "https://www.auroravision.net"

LOGIN_URL = f"{BASE_URL}/ums/v1/login"

PORTFOLIO_URL = f"{BASE_URL}/ums/v1/portfolios"

TELEMETRY_URL = f"{BASE_URL}/telemetry/v1"

# Telemetry parameters
AGP = "All"
AFX_LAST = "Last"
AFX_DELTA = "Delta"

# Sensor keys
SENSOR_GENERATION_POWER = "generation_power"
SENSOR_GENERATION_TODAY = "generation_today"
SENSOR_GRID_POWER = "grid_power"
SENSOR_BATTERY_POWER = "battery_power"

SENSORS = (
    SENSOR_GENERATION_POWER,
    SENSOR_GENERATION_TODAY,
    SENSOR_GRID_POWER,
    SENSOR_BATTERY_POWER,
)
