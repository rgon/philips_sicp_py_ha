"""Switch entities for Philips SICP displays."""
from __future__ import annotations
from functools import cached_property

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from sicppy.messages import PowerState

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import PhilipsSicpCoordinator
from .entity import PhilipsSicpEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities for a config entry."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PhilipsSicpCoordinator = entry_data[DATA_COORDINATOR]

    async_add_entities(
        [
            PhilipsSicpPowerSwitch(coordinator, entry),
            PhilipsSicpMuteSwitch(coordinator, entry),
        ]
    )


class PhilipsSicpPowerSwitch(PhilipsSicpEntity): #, SwitchEntity):
    """Switch entity that toggles the hardware power state."""

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "power_switch")

    @property
    def is_on(self) -> bool | None:
        data = self.sicp_data
        if not data or not data.power_state:
            return None
        return data.power_state == PowerState.POWER_ON

    @cached_property
    def extra_state_attributes(self) -> dict[str, str]:
        data = self.sicp_data
        if not data:
            return {"power_state": "offline"}
        if not data.power_state:
            return {"power_state": "offline"}
        return {"power_state": "on" if data.power_state == PowerState.POWER_ON else "off"}

    async def async_turn_on(self, **kwargs) -> None:
        await self._async_call_client(
            self.coordinator.client.set_power,
            True,
            error_hint="Unable to power on the display",
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self._async_call_client(
            self.coordinator.client.set_power,
            False,
            error_hint="Unable to power off the display",
        )
        await self.coordinator.async_request_refresh()


class PhilipsSicpMuteSwitch(PhilipsSicpEntity): #, SwitchEntity):
    """Switch entity that toggles the audio mute state."""

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "mute")

    @property
    def is_on(self) -> bool | None:
        data = self.sicp_data
        if data is None:
            return None
        return data.mute

    async def async_turn_on(self, **kwargs) -> None:
        await self._async_call_client(
            self.coordinator.client.set_mute,
            True,
            error_hint="Unable to mute the display audio",
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self._async_call_client(
            self.coordinator.client.set_mute,
            False,
            error_hint="Unable to unmute the display audio",
        )
        await self.coordinator.async_request_refresh()
