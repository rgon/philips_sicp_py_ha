import string
from abc import abstractmethod
import logging

from .errors import NetworkError
from .messages import (
    construct_message,
    SICPCommand,
    build_video_parameters_set_message,
    build_volume_set_message,
    SicpInfoFields,
    ModelInfoFields,
    PowerState,
    ColdStartPowerState,
    PictureStyle,
    ColorTemperatureMode,
    TestPattern,
    RemoteLockState,
    RemoteKey,
    PowerOnLogoMode,
    AutoSignalMode,
    PowerSaveMode,
    SmartPowerLevel,
    ApmMode,
    IPParameterCode,
    IPParameterValueType,
    InputSource,
)

from .response import SicpResponse

logger = logging.getLogger(__name__)

def _coerce_kelvin_to_step_value(kelvin_value):
    try:
        kelvin_int = int(kelvin_value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Color temperature must be an integer in Kelvin") from exc

    step = int(round(kelvin_int / 100.0))
    step = max(20, min(100, step))
    resolved_kelvin = step * 100
    return step, resolved_kelvin

def _format_ip_parameter_value(parameter_code, value_bytes):
    ascii_text = ''.join(chr(b) for b in value_bytes if 32 <= b <= 126)
    raw_hex = ''.join(f"{b:02X}" for b in value_bytes)
    formatted = None

    if parameter_code in {0x01, 0x02, 0x03, 0x04, 0x05} and len(ascii_text) == 12 and ascii_text.isdigit():
        octets = []
        for i in range(0, 12, 3):
            octet = int(ascii_text[i:i + 3])
            octets.append(str(octet))
        formatted = '.'.join(octets)
    elif parameter_code in {0x06, 0x07}:
        if len(value_bytes) == 6:
            formatted = ':'.join(f"{b:02X}" for b in value_bytes)
        elif len(ascii_text) == 12 and all(c in string.hexdigits for c in ascii_text):
            pairs = [ascii_text[i:i + 2].upper() for i in range(0, 12, 2)]
            formatted = ':'.join(pairs)

    if not formatted:
        formatted = ascii_text or raw_hex or "(no data)"

    return formatted, ascii_text, raw_hex

class SICPProtocol:
    def __init__(self, monitor_id=1) -> None:
        self.monitor_id = monitor_id

    @abstractmethod
    async def send_message(self, message, expect_data=False) -> SicpResponse | None:
        """Abstract method to send a SICP message to the display."""
        pass

    async def set_power(self, power_on:bool):
        """Control display power state."""
        param = PowerState.POWER_ON if power_on else PowerState.POWER_OFF
        message = construct_message(self.monitor_id, SICPCommand.POWER_STATE_SET, param)

        action_description = "Screen ON" if power_on else "Screen OFF"
        logger.debug(f"Sending power control message: {action_description} to Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_power_state(self) -> PowerState:
        """Query current power state."""
        message = construct_message(self.monitor_id, SICPCommand.POWER_STATE_GET)
        logger.debug(f"Get power state for Monitor ID {self.monitor_id}")
        try:
            response = await self.send_message(message, expect_data=True)
        # if network error, return PowerState.OFFLINE
        except NetworkError as exc:
            logger.error(f"Error getting power state for Monitor ID {self.monitor_id}: {exc}")
            return PowerState.OFFLINE

        if not response or not response.data_payload:
            raise RuntimeError("Unable to read power state")

        try:
            return PowerState(response.data_payload[0])
        except ValueError as exc:
            raise ValueError(f"Unknown power state value 0x{response.data_payload[0]:02X}") from exc


    async def get_cold_start_power_state(self) -> ColdStartPowerState:
        """Query cold-start power behavior."""
        message = construct_message(self.monitor_id, SICPCommand.COLD_START_GET)
        logger.debug(f"Get cold-start power state for Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read cold-start power state")

        try:
            return ColdStartPowerState(response.data_payload[0])
        except ValueError as exc:
            raise ValueError(f"Unknown cold-start state 0x{response.data_payload[0]:02X}") from exc


    async def set_cold_start_power_state(self, state_code: ColdStartPowerState):
        """Set cold-start power behavior."""
        message = construct_message(self.monitor_id, SICPCommand.COLD_START_SET, state_code.value)
        action = f"Set cold-start power state to {state_code}"
        logger.debug(f"Sending cold-start power state message: {action} to Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_temperature(self) -> list[int] | None:
        """Read temperature sensors (returns list of Celsius values)."""
        message = construct_message(self.monitor_id, SICPCommand.TEMPERATURE_GET)
        logger.debug(f"Get temperature for Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read temperature sensors")
    
        temps = []
        for idx, value in enumerate(response.data_payload):
            # Some platforms may return invalid 0xFF for unused sensors
            if value == 0xFF:
                continue
            temps.append(value)

        if temps:
            return temps

        return None


    async def get_sicp_info(self, field: SicpInfoFields) -> str:
        """Retrieve SICP version/platform info text for the requested label code."""
        message = construct_message(self.monitor_id, SICPCommand.SICP_INFO_GET, field.value)
        logger.debug(f"Get SICP info ({field.name.lower()}) for Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read A/V mute state")

        return ''.join(chr(b) for b in response.data_payload if 32 <= b <= 126)


    async def get_model_info(self, field: ModelInfoFields) -> str:
        """Retrieve model/firmware/build information for the given label code."""
        message = construct_message(self.monitor_id, SICPCommand.MODEL_INFO_GET, field.value)
        logger.debug(f"Get model info ({field.name.lower()}) for Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read A/V mute state")

        return ''.join(chr(b) for b in response.data_payload if 32 <= b <= 126)


    async def get_serial_number(self) -> str:
        """Fetch the 14-character display serial number."""
        message = construct_message(self.monitor_id, SICPCommand.SERIAL_GET)
        logger.debug(f"Get serial number for Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read A/V mute state")

        return ''.join(chr(b) for b in response.data_payload if 32 <= b <= 126)


    async def get_video_signal_status(self) -> bool:
        """Determine if a video signal is present on the active input."""
        message = construct_message(self.monitor_id, SICPCommand.VIDEO_SIGNAL_GET)
        logger.debug(f"Get video signal status for Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read video signal status")
        return response.data_payload[0] == 0x01


    async def get_picture_style(self) -> PictureStyle:
        """Retrieve the current picture style value."""
        message = construct_message(self.monitor_id, SICPCommand.PICTURE_STYLE_GET)
        logger.debug(f"Get picture style for Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read picture style")

        try:
            return PictureStyle(response.data_payload[0])
        except ValueError as exc:
            raise ValueError(f"Unknown picture style 0x{response.data_payload[0]:02X}") from exc


    async def set_picture_style(self, style_code: PictureStyle):
        """Set the picture style to the provided code."""
        message = construct_message(self.monitor_id, SICPCommand.PICTURE_STYLE_SET, style_code.value)
        logger.debug(f"Set picture style to {style_code} for Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def set_brightness_level(self, brightness_percent:int):
        """
        Set user brightness (0-100%) via video parameters.

        Note 1: This command is not supported on below models:
            10BDLxxxxT, 24BDL4151T
        Note 2: This command is only supported on external sources(HDMI, DVI, …) and not on Android sources(Browser,
            Mediaplayer, Custom App) on all models where video parameters are greyed out in the menu when an internal
            source is active. This includes but is not restricted to the following models:
            xxBDL3452T, xxBDL3651T, xxBDL3552T, xxBDL3652T, xxBDL3052E, xxBDL4052E/00 & /02, xxBDL3550Q,
            xxBDL3650Q, xxBDL4550D
        """
        try:
            brightness_value = int(brightness_percent)
        except (TypeError, ValueError) as exc:
            raise ValueError("Brightness value must be an integer") from exc

        clamped_value = max(0, min(100, brightness_value))

        message = build_video_parameters_set_message(self.monitor_id, brightness=clamped_value)
        action = f"Set brightness to {clamped_value}%"
        logger.debug(f"Sending brightness set message: {action} to Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_brightness_level(self) -> int:
        """
        Retrieve current brightness percentage via video parameters.

        Same limitations as set_brightness_level() apply.
        """
        message = construct_message(self.monitor_id, SICPCommand.VIDEO_PARAMETERS_GET)
        logger.debug(f"Sending get brightness to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read brightness level")
        return response.data_payload[0]

    async def set_color_temperature_mode(self, mode_code: ColorTemperatureMode):
        """
        Set the color temperature preset.

        Same limitations as set_brightness_level() Note 1 and Note 2 apply.
        """
        message = construct_message(self.monitor_id, SICPCommand.COLOR_TEMPERATURE_SET, mode_code.value)
        logger.debug(f"Sending set color temperature to {mode_code} to Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_color_temperature_mode(self) -> ColorTemperatureMode:
        """
        Retrieve the active color temperature preset.

        Same limitations as set_brightness_level() Note 1 and Note 2 apply.
        """
        message = construct_message(self.monitor_id, SICPCommand.COLOR_TEMPERATURE_GET)
        logger.debug(f"Sending get color temperature to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read color temperature mode")

        try:
            return ColorTemperatureMode(response.data_payload[0])
        except ValueError as exc:
            raise ValueError(f"Unknown color temperature mode 0x{response.data_payload[0]:02X}") from exc


    async def set_precise_color_temperature(self, kelvin_value):
        """
        Set User 2 color temperature in 100K steps.

        Same limitations as set_brightness_level() Note 1 and Note 2 apply.
        This sets the color temperature mode to User 2 automatically to be able to adjust precise color temperature.
        """
        step_value, resolved_kelvin = _coerce_kelvin_to_step_value(kelvin_value)

        if not self.set_color_temperature_mode(ColorTemperatureMode.USER2):
            logger.warning("Unable to set base color temperature to User 2; precise adjustment skipped")
            return False

        message = construct_message(self.monitor_id, SICPCommand.COLOR_TEMPERATURE_FINE_SET, step_value)
        action = f"Set precise color temperature to {resolved_kelvin}K"
        logger.debug(f"Sending set precise color temperature message: {action} to Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_precise_color_temperature(self) -> int:
        """
        Same limitations as set_precise_color_temperature().
        """
        message = construct_message(self.monitor_id, SICPCommand.COLOR_TEMPERATURE_FINE_GET)
        logger.debug(f"Sending get precise color temperature to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read precise color temperature")

        step_value = response.data_payload[0]
        if 20 <= step_value <= 100:
            return step_value * 100

        return step_value


    async def get_test_pattern(self) -> TestPattern:
        """
        Retrieve the current internal test pattern (SICP 2.06 onwards).
        """
        message = construct_message(self.monitor_id, SICPCommand.TEST_PATTERN_GET)
        logger.debug(f"Sending get test pattern to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read test pattern")

        try:
            return TestPattern(response.data_payload[0])
        except ValueError as exc:
            raise ValueError(f"Unknown test pattern code 0x{response.data_payload[0]:02X}") from exc


    async def set_test_pattern(self, pattern_code: TestPattern):
        """
        Enable an internal test pattern (unsupported on some BDL models).

        This command is not supported on the xxBDL4550D / xxBDL3550Q / xxBDL3452T / xxBDL3651T.
        Supported from SICP version 2.06 onwards.
        """
        message = construct_message(self.monitor_id, SICPCommand.TEST_PATTERN_SET, pattern_code.value)
        logger.debug(f"Sending set test pattern to {pattern_code} for Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_remote_lock_state(self) -> RemoteLockState:
        """Retrieve the current remote control/keypad lock mode."""
        message = construct_message(self.monitor_id, SICPCommand.REMOTE_LOCK_GET)
        logger.debug(f"Sending get remote lock state to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read remote lock state")

        try:
            return RemoteLockState(response.data_payload[0])
        except ValueError as exc:
            raise ValueError(f"Unknown remote lock state 0x{response.data_payload[0]:02X}") from exc


    async def set_remote_lock_state(self, state_code: RemoteLockState):
        """Set the remote control/keypad lock mode."""
        message = construct_message(self.monitor_id, SICPCommand.REMOTE_LOCK_SET, state_code.value)
        logger.debug(f"Sending set remote lock to {state_code} for Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def simulate_remote_key(self, key_code: RemoteKey):
        """Simulate a button press on the remote control (SICP 2.10 onwards)."""
        reserved = 0x00
        message = construct_message(self.monitor_id, SICPCommand.REMOTE_CONTROL_SIM, key_code.value, reserved)
        logger.debug(f"Sending simulate remote key {key_code} to Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_power_on_logo_mode(self) -> PowerOnLogoMode:
        """Retrieve the power-on logo mode (off|on|user)."""
        message = construct_message(self.monitor_id, SICPCommand.POWER_ON_LOGO_GET)
        logger.debug(f"Sending get power-on logo to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read power-on logo mode")

        try:
            return PowerOnLogoMode(response.data_payload[0])
        except ValueError as exc:
            raise ValueError(f"Unknown power-on logo mode 0x{response.data_payload[0]:02X}") from exc


    async def set_power_on_logo_mode(self, mode: PowerOnLogoMode):
        """Set the power-on logo mode. User mode must be set in the admin options (Home + 1888) and uploading an android bootanimation file."""
        message = construct_message(self.monitor_id, SICPCommand.POWER_ON_LOGO_SET, mode.value)
        logger.debug(f"Sending set power-on logo to {mode} for Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_osd_info_timeout(self) -> int:
        """Retrieve the information OSD timeout (0=off, 1-60 seconds)."""
        message = construct_message(self.monitor_id, SICPCommand.OSD_INFO_GET)
        logger.debug(f"Sending get information OSD to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read information OSD timeout")
        return response.data_payload[0]


    async def set_osd_info_timeout(self, timeout: int):
        """Set the information OSD timeout (0=off, 1-60 seconds)."""
        if not (0 <= timeout <= 0x3C):
            raise ValueError("OSD timeout must be 0 (off) or between 1 and 60 seconds")

        message = construct_message(self.monitor_id, SICPCommand.OSD_INFO_SET, timeout)
        label = "off" if timeout == 0 else f"{timeout} sec"
        logger.debug(f"Sending set information OSD to {label} for Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_auto_signal_mode(self) -> AutoSignalMode:
        """Retrieve the auto signal detection mode (SICP 2.05 onwards)."""
        message = construct_message(self.monitor_id, SICPCommand.AUTO_SIGNAL_GET)
        logger.debug(f"Sending get auto signal detection to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read auto signal mode")

        try:
            return AutoSignalMode(response.data_payload[0])
        except ValueError as exc:
            raise ValueError(f"Unknown auto signal mode 0x{response.data_payload[0]:02X}") from exc


    async def set_auto_signal_mode(self, mode: AutoSignalMode):
        """Set the auto signal detection mode."""
        if not (0 <= mode.value <= 0x05):
            raise ValueError("Auto signal mode must be between 0 and 5")

        message = construct_message(self.monitor_id, SICPCommand.AUTO_SIGNAL_SET, mode.value)
        logger.debug(f"Sending set auto signal detection to {mode} for Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_power_save_mode(self) -> PowerSaveMode:
        """Retrieve the current power save mode."""
        message = construct_message(self.monitor_id, SICPCommand.POWER_SAVE_GET)
        logger.debug(f"Sending get power save mode to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read power save mode")

        try:
            return PowerSaveMode(response.data_payload[0])
        except ValueError as exc:
            raise ValueError(f"Unknown power save mode 0x{response.data_payload[0]:02X}") from exc


    async def set_power_save_mode(self, mode: PowerSaveMode):
        """Set the display power save mode."""
        message = construct_message(self.monitor_id, SICPCommand.POWER_SAVE_SET, mode.value)
        logger.debug(f"Sending set power save mode to {mode} for Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_smart_power_level(self) -> SmartPowerLevel:
        """Retrieve the current smart power level."""
        message = construct_message(self.monitor_id, SICPCommand.SMART_POWER_GET)
        logger.debug(f"Sending get smart power level to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read smart power level")

        try:
            return SmartPowerLevel(response.data_payload[0])
        except ValueError as exc:
            raise ValueError(f"Unknown smart power level 0x{response.data_payload[0]:02X}") from exc


    async def set_smart_power_level(self, level: SmartPowerLevel):
        """
        Set the smart power level.

        Smart Power control is not relative to brightness control:
            OFF: no adaptation
            MEDIUM: 80% of power consumption relative to current settings
            HIGH: 65% of power consumption relative to current settings
        """
        message = construct_message(self.monitor_id, SICPCommand.SMART_POWER_SET, level.value)
        logger.debug(f"Sending set smart power level to {level} for Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_apm_mode(self) -> ApmMode:
        """Retrieve the current advanced power management mode."""
        message = construct_message(self.monitor_id, SICPCommand.APM_GET)
        logger.debug(f"Sending get advanced power management to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read advanced power management mode")

        try:
            return ApmMode(response.data_payload[0])
        except ValueError as exc:
            raise ValueError(f"Unknown APM mode 0x{response.data_payload[0]:02X}") from exc


    async def set_apm_mode(self, mode: ApmMode):
        """Set the advanced power management mode."""
        message = construct_message(self.monitor_id, SICPCommand.APM_SET, mode.value)
        logger.debug(f"Sending set advanced power management to {mode} for Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_group_id(self) -> int:
        """Retrieve the current group ID (1-254, or 0xFF for off)."""
        message = construct_message(self.monitor_id, SICPCommand.GROUP_ID_GET)
        logger.debug(f"Sending get group ID to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read group ID")
        return response.data_payload[0]


    async def set_group_id(self, group_value: int):
        """Set the display group ID."""
        if not ((1 <= group_value <= 0xFE) or group_value == 0xFF):
            raise ValueError("Group ID must be 1-254 or 0xFF for off")

        message = construct_message(self.monitor_id, SICPCommand.GROUP_ID_SET, group_value)
        label = "off" if group_value == 0xFF else str(group_value)
        logger.debug(f"Sending set group ID to {label} for Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def set_monitor_id(self, new_monitor_id: int):
        """Assign a new monitor ID (1-255; 0 is reserved for broadcast)."""
        if not 1 <= new_monitor_id <= 0xFF:
            raise ValueError("Monitor ID must be between 1 and 255")

        message = construct_message(self.monitor_id, SICPCommand.MONITOR_ID_SET, new_monitor_id)
        logger.debug(f"Sending set monitor ID to {new_monitor_id} for Monitor ID {self.monitor_id}")
        response = await self.send_message(message)

        if response and response.is_ack:
            logger.info("Monitor ID updated to %s", new_monitor_id)
            self.monitor_id = new_monitor_id
            return True

        return False


    async def set_backlight(self, backlight_on: bool):
        """Control display backlight state."""
        message = construct_message(self.monitor_id, SICPCommand.BACKLIGHT_SET, 0x00 if backlight_on else 0x01)
        action = "Backlight ON" if backlight_on else "Backlight OFF"
        logger.debug(f"Sending backlight control message: {action} to Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_backlight_state(self) -> bool:
        """Get current display backlight state."""
        message = construct_message(self.monitor_id, SICPCommand.BACKLIGHT_GET)
        logger.debug(f"Sending get backlight state to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read backlight state")

        state_byte = response.data_payload[0]
        # Spec indicates 0x00 = On, 0x01 = Off
        return state_byte == 0x00


    async def set_android_4k_state(self, enable_4k: bool):
        """
        Control Android 4K mode.
        
        Available from SICP 2.11 onwards.
        """
        message = construct_message(self.monitor_id, SICPCommand.ANDROID_4K_SET, 0x01 if enable_4k else 0x00)
        action = "Android 4K ENABLED" if enable_4k else "Android 4K DISABLED"
        logger.debug(f"Sending Android 4K control message: {action} to Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_android_4k_state(self) -> bool:
        """Get current Android 4K state."""
        message = construct_message(self.monitor_id, SICPCommand.ANDROID_4K_GET)
        logger.debug(f"Sending get Android 4K state to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read Android 4K state")

        state_byte = response.data_payload[0]
        return state_byte == 0x01


    async def set_wol(self, enable_wol: bool):
        """Control Wake on LAN state."""
        message = construct_message(self.monitor_id, SICPCommand.WOL_SET, 0x01 if enable_wol else 0x00)
        action = "Wake on LAN ON" if enable_wol else "Wake on LAN OFF"
        logger.debug(f"Sending set Wake on LAN message: {action} to Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_wake_on_lan(self) -> bool:
        """Retrieve the Wake on LAN (WOL) setting (0x00 off, 0x01 on)."""
        message = construct_message(self.monitor_id, SICPCommand.WOL_GET)
        logger.debug(f"Sending get Wake on LAN state to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read Wake on LAN state")

        return response.data_payload[0] == 0x01

    async def set_volume(self, speaker_level: int|None = None, audio_out_level: int|None = None):
        """Set speaker/audio-out volume (0-100, None = no change)."""
        if speaker_level is not None and not 0 <= speaker_level <= 100:
            raise ValueError("Speaker volume must be between 0 and 100")

        if audio_out_level is not None and not 0 <= audio_out_level <= 100:
            raise ValueError("Audio out volume must be between 0 and 100")

        message = build_volume_set_message(self.monitor_id, speaker_level, audio_out_level)
        speaker_desc = "no change" if speaker_level is None else f"{speaker_level}%"
        audio_desc = "no change" if audio_out_level is None else f"{audio_out_level}%"
        action = f"Set volume (speaker={speaker_desc}, audio-out={audio_desc})"
        logger.debug(f"Sending set volume message: {action} to Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_volume(self) -> tuple[int, int | None]:
        """Get current speaker/audio-out volume levels."""
        message = construct_message(self.monitor_id, SICPCommand.VOLUME_GET)
        logger.debug(f"Sending get volume to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read volume levels")

        speaker = response.data_payload[0]
        audio_out = response.data_payload[1] if len(response.data_payload) > 1 else None
        return speaker, audio_out


    async def set_mute(self, mute_on: bool):
        """Set mute state for both speaker and audio-out."""
        message = construct_message(self.monitor_id, SICPCommand.MUTE_SET, 0x01 if mute_on else 0x00)
        action = "Mute ON" if mute_on else "Mute OFF"
        logger.debug(f"Sending set mute message: {action} to Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_mute(self) -> bool:
        """Get mute status."""
        message = construct_message(self.monitor_id, SICPCommand.MUTE_GET)
        logger.debug(f"Sending get mute status to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read mute status")

        return response.data_payload[0] == 0x01


    async def set_av_mute(self, mute_on: bool):
        """Enable or disable A/V mute (backlight, audio, touch)."""
        message = construct_message(self.monitor_id, SICPCommand.AV_MUTE_SET, 0x01 if mute_on else 0x00)
        action = "A/V Mute ON" if mute_on else "A/V Mute OFF"
        logger.debug(f"Sending set A/V mute message: {action} to Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_av_mute(self) -> bool:
        """Retrieve current A/V mute state."""
        message = construct_message(self.monitor_id, SICPCommand.AV_MUTE_GET)
        logger.debug(f"Sending get A/V mute to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read A/V mute state")

        return response.data_payload[0] == 0x01

    async def get_ip_parameter(
        self,
        parameter: IPParameterCode,
        value_type: IPParameterValueType = IPParameterValueType.CURRENT,
    ) -> str:
        """Get IP parameter or MAC address information."""

        parameter_code = parameter.value
        value_type_code = value_type.value

        message = construct_message(
            self.monitor_id,
            SICPCommand.IP_PARAMETER_GET,
            parameter_code,
            value_type_code,
        )
        action = f"Get {parameter} ({value_type})"
        logger.debug(f"Sending IP parameter get message: {action} to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read A/V mute state")

        if len(response.data_payload) < 2:
            raise RuntimeError("Unexpected IP parameter response payload")

        reported_parameter = response.data_payload[0]
        _reported_type = response.data_payload[1]
        value_bytes = response.data_payload[2:]

        formatted, _, _ = _format_ip_parameter_value(reported_parameter, value_bytes)
        return formatted

    async def set_input_source(
        self,
        input_source: InputSource,
        playlist: int = 0,
        osd_style: int = 1,
        effect_duration: int = 0,
    ):
        """Set display input source."""
        message = construct_message(
            self.monitor_id,
            SICPCommand.INPUT_SOURCE_SET,
            input_source.value,
            playlist,
            osd_style,
            effect_duration,
        )

        playlist_info = f" (playlist {playlist})" if playlist > 0 else ""
        action = f"Set input to {input_source}{playlist_info}"
        logger.debug(f"Sending set input source message: {action} to Monitor ID {self.monitor_id}")
        response = await self.send_message(message)
        return response and response.is_ack


    async def get_input_source(self) -> InputSource:
        """Get current display input source."""
        message = construct_message(self.monitor_id, SICPCommand.CURRENT_SOURCE_GET)
        logger.debug(f"Sending get input source to Monitor ID {self.monitor_id}")
        response = await self.send_message(message, expect_data=True)
        if not response or not response.data_payload:
            raise RuntimeError("Unable to read current input source")

        try:
            return InputSource(response.data_payload[0])
        except ValueError as exc:
            raise ValueError(f"Unknown input source code 0x{response.data_payload[0]:02X}") from exc

