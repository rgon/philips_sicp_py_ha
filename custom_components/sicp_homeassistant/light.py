"""Light platform for Philips SICP displays."""
from __future__ import annotations

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    LightEntity,
)
from homeassistant.components.light.const import ColorMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from functools import cached_property

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import PhilipsSicpCoordinator
from .entity import PhilipsSicpEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Philips SICP light entities for a config entry."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PhilipsSicpCoordinator = entry_data[DATA_COORDINATOR]

    async_add_entities([PhilipsSicpLight(coordinator, entry)])


class PhilipsSicpLight(PhilipsSicpEntity, LightEntity):
    """Representation of the display power/brightness controls."""

    _attr_supported_color_modes = {ColorMode.COLOR_TEMP}
    _attr_min_color_temp_kelvin = 2000
    _attr_max_color_temp_kelvin = 10000

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "backlight")

    @cached_property
    def is_on(self) -> bool | None:
        data = self.sicp_data
        if not data:
            return None
        return data.backlight_on

    @cached_property
    def brightness(self) -> int | None:
        data = self.sicp_data
        if not data or data.brightness is None:
            return None
        return int(data.brightness / 100 * 255)

    @cached_property
    def color_mode(self) -> ColorMode:
        return ColorMode.COLOR_TEMP
        # data = self.sicp_data
        # if data and data.precise_color_temperature:
        #     return ColorMode.COLOR_TEMP
        # return ColorMode.BRIGHTNESS

    @property
    def color_temp_kelvin(self) -> int | None:
        data = self.sicp_data
        if not data or not data.precise_color_temperature:
            return None
        return data.precise_color_temperature

    async def async_turn_on(self, **kwargs) -> None:
        client = self.coordinator.client
        if not self.is_on:
            await self._async_call_client(
                client.set_backlight,
                True,
                error_hint="Unable to enable the backlight",
            )

        if ATTR_BRIGHTNESS in kwargs:
            percent = max(0, min(100, round(kwargs[ATTR_BRIGHTNESS] * 100 / 255)))
            await self._async_call_client(
                client.set_brightness_percent,
                percent,
                error_hint="Brightness control is not available on this source",
            )

        if ATTR_COLOR_TEMP_KELVIN in kwargs:
            kelvin = int(kwargs[ATTR_COLOR_TEMP_KELVIN])
            await self._async_call_client(
                client.set_precise_color_temperature,
                kelvin,
                error_hint="Precise color temperature is not available on this source",
            )

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        client = self.coordinator.client
        await self._async_call_client(
            client.set_backlight,
            False,
            error_hint="Unable to disable the backlight",
        )
        await self.coordinator.async_request_refresh()