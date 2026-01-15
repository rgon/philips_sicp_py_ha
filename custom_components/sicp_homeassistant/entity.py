"""Shared entity helpers for the Philips SICP integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from sicppy.ip_monitor import NotSupportedOrNotAvailableError
from functools import cached_property

from .const import CONF_MAC_ADDRESS, DOMAIN, MANUFACTURER
from .coordinator import PhilipsSicpCoordinator, SicpDisplayData


class PhilipsSicpEntity(CoordinatorEntity[PhilipsSicpCoordinator]):
    """Base class for SICP-backed entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry, suffix: str) -> None:
        super().__init__(coordinator)
        self._entry = entry
        unique_source = entry.unique_id or entry.entry_id
        self._attr_unique_id = f"{unique_source}_{suffix}"
        friendly_suffix = suffix.replace("_", " ").strip()
        self._attr_name = friendly_suffix.title() if friendly_suffix else suffix

    @cached_property
    def device_info(self) -> DeviceInfo:
        """Return metadata for the parent display."""
        data = self.coordinator.data
        mac = self._entry.data.get(CONF_MAC_ADDRESS)
        connections: set[tuple[str, str]] | None = None
        if mac:
            connections = {(CONNECTION_NETWORK_MAC, mac)}

        serial = self._entry.data.get("serial_number")
        model = data.model_info.get("model_number") if data else None

        identifiers = {(DOMAIN, self._entry.entry_id)}
        if self._entry.unique_id:
            identifiers.add((DOMAIN, self._entry.unique_id))

        if not connections:
            raise HomeAssistantError("Cannot determine device connections for SICP display.")

        return DeviceInfo(
            identifiers=identifiers,
            connections=connections,
            manufacturer=MANUFACTURER,
            model=model,
            name=self._entry.title,
            serial_number=serial,
        )

    @property
    def sicp_data(self) -> SicpDisplayData:
        """Shortcut to the latest coordinator data."""
        return self.coordinator.data

    async def _async_call_client(self, func, *args, error_hint: str | None = None):
        """Run a blocking client method and normalize errors."""
        try:
            return await self.hass.async_add_executor_job(func, *args)
        except NotSupportedOrNotAvailableError as exc:
            message = error_hint or "This function is not available on the current display/source."
            raise HomeAssistantError(message) from exc
        except Exception as exc:  # noqa: BLE001
            raise HomeAssistantError(str(exc)) from exc
