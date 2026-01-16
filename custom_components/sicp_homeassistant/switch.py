"""Switch entities for Philips SICP displays."""
from __future__ import annotations

import asyncio
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from sicppy.messages import PowerState

from .const import CONF_MAC_ADDRESS, DATA_COORDINATOR, DOMAIN
from .coordinator import PhilipsSicpCoordinator
from .entity import PhilipsSicpEntity
from .wol import async_wake_on_lan

_LOGGER = logging.getLogger(__name__)
_TURN_OFF_TIME_SECONDS = 15
_TURN_ON_TIME_SECONDS = 12

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


class PhilipsSicpPowerSwitch(PhilipsSicpEntity, SwitchEntity):
    """Switch entity that toggles the hardware power state."""

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "power_switch")
        mac = entry.data.get(CONF_MAC_ADDRESS)
        if not isinstance(mac, str) or not mac:
            raise HomeAssistantError("Missing MAC address for power switch entity")
        self._mac_address = mac

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data
        if not data or not data.power_state:
            return None
        return data.power_state == PowerState.POWER_ON

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        data = self.coordinator.data
        if not data:
            return {"power_state": "offline"}
        if not data.power_state:
            return {"power_state": "offline"}
        return {"power_state": "on" if data.power_state == PowerState.POWER_ON else "off"}

    async def async_turn_on(self, **kwargs) -> None:
        await self._async_handle_power(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._async_handle_power(False)
        # Prevent turning on again with wol to prevent hanging if a kid is spamming the button
        await asyncio.sleep(_TURN_OFF_TIME_SECONDS)


    async def _async_handle_power(self, turn_on: bool) -> None:
        data = self.coordinator.data
        power_state = data.power_state if data else None

        if power_state == PowerState.OFFLINE:
            if turn_on:
                _LOGGER.info("Sending Wake-on-LAN to %s", self._mac_address)
                await async_wake_on_lan(self._mac_address)
                await asyncio.sleep(_TURN_ON_TIME_SECONDS)
                await self.coordinator.async_request_refresh()
            return

        await self._async_call_client(
            self.coordinator.client.set_power,
            turn_on,
            error_hint="Unable to power on the display" if turn_on else "Unable to power off the display",
        )
        await self.coordinator.async_request_refresh()


class PhilipsSicpMuteSwitch(PhilipsSicpEntity, SwitchEntity):
    """Switch entity that toggles the audio mute state."""

    _attr_disable_on_offline = True

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "mute")

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data
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
