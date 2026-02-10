"""Shared entity helpers for the Philips SICP integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from sicppy.ip_monitor import NotSupportedOrNotAvailableError
from sicppy.messages import PowerState

from .const import CONF_MAC_ADDRESS, DOMAIN, MANUFACTURER
from .coordinator import PhilipsSicpCoordinator


class PhilipsSicpEntity(CoordinatorEntity[PhilipsSicpCoordinator]):
    """Base class for SICP-backed entities."""

    _attr_has_entity_name = True
    _attr_disable_on_offline = False

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry, suffix: str) -> None:
        super().__init__(coordinator)
        self._entry = entry
        unique_source = entry.unique_id or entry.entry_id
        self._attr_unique_id = f"{unique_source}_{suffix}"
        friendly_suffix = suffix.replace("_", " ").strip()
        self._attr_name = friendly_suffix.title() if friendly_suffix else suffix

        mac = entry.data.get(CONF_MAC_ADDRESS)
        connections = {(CONNECTION_NETWORK_MAC, mac)} if mac else None

        data = coordinator.data
        model = data.model_info.get("model_number") if data and data.model_info else None
        serial = data.serial_number if data else None

        identifiers = {(DOMAIN, entry.entry_id)}
        if entry.unique_id:
            identifiers.add((DOMAIN, entry.unique_id))

        if not connections:
            raise HomeAssistantError("Cannot determine device connections for SICP display.")
        self._attr_device_info = DeviceInfo(
            identifiers=identifiers,
            connections=connections,
            manufacturer=MANUFACTURER,
            model=model,
            name=entry.title,
            serial_number=serial,
        )

    def _is_display_offline(self) -> bool:
        data = self.coordinator.data
        return bool(data and data.power_state == PowerState.OFFLINE)

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        if self._attr_disable_on_offline and self._is_display_offline():
            return False
        return True
    async def _async_call_client(self, func, *args, error_hint: str | None = None):
        """Invoke a client method and normalize errors."""
        try:
            return await self.coordinator.async_call_client(func, *args)
        except NotSupportedOrNotAvailableError as exc:
            message = error_hint or "This function is not available on the current display/source."
            raise HomeAssistantError(message) from exc
        except Exception as exc:  # noqa: BLE001
            raise HomeAssistantError(str(exc)) from exc
