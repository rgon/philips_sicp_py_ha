"""Coordinator and client helpers for the Philips SICP display integration."""
from __future__ import annotations

import asyncio
import inspect
import logging
from dataclasses import dataclass
from typing import Any, Mapping

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
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

REQUEST_REFRESH_DELAY = 0.5

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
    """Async client that proxies calls to a Philips SICP display."""

    def __init__(self, entry_data: Mapping[str, Any]) -> None:
        host = entry_data.get(CONF_HOST)
        if not host:
            raise ValueError("Host/IP address is required to create the SICP client")

        monitor_id = entry_data.get(CONF_MONITOR_ID, DEFAULT_MONITOR_ID)
        port = entry_data.get(CONF_PORT) or DEFAULT_PORT or SICP_DEFAULT_PORT

        self._monitor = SICPIPMonitor(host, monitor_id=monitor_id, port=port)

    async def fetch_status(self) -> SicpDisplayData:
        """Fetch the latest state from the display."""

        power_state:PowerState | None = None
        try:
            power_state = await self._monitor.get_power_state()
        except Exception:
            _LOGGER.debug("Unable to read power state", exc_info=True)

        brightness: int | None = None
        try:
            brightness = await self._monitor.get_brightness_level()
        except NotSupportedOrNotAvailableError:
            _LOGGER.debug("Brightness level unsupported on this source or power saving mode")
        except Exception:  # noqa: BLE001 - optional metric, ignore
            _LOGGER.debug("Brightness level unavailable", exc_info=True)

        precise_color_temperature: int | None = None
        try:
            precise_color_temperature = await self._monitor.get_precise_color_temperature()
        except NotSupportedOrNotAvailableError:
            _LOGGER.debug("Precise color temperature unsupported on this source")
        except Exception:
            _LOGGER.debug("Unable to read precise color temperature", exc_info=True)

        backlight_on: bool | None = None
        try:
            backlight_on = await self._monitor.get_backlight_state()
        except Exception:
            _LOGGER.debug("Unable to read backlight state", exc_info=True)

        temperatures = []
        try:
            temperatures = await self._monitor.get_temperature()
        except Exception:
            _LOGGER.debug("Unable to read temperature sensors", exc_info=True)

        # will raise an error if unable to read
        serial_number = None
        try:
            serial_number = await self._monitor.get_serial_number()
        except Exception:
            _LOGGER.debug("Unable to read serial number", exc_info=True)
        
        model_info: dict[str, str] = {}
        try:
            model_info = await self._collect_model_info()
        except Exception:
            _LOGGER.debug("Unable to read model info", exc_info=True)
        
        sicp_info: dict[str, str] = {}
        try:
            sicp_info = await self._collect_sicp_info()
        except Exception:
            _LOGGER.debug("Unable to read SICP info", exc_info=True)

        smart_power_level: SmartPowerLevel | None = None
        try:
            smart_power_level = await self._monitor.get_smart_power_level()
        except NotSupportedOrNotAvailableError:
            _LOGGER.debug("Smart power level unsupported")
        except Exception:
            _LOGGER.debug("Unable to read smart power level", exc_info=True)
        
        power_on_logo_mode: PowerOnLogoMode | None = None
        try:
            power_on_logo_mode = await self._monitor.get_power_on_logo_mode()
        except NotSupportedOrNotAvailableError:
            _LOGGER.debug("Power-on logo control unsupported")
        except Exception:
            _LOGGER.debug("Unable to read power-on logo mode", exc_info=True)

        cold_start_state: ColdStartPowerState | None = None
        try:
            cold_start_state = await self._monitor.get_cold_start_power_state()
        except Exception:
            _LOGGER.debug("Unable to read cold-start power state", exc_info=True)

        input_source: InputSource | None = None
        try:
            input_source = await self._monitor.get_input_source()
        except Exception:
            _LOGGER.debug("Unable to read input source", exc_info=True)

        volume_speaker: int | None = None
        volume_audio_out: int | None = None
        try:
            volume_speaker, volume_audio_out = await self._monitor.get_volume()
        except Exception:
            _LOGGER.debug("Unable to read volume levels", exc_info=True)

        mute: bool | None = None
        try:
            mute = await self._monitor.get_mute()
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

    async def set_power(self, power_on: bool) -> bool:
        """Set the display power state."""
        return bool(await self._monitor.set_power(power_on))

    async def set_brightness_percent(self, percent: int) -> bool:
        """Set display brightness in percent (0-100)."""
        return bool(await self._monitor.set_brightness_level(percent))

    async def set_precise_color_temperature(self, kelvin: int) -> bool:
        """Set the precise color temperature in Kelvin."""
        return bool(await self._monitor.set_precise_color_temperature(kelvin))

    async def set_backlight(self, backlight_on: bool) -> bool:
        """Control the backlight state."""
        return bool(await self._monitor.set_backlight(backlight_on))

    async def set_smart_power_level(self, level: SmartPowerLevel) -> bool:
        return bool(await self._monitor.set_smart_power_level(level))

    async def set_power_on_logo_mode(self, mode: PowerOnLogoMode) -> bool:
        return bool(await self._monitor.set_power_on_logo_mode(mode))

    async def set_cold_start_power_state(self, state: ColdStartPowerState) -> bool:
        return bool(await self._monitor.set_cold_start_power_state(state))

    async def set_input_source(self, source: InputSource) -> bool:
        return bool(await self._monitor.set_input_source(source))

    async def set_mute(self, mute_on: bool) -> bool:
        return bool(await self._monitor.set_mute(mute_on))

    async def set_volume(self, speaker_level: int) -> bool:
        return bool(await self._monitor.set_volume(speaker_level=speaker_level))

    async def _collect_model_info(self) -> dict[str, str]:
        fields = {
            "model_number": ModelInfoFields.MODEL_NUMBER,
            "firmware_version": ModelInfoFields.FIRMWARE_VERSION,
            "build_date": ModelInfoFields.BUILD_DATE,
            "android_firmware": ModelInfoFields.ANDROID_FIRMWARE,
        }
        info: dict[str, str] = {}
        for key, enum_field in fields.items():
            try:
                info[key] = await self._monitor.get_model_info(enum_field)
            except (IndexError, NetworkError, RuntimeError):
                _LOGGER.debug("Unable to read %s from model info", key, exc_info=True)
        return info

    async def _collect_sicp_info(self) -> dict[str, str]:
        info: dict[str, str] = {}
        fields = {
            "platform_label": SicpInfoFields.PLATFORM_LABEL,
            "platform_version": SicpInfoFields.PLATFORM_VERSION,
            "custom_intent_version": SicpInfoFields.CUSTOM_INTENT_VERSION,
        }
        for key, enum_field in fields.items():
            try:
                info[key] = await self._monitor.get_sicp_info(enum_field)
            except NotSupportedOrNotAvailableError:
                info[key] = "N/A"
            except (IndexError, NetworkError, RuntimeError):
                _LOGGER.debug("Unable to read %s from SICP info", key, exc_info=True)
        return info


class PhilipsSicpCoordinator(DataUpdateCoordinator[SicpDisplayData]):
    """DataUpdateCoordinator used by the entities."""

    def __init__(self, hass: HomeAssistant, client: SicpDisplayClient, config_entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{config_entry.title}",
            config_entry=config_entry,
            update_interval=UPDATE_INTERVAL,
            request_refresh_debouncer=Debouncer(
                hass,
                _LOGGER,
                cooldown=REQUEST_REFRESH_DELAY,
                immediate=False,
            ),
        )
        self._client = client
        self._lock = asyncio.Lock()

    async def _async_update_data(self) -> SicpDisplayData:
        """Fetch data from SICP endpoint in display."""
        try:
            self.data = await self.async_call_client(self._client.fetch_status)
        except NetworkError as exc:
            raise UpdateFailed("Unable to reach Philips display") from exc
        except Exception as exc:  # noqa: BLE001
            raise UpdateFailed(str(exc)) from exc
        return self.data

    @property
    def client(self) -> SicpDisplayClient:
        """Expose the underlying client to entities for control operations."""
        return self._client

    async def async_call_client(self, func, *args):
        """Serialize access to the SICP client and await the result."""
        async with self._lock:
            result = func(*args)
            if inspect.isawaitable(result):
                return await result
            return result

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
