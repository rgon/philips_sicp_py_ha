"""Constants for the Philips SICP display integration."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.const import CONF_MAC, Platform

DOMAIN = "philips_sicp_display"
PLATFORMS: list[Platform] = [
	Platform.SENSOR,
	Platform.LIGHT,
	Platform.SELECT,
	Platform.SWITCH,
	Platform.NUMBER,
]

CONF_MONITOR_ID = "monitor_id"
CONF_MAC_ADDRESS = CONF_MAC
CONF_DISPLAY_NAME = "display_name"

DEFAULT_MONITOR_ID = 1
DEFAULT_PORT = 5000

DATA_CLIENT = "client"
DATA_COORDINATOR = "coordinator"

MANUFACTURER = "Philips"

UPDATE_INTERVAL = timedelta(seconds=60)
