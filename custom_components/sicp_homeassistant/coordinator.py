"""Coordinator and client helpers for the Philips SICP display integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from sicppy.ip_monitor import (
    DEFAULT_PORT as SICP_DEFAULT_PORT,
    NetworkError,
    NotSupportedOrNotAvailableError,
    SICPIPMonitor,
)
from sicppy.messages import (
    ColdStartPowerState,
    InputSource,
    ModelInfoFields,
    PowerOnLogoMode,
    PowerState,
    SicpInfoFields,
    SmartPowerLevel,
)

from .const import (
    CONF_MONITOR_ID,
    DEFAULT_MONITOR_ID,
    DEFAULT_PORT,
    DOMAIN,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class SicpDisplayData:
    """Container for the latest monitor data."""

    power_state: PowerState | None
    backlight_on: bool | None
    brightness: int | None
    precise_color_temperature: int | None
    temperatures: list[int] | None
    serial_number: str | None
    model_info: dict[str, str]
    sicp_info: dict[str, str]
    smart_power_level: SmartPowerLevel | None
    power_on_logo_mode: PowerOnLogoMode | None
    cold_start_state: ColdStartPowerState | None
    input_source: InputSource | None
    volume_speaker: int | None
    volume_audio_out: int | None
    mute: bool | None


class SicpDisplayClient:
    """Blocking client that proxies calls to a Philips SICP display."""

    def __init__(self, entry_data: Mapping[str, Any]) -> None:
        host = entry_data.get(CONF_HOST)
        if not host:
            raise ValueError("Host/IP address is required to create the SICP client")

        monitor_id = entry_data.get(CONF_MONITOR_ID, DEFAULT_MONITOR_ID)
        port = entry_data.get(CONF_PORT) or DEFAULT_PORT or SICP_DEFAULT_PORT

        self._monitor = SICPIPMonitor(host, monitor_id=monitor_id, port=port)

    def fetch_status(self) -> SicpDisplayData:
        """Fetch the latest state from the display."""
        power_state = self._monitor.get_power_state()

        brightness: int | None = None
        try:
            brightness = self._monitor.get_brightness_level()
        except NotSupportedOrNotAvailableError:
            _LOGGER.debug("Brightness level unsupported on this source or power saving mode")
        except Exception:  # noqa: BLE001 - optional metric, ignore
            _LOGGER.debug("Brightness level unavailable", exc_info=True)

        precise_color_temperature: int | None = None
        try:
            precise_color_temperature = self._monitor.get_precise_color_temperature()
        except NotSupportedOrNotAvailableError:
            _LOGGER.debug("Precise color temperature unsupported on this source")
        except Exception:
            _LOGGER.debug("Unable to read precise color temperature", exc_info=True)

        backlight_on: bool | None = None
        try:
            backlight_on = self._monitor.get_backlight_state()
        except Exception:
            _LOGGER.debug("Unable to read backlight state", exc_info=True)

        temperatures = self._monitor.get_temperature()
        serial_number = self._monitor.get_serial_number()
        model_info = self._collect_model_info()
        sicp_info = self._collect_sicp_info()

        smart_power_level: SmartPowerLevel | None = None
        try:
            smart_power_level = self._monitor.get_smart_power_level()
        except NotSupportedOrNotAvailableError:
            _LOGGER.debug("Smart power level unsupported")
        except Exception:
            _LOGGER.debug("Unable to read smart power level", exc_info=True)

        power_on_logo_mode: PowerOnLogoMode | None = None
        try:
            power_on_logo_mode = self._monitor.get_power_on_logo_mode()
        except NotSupportedOrNotAvailableError:
            _LOGGER.debug("Power-on logo control unsupported")
        except Exception:
            _LOGGER.debug("Unable to read power-on logo mode", exc_info=True)

        cold_start_state: ColdStartPowerState | None = None
        try:
            cold_start_state = self._monitor.get_cold_start_power_state()
        except Exception:
            _LOGGER.debug("Unable to read cold-start power state", exc_info=True)

        input_source: InputSource | None = None
        try:
            input_source = self._monitor.get_input_source()
        except Exception:
            _LOGGER.debug("Unable to read input source", exc_info=True)

        volume_speaker: int | None = None
        volume_audio_out: int | None = None
        try:
            volume_speaker, volume_audio_out = self._monitor.get_volume()
        except Exception:
            _LOGGER.debug("Unable to read volume levels", exc_info=True)

        mute: bool | None = None
        try:
            mute = self._monitor.get_mute()
        except Exception:
            _LOGGER.debug("Unable to read mute state", exc_info=True)

        return SicpDisplayData(
            power_state=power_state,
            backlight_on=backlight_on,
            brightness=brightness,
            precise_color_temperature=precise_color_temperature,
            temperatures=temperatures,
            serial_number=serial_number,
            model_info=model_info,
            sicp_info=sicp_info,
            smart_power_level=smart_power_level,
            power_on_logo_mode=power_on_logo_mode,
            cold_start_state=cold_start_state,
            input_source=input_source,
            volume_speaker=volume_speaker,
            volume_audio_out=volume_audio_out,
            mute=mute,
        )

    def set_power(self, power_on: bool) -> bool:
        """Set the display power state."""
        return bool(self._monitor.set_power(power_on))

    def set_brightness_percent(self, percent: int) -> bool:
        """Set display brightness in percent (0-100)."""
        return bool(self._monitor.set_brightness_level(percent))

    def set_precise_color_temperature(self, kelvin: int) -> bool:
        """Set the precise color temperature in Kelvin."""
        return bool(self._monitor.set_precise_color_temperature(kelvin))

    def set_backlight(self, backlight_on: bool) -> bool:
        """Control the backlight state."""
        return bool(self._monitor.set_backlight(backlight_on))

    def set_smart_power_level(self, level: SmartPowerLevel) -> bool:
        return bool(self._monitor.set_smart_power_level(level))

    def set_power_on_logo_mode(self, mode: PowerOnLogoMode) -> bool:
        return bool(self._monitor.set_power_on_logo_mode(mode))

    def set_cold_start_power_state(self, state: ColdStartPowerState) -> bool:
        return bool(self._monitor.set_cold_start_power_state(state))

    def set_input_source(self, source: InputSource) -> bool:
        return bool(self._monitor.set_input_source(source))

    def set_mute(self, mute_on: bool) -> bool:
        return bool(self._monitor.set_mute(mute_on))

    def set_volume(self, speaker_level: int) -> bool:
        return bool(self._monitor.set_volume(speaker_level=speaker_level))

    def _collect_model_info(self) -> dict[str, str]:
        return {
            "model_number": self._monitor.get_model_info(ModelInfoFields.MODEL_NUMBER),
            "firmware_version": self._monitor.get_model_info(ModelInfoFields.FIRMWARE_VERSION),
            "build_date": self._monitor.get_model_info(ModelInfoFields.BUILD_DATE),
            "android_firmware": self._monitor.get_model_info(ModelInfoFields.ANDROID_FIRMWARE),
        }

    def _collect_sicp_info(self) -> dict[str, str]:
        custom_intent_version: str | None = None
        try:
            custom_intent_version = self._monitor.get_sicp_info(SicpInfoFields.CUSTOM_INTENT_VERSION)
        except NotSupportedOrNotAvailableError:
            custom_intent_version = "N/A"

        return {
            "platform_label": self._monitor.get_sicp_info(SicpInfoFields.PLATFORM_LABEL),
            "platform_version": self._monitor.get_sicp_info(SicpInfoFields.PLATFORM_VERSION),
            "custom_intent_version": custom_intent_version,
        }


class PhilipsSicpCoordinator(DataUpdateCoordinator[SicpDisplayData]):
    """DataUpdateCoordinator used by the entities."""

    def __init__(self, hass: HomeAssistant, client: SicpDisplayClient, config_entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{config_entry.title}",
            config_entry=config_entry,
            update_interval=UPDATE_INTERVAL,
        )
        self._client = client

    async def _async_update_data(self) -> SicpDisplayData:
        """Fetch data from SICP endpoint in display."""
        try:
            return await self.hass.async_add_executor_job(self._client.fetch_status)
        except NetworkError as exc:
            raise UpdateFailed("Unable to reach Philips display") from exc
        except Exception as exc:  # noqa: BLE001
            raise UpdateFailed(str(exc)) from exc

    @property
    def client(self) -> SicpDisplayClient:
        """Expose the underlying client to entities for control operations."""
        return self._client

    @property
    def serial_number(self) -> str | None:
        """Return the most recent serial number."""
        if self.data and self.data.serial_number:
            return self.data.serial_number
        if not self.config_entry:
            return None
        return self.config_entry.data.get("serial_number")

    @property
    def model_number(self) -> str | None:
        """Return the reported model number if available."""
        if self.data and self.data.model_info:
            return self.data.model_info.get("model_number")
        return None
