"""Number (slider) entities for Philips SICP displays."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import PhilipsSicpCoordinator
from .entity import PhilipsSicpEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities for a config entry."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PhilipsSicpCoordinator = entry_data[DATA_COORDINATOR]

    async_add_entities([PhilipsSicpVolumeNumber(coordinator, entry)])


class PhilipsSicpVolumeNumber(PhilipsSicpEntity, NumberEntity):
    """Speaker volume slider (0-100%)."""

    min_value = 0
    max_value = 100
    step = 1
    mode = NumberMode.SLIDER
    native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "speaker_volume")

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data
        if not data:
            return None
        return data.volume_speaker

    async def async_set_native_value(self, value: float) -> None:
        await self._async_call_client(
            self.coordinator.client.set_volume,
            int(value),
            error_hint="Unable to set the speaker volume",
        )
        await self.coordinator.async_request_refresh()
