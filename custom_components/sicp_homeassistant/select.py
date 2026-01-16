"""Select entities for Philips SICP displays."""
from __future__ import annotations

from collections import OrderedDict

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from sicppy.messages import (
    ColdStartPowerState,
    InputSource,
    PowerOnLogoMode,
    SmartPowerLevel,
)

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import PhilipsSicpCoordinator
from .entity import PhilipsSicpEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities for a config entry."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PhilipsSicpCoordinator = entry_data[DATA_COORDINATOR]

    async_add_entities(
        [
            PhilipsSicpSmartPowerSelect(coordinator, entry),
            PhilipsSicpPowerOnLogoSelect(coordinator, entry),
            PhilipsSicpColdStartSelect(coordinator, entry),
            PhilipsSicpInputSourceSelect(coordinator, entry),
        ]
    )


def _friendly_name(enum_name: str) -> str:
    text = enum_name.replace("_", " ").title()
    replacements = {
        "Usb": "USB",
        "Hdmi": "HDMI",
        "Dvi": "DVI",
        "Cms": "CMS",
        "Ops": "OPS",
        "Lan": "LAN",
    }
    for needle, repl in replacements.items():
        text = text.replace(needle, repl)
    return text


class PhilipsSicpEnumSelect(PhilipsSicpEntity, SelectEntity):
    """Base class for selects backed by Enum options."""

    _attr_disable_on_offline = True

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry, suffix: str, enum_class) -> None:
        super().__init__(coordinator, entry, suffix)
        self._enum_class = enum_class
        self._option_map = OrderedDict()
        for member in enum_class:
            label = _friendly_name(member.name)
            self._option_map[label] = member

    @property
    def options(self) -> list[str]:
        return list(self._option_map.keys())

    def _option_from_enum(self, enum_value) -> str | None:
        for label, value in self._option_map.items():
            if value == enum_value:
                return label
        return None

    def _enum_from_option(self, option: str):
        try:
            return self._option_map[option]
        except KeyError as exc:  # noqa: PERF203 - single lookup
            raise HomeAssistantError(f"Unknown option: {option}") from exc

    async def _async_set_enum(self, enum_value) -> None:
        raise NotImplementedError

    async def async_select_option(self, option: str) -> None:
        enum_value = self._enum_from_option(option)
        await self._async_set_enum(enum_value)
        await self.coordinator.async_request_refresh()


class PhilipsSicpSmartPowerSelect(PhilipsSicpEnumSelect):
    """Select entity for smart power levels."""

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "smart_power", SmartPowerLevel)

    @property
    def current_option(self) -> str | None:
        data = self.coordinator.data
        if not data or data.smart_power_level is None:
            return None
        return self._option_from_enum(data.smart_power_level)

    async def _async_set_enum(self, enum_value: SmartPowerLevel) -> None:
        await self._async_call_client(
            self.coordinator.client.set_smart_power_level,
            enum_value,
            error_hint="Smart power level control is not available on this display",
        )


class PhilipsSicpPowerOnLogoSelect(PhilipsSicpEnumSelect):
    """Select entity for the power-on logo mode."""

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "power_on_logo", PowerOnLogoMode)

    @property
    def current_option(self) -> str | None:
        data = self.coordinator.data
        if not data or data.power_on_logo_mode is None:
            return None
        return self._option_from_enum(data.power_on_logo_mode)

    async def _async_set_enum(self, enum_value: PowerOnLogoMode) -> None:
        await self._async_call_client(
            self.coordinator.client.set_power_on_logo_mode,
            enum_value,
            error_hint="Power-on logo control is not supported",
        )


class PhilipsSicpColdStartSelect(PhilipsSicpEnumSelect):
    """Select entity for cold-start behavior."""

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "cold_start", ColdStartPowerState)

    @property
    def current_option(self) -> str | None:
        data = self.coordinator.data
        if not data or data.cold_start_state is None:
            return None
        return self._option_from_enum(data.cold_start_state)

    async def _async_set_enum(self, enum_value: ColdStartPowerState) -> None:
        await self._async_call_client(
            self.coordinator.client.set_cold_start_power_state,
            enum_value,
            error_hint="Unable to update cold-start power behavior",
        )


class PhilipsSicpInputSourceSelect(PhilipsSicpEnumSelect):
    """Select entity for active input source."""

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "input_source", InputSource)
        self._playlist_options: OrderedDict[str, tuple[InputSource, int]] = OrderedDict()
        playlist_sources = (
            InputSource.MEDIAPLAYER,
            InputSource.BROWSER,
        )
        for source in playlist_sources:
            base_label = _friendly_name(source.name)
            for playlist_id in (1, 2):
                label = f"{base_label} Playlist {playlist_id}"
                self._playlist_options[label] = (source, playlist_id)

    @property
    def current_option(self) -> str | None:
        data = self.coordinator.data
        if not data or data.input_source is None:
            return None
        return self._option_from_enum(data.input_source)

    @property
    def options(self) -> list[str]:
        base_options = super().options
        return base_options + list(self._playlist_options.keys())

    async def _async_set_enum(self, enum_value: InputSource) -> None:
        await self._async_set_input_source(enum_value)

    async def async_select_option(self, option: str) -> None:
        playlist_target = self._playlist_options.get(option)
        if playlist_target:
            source, playlist_id = playlist_target
            await self._async_set_input_source(source, playlist_id)
            await self.coordinator.async_request_refresh()
            return
        await super().async_select_option(option)

    async def _async_set_input_source(self, enum_value: InputSource, playlist: int = 0) -> None:
        await self._async_call_client(
            self.coordinator.client.set_input_source,
            enum_value,
            playlist,
            error_hint="Unable to switch input source",
        )
