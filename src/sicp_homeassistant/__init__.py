"""Philips Signage SICP display integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.typing import ConfigType

from .const import (
	DATA_CLIENT,
	DATA_COORDINATOR,
	DOMAIN,
	PLATFORMS,
)
from .coordinator import PhilipsSicpCoordinator, SicpDisplayClient


async def async_setup(hass: HomeAssistant, _: ConfigType) -> bool:
	"""Set up the integration namespace."""
	hass.data.setdefault(DOMAIN, {})
	return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
	"""Set up a config entry."""
	hass.data.setdefault(DOMAIN, {})

	client = SicpDisplayClient(entry.data)
	coordinator = PhilipsSicpCoordinator(hass, client, entry)

	try:
		await coordinator.async_config_entry_first_refresh()
	except Exception as exc:  # noqa: BLE001 - bubble up as ConfigEntryNotReady
		raise ConfigEntryNotReady from exc

	hass.data[DOMAIN][entry.entry_id] = {
		DATA_CLIENT: client,
		DATA_COORDINATOR: coordinator,
	}

	await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
	return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
	"""Unload a config entry."""
	unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
	if unload_ok:
		hass.data[DOMAIN].pop(entry.entry_id, None)

	return unload_ok