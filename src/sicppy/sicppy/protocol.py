import string
from abc import abstractmethod
import logging

from .messages import (
    construct_message,
    SICPCommand,
    build_video_parameters_set_message,
    build_volume_set_message,
    SICP_INFO_LABELS,
    MODEL_INFO_LABELS,
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

def _format_color_temperature_label(label):
    condensed = label.replace('-', '')
    if condensed.isdigit():
        return f"{condensed}k"
    if condensed.endswith('k') and condensed[:-1].isdigit():
        return f"{condensed[:-1]}k"
    if condensed.startswith('k') and condensed[1:].isdigit():
        return f"{condensed[1:]}k"
    return label


def _normalize_enum_name(enum_cls, raw_name):
    label = raw_name.lower().replace('_', '-')
    if enum_cls is ColorTemperatureMode:
        return _format_color_temperature_label(label)
    return label


def _normalize_enum_token(enum_cls, token):
    label = str(token).lower().replace('_', '-').replace(' ', '-').strip()
    if enum_cls is ColorTemperatureMode:
        return _format_color_temperature_label(label)
    return label


def _enum_label(enum_cls, value):
    """Return kebab-case label for enum value or fallback to hex."""
    try:
        member = enum_cls(value)
    except ValueError:
        if isinstance(value, int):
            return f"0x{value:02X}"
        return str(value)

    return _normalize_enum_name(enum_cls, member.name)


def _enum_choice_names(enum_cls):
    labels = []
    seen = set()
    for name in enum_cls.__members__:
        label = _normalize_enum_name(enum_cls, name)
        if label not in seen:
            labels.append(label)
            seen.add(label)
    return sorted(labels)


def _parse_enum_token(enum_cls, token):
    if isinstance(token, enum_cls):
        return token

    if isinstance(token, int):
        try:
            return enum_cls(token)
        except ValueError as exc:
            raise ValueError from exc

    normalized = _normalize_enum_token(enum_cls, token)

    for name, member in enum_cls.__members__.items():
        if _normalize_enum_name(enum_cls, name) == normalized:
            return member

    try:
        value = int(str(token), 0)
    except ValueError as exc:
        raise ValueError from exc

    return enum_cls(value)

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
    def send_message(self, message, expect_data=False) -> SicpResponse | None:
        """Abstract method to send a SICP message to the display."""
        pass

    def set_power(self, power_on:bool):
        """Control display power state."""
        param = PowerState.POWER_ON if power_on else PowerState.POWER_OFF
        message = construct_message(self.monitor_id, SICPCommand.POWER_STATE_SET, param)

        action_description = "Screen ON" if power_on else "Screen OFF"
        logger.debug(f"Sending power control message: {action_description} to Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_power_state(self):
        """Query current power state (returns 0x01 off, 0x02 on)."""
        message = construct_message(self.monitor_id, SICPCommand.POWER_STATE_GET)
        logger.debug(f"Get power state for Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            state_code = response.data_payload[0]
            if state_code == PowerState.POWER_ON:
                print("  Power state: ON")
            elif state_code == PowerState.POWER_OFF:
                print("  Power state: OFF")
            else:
                print(f"  Power state: 0x{state_code:02X} (unknown)")
            return state_code

        return None


    def get_cold_start_power_state(self):
        """Query cold-start power behavior (0x00 off, 0x01 forced on, 0x02 last status)."""
        message = construct_message(self.monitor_id, SICPCommand.COLD_START_GET)
        logger.debug(f"Get cold-start power state for Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            state_code = response.data_payload[0]
            label = _enum_label(ColdStartPowerState, state_code)
            print(f"  Cold-start power state: {label}")
            return state_code

        return None


    def set_cold_start_power_state(self, state_code):
        """Set cold-start power behavior."""
        message = construct_message(self.monitor_id, SICPCommand.COLD_START_SET, state_code)
        label = _enum_label(ColdStartPowerState, state_code)
        action = f"Set cold-start power state to {label}"
        logger.debug(f"Sending cold-start power state message: {action} to Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_temperature(self):
        """Read temperature sensors (returns list of Celsius values)."""
        message = construct_message(self.monitor_id, SICPCommand.TEMPERATURE_GET)
        logger.debug(f"Get temperature for Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response:
            payload = response.data_payload
            if payload and payload[0] == SICPCommand.TEMPERATURE_GET:
                payload = payload[1:]

            if not payload:
                print("  No temperature data reported")
                return None

            temps = []
            for idx, value in enumerate(payload, start=1):
                # Some platforms may return invalid 0xFF for unused sensors
                if value == 0xFF:
                    continue
                print(f"  Temperature sensor {idx}: {value}°C")
                temps.append(value)

            if temps:
                return temps

            print("  No valid temperature values reported")

        return None


    def get_sicp_info(self, label_code):
        """Retrieve SICP version/platform info text for the requested label code."""
        message = construct_message(self.monitor_id, SICPCommand.SICP_INFO_GET, label_code)
        label = SICP_INFO_LABELS.get(label_code, f"0x{label_code:02X}")
        logger.debug(f"Get SICP info ({label}) for Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.SICP_INFO_GET and len(payload) > 1:
                payload = payload[1:]

            info_text = ''.join(chr(b) for b in payload if 32 <= b <= 126)
            print(f"  {label}: {info_text or '(no data)'}")
            return info_text

        return None


    def get_model_info(self, label_code):
        """Retrieve model/firmware/build information for the given label code."""
        message = construct_message(self.monitor_id, SICPCommand.MODEL_INFO_GET, label_code)
        label = MODEL_INFO_LABELS.get(label_code, f"0x{label_code:02X}")
        logger.debug(f"Get model info ({label}) for Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.MODEL_INFO_GET and len(payload) > 1:
                payload = payload[1:]

            text = ''.join(chr(b) for b in payload if 32 <= b <= 126)
            print(f"  {label}: {text or '(no data)'}")
            return text

        return None


    def get_serial_number(self):
        """Fetch the 14-character display serial number."""
        message = construct_message(self.monitor_id, SICPCommand.SERIAL_GET)
        logger.debug(f"Get serial number for Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.SERIAL_GET and len(payload) > 1:
                payload = payload[1:]

            serial_chars = [chr(b) for b in payload if 32 <= b <= 126]
            serial = ''.join(serial_chars)
            print(f"  Serial number: {serial or '(no data)'}")
            return serial

        return None


    def get_video_signal_status(self):
        """Determine if a video signal is present on the active input."""
        message = construct_message(self.monitor_id, SICPCommand.VIDEO_SIGNAL_GET)
        logger.debug(f"Get video signal status for Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.VIDEO_SIGNAL_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                status = payload[0]
                present = status == 0x01
                print(f"  Video signal: {'present' if present else 'not present'}")
                return present

        return None


    def get_picture_style(self):
        """Retrieve the current picture style value."""
        message = construct_message(self.monitor_id, SICPCommand.PICTURE_STYLE_GET)
        logger.debug(f"Get picture style for Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.PICTURE_STYLE_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                style_code = payload[0]
                style_name = _enum_label(PictureStyle, style_code)
                print(f"  Picture style: {style_name}")
                return style_code

        return None


    def set_picture_style(self, style_code):
        """Set the picture style to the provided code."""
        message = construct_message(self.monitor_id, SICPCommand.PICTURE_STYLE_SET, style_code)
        style_name = _enum_label(PictureStyle, style_code)
        logger.debug(f"Set picture style to {style_name} for Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def set_brightness_level(self, brightness_percent):
        """Set user brightness (0-100%) via video parameters (SICP 8.10)."""
        try:
            brightness_value = int(brightness_percent)
        except (TypeError, ValueError) as exc:
            raise ValueError("Brightness value must be an integer") from exc

        clamped_value = max(0, min(100, brightness_value))

        message = build_video_parameters_set_message(self.monitor_id, brightness=clamped_value)
        action = f"Set brightness to {clamped_value}%"
        logger.debug(f"Sending brightness set message: {action} to Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_brightness_level(self):
        """Retrieve current brightness percentage via video parameters (SICP 8.10)."""
        message = construct_message(self.monitor_id, SICPCommand.VIDEO_PARAMETERS_GET)
        logger.debug(f"Sending get brightness to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.VIDEO_PARAMETERS_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                brightness = payload[0]
                print(f"  Brightness: {brightness}%")
                return brightness

        return None

    def set_color_temperature_mode(self, mode_code):
        """Set the color temperature preset (SICP 8.11)."""
        message = construct_message(self.monitor_id, SICPCommand.COLOR_TEMPERATURE_SET, mode_code)
        label = _enum_label(ColorTemperatureMode, mode_code)
        logger.debug(f"Sending set color temperature to {label} to Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_color_temperature_mode(self):
        """Retrieve the active color temperature preset (SICP 8.11)."""
        message = construct_message(self.monitor_id, SICPCommand.COLOR_TEMPERATURE_GET)
        logger.debug(f"Sending get color temperature to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.COLOR_TEMPERATURE_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                mode_code = payload[0]
                label = _enum_label(ColorTemperatureMode, mode_code)
                print(f"  Color temperature: {label}")
                return mode_code

        return None


    def set_precise_color_temperature(self, kelvin_value):
        """Set User 2 color temperature in 100K steps (SICP 8.12)."""
        step_value, resolved_kelvin = _coerce_kelvin_to_step_value(kelvin_value)

        user2_code = ColorTemperatureMode.USER2.value
        if not self.set_color_temperature_mode(user2_code):
            print("  Failed to set base color temperature to User 2; precise adjustment skipped")
            return False

        message = construct_message(self.monitor_id, SICPCommand.COLOR_TEMPERATURE_FINE_SET, step_value)
        action = f"Set precise color temperature to {resolved_kelvin}K"
        logger.debug(f"Sending set precise color temperature message: {action} to Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_precise_color_temperature(self):
        """Read the current User 2 color temperature in 100K steps (SICP 8.12)."""
        message = construct_message(self.monitor_id, SICPCommand.COLOR_TEMPERATURE_FINE_GET)
        logger.debug(f"Sending get precise color temperature to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.COLOR_TEMPERATURE_FINE_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                step_value = payload[0]
                if not (20 <= step_value <= 100):
                    print(f"  Color temperature (precise): step {step_value}")
                    return step_value

                kelvin = step_value * 100
                print(f"  Color temperature (precise): {kelvin}K")
                return kelvin

        return None


    def get_test_pattern(self):
        """Retrieve the current internal test pattern (SICP 8.24)."""
        message = construct_message(self.monitor_id, SICPCommand.TEST_PATTERN_GET)
        logger.debug(f"Sending get test pattern to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.TEST_PATTERN_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                pattern_code = payload[0]
                pattern_name = _enum_label(TestPattern, pattern_code)
                print(f"  Test pattern: {pattern_name}")
                return pattern_code

        return None


    def set_test_pattern(self, pattern_code):
        """Enable an internal test pattern (unsupported on some BDL models)."""
        message = construct_message(self.monitor_id, SICPCommand.TEST_PATTERN_SET, pattern_code)
        pattern_name = _enum_label(TestPattern, pattern_code)
        logger.debug(f"Sending set test pattern to {pattern_name} for Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_remote_lock_state(self):
        """Retrieve the current remote control/keypad lock mode."""
        message = construct_message(self.monitor_id, SICPCommand.REMOTE_LOCK_GET)
        logger.debug(f"Sending get remote lock state to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.REMOTE_LOCK_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                state_code = payload[0]
                state_name = _enum_label(RemoteLockState, state_code)
                print(f"  Remote lock state: {state_name}")
                return state_code

        return None


    def set_remote_lock_state(self, state_code):
        """Set the remote control/keypad lock mode."""
        message = construct_message(self.monitor_id, SICPCommand.REMOTE_LOCK_SET, state_code)
        state_name = _enum_label(RemoteLockState, state_code)
        logger.debug(f"Sending set remote lock to {state_name} for Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def simulate_remote_key(self, key_code):
        """Simulate a button press on the remote control (SICP 7.2)."""
        reserved = 0x00
        message = construct_message(self.monitor_id, SICPCommand.REMOTE_CONTROL_SIM, key_code, reserved)
        key_name = _enum_label(RemoteKey, key_code)
        logger.debug(f"Sending simulate remote key {key_name} to Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_power_on_logo_mode(self):
        """Retrieve the power-on logo mode (off|on|user)."""
        message = construct_message(self.monitor_id, SICPCommand.POWER_ON_LOGO_GET)
        logger.debug(f"Sending get power-on logo to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.POWER_ON_LOGO_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                mode_code = payload[0]
                mode_name = _enum_label(PowerOnLogoMode, mode_code)
                print(f"  Power-on logo: {mode_name}")
                return mode_code

        return None


    def set_power_on_logo_mode(self, mode_code):
        """Set the power-on logo mode (SICP 11.1)."""
        message = construct_message(self.monitor_id, SICPCommand.POWER_ON_LOGO_SET, mode_code)
        mode_name = _enum_label(PowerOnLogoMode, mode_code)
        logger.debug(f"Sending set power-on logo to {mode_name} for Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_osd_info_timeout(self):
        """Retrieve the information OSD timeout (0=off, 1-60 seconds)."""
        message = construct_message(self.monitor_id, SICPCommand.OSD_INFO_GET)
        logger.debug(f"Sending get information OSD to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.OSD_INFO_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                timeout_code = payload[0]
                if timeout_code == 0:
                    print("  Information OSD: off")
                else:
                    print(f"  Information OSD: {timeout_code} sec")
                return timeout_code

        return None


    def set_osd_info_timeout(self, timeout_code):
        """Set the information OSD timeout (0=off, 1-60 seconds)."""
        if not (0 <= timeout_code <= 0x3C):
            raise ValueError("OSD timeout must be 0 (off) or between 1 and 60 seconds")

        message = construct_message(self.monitor_id, SICPCommand.OSD_INFO_SET, timeout_code)
        label = "off" if timeout_code == 0 else f"{timeout_code} sec"
        logger.debug(f"Sending set information OSD to {label} for Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_auto_signal_mode(self):
        """Retrieve the auto signal detection mode (SICP 5.4)."""
        message = construct_message(self.monitor_id, SICPCommand.AUTO_SIGNAL_GET)
        logger.debug(f"Sending get auto signal detection to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.AUTO_SIGNAL_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                mode_code = payload[0]
                mode_name = _enum_label(AutoSignalMode, mode_code)
                print(f"  Auto signal detection: {mode_name}")
                return mode_code

        return None


    def set_auto_signal_mode(self, mode_code):
        """Set the auto signal detection mode."""
        if not (0 <= mode_code <= 0x05):
            raise ValueError("Auto signal mode must be between 0 and 5")

        message = construct_message(self.monitor_id, SICPCommand.AUTO_SIGNAL_SET, mode_code)
        mode_name = _enum_label(AutoSignalMode, mode_code)
        logger.debug(f"Sending set auto signal detection to {mode_name} for Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_power_save_mode(self):
        """Retrieve the current power save mode."""
        message = construct_message(self.monitor_id, SICPCommand.POWER_SAVE_GET)
        logger.debug(f"Sending get power save mode to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.POWER_SAVE_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                mode_code = payload[0]
                mode_name = _enum_label(PowerSaveMode, mode_code)
                print(f"  Power save mode: {mode_name}")
                return mode_code

        return None


    def set_power_save_mode(self, mode_code):
        """Set the display power save mode."""
        message = construct_message(self.monitor_id, SICPCommand.POWER_SAVE_SET, mode_code)
        mode_name = _enum_label(PowerSaveMode, mode_code)
        logger.debug(f"Sending set power save mode to {mode_name} for Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_smart_power_level(self):
        """Retrieve the current smart power level."""
        message = construct_message(self.monitor_id, SICPCommand.SMART_POWER_GET)
        logger.debug(f"Sending get smart power level to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.SMART_POWER_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                level_code = payload[0]
                level_name = _enum_label(SmartPowerLevel, level_code)
                print(f"  Smart power level: {level_name}")
                return level_code

        return None


    def set_smart_power_level(self, level_code):
        """Set the smart power level."""
        message = construct_message(self.monitor_id, SICPCommand.SMART_POWER_SET, level_code)
        level_name = _enum_label(SmartPowerLevel, level_code)
        logger.debug(f"Sending set smart power level to {level_name} for Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_apm_mode(self):
        """Retrieve the current advanced power management mode."""
        message = construct_message(self.monitor_id, SICPCommand.APM_GET)
        logger.debug(f"Sending get advanced power management to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.APM_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                mode_code = payload[0]
                mode_name = _enum_label(ApmMode, mode_code)
                print(f"  Advanced power management: {mode_name}")
                return mode_code

        return None


    def set_apm_mode(self, mode_code):
        """Set the advanced power management mode."""
        message = construct_message(self.monitor_id, SICPCommand.APM_SET, mode_code)
        mode_name = _enum_label(ApmMode, mode_code)
        logger.debug(f"Sending set advanced power management to {mode_name} for Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_group_id(self):
        """Retrieve the current group ID (1-254, or 0xFF for off)."""
        message = construct_message(self.monitor_id, SICPCommand.GROUP_ID_GET)
        logger.debug(f"Sending get group ID to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.GROUP_ID_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                group_value = payload[0]
                label = "off" if group_value == 0xFF else str(group_value)
                print(f"  Group ID: {label}")
                return group_value

        return None


    def set_group_id(self, group_value):
        """Set the display group ID."""
        if not ((1 <= group_value <= 0xFE) or group_value == 0xFF):
            raise ValueError("Group ID must be 1-254 or 0xFF for off")

        message = construct_message(self.monitor_id, SICPCommand.GROUP_ID_SET, group_value)
        label = "off" if group_value == 0xFF else str(group_value)
        logger.debug(f"Sending set group ID to {label} for Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def set_monitor_id(self, new_monitor_id):
        """Assign a new monitor ID (1-255; 0 is reserved for broadcast)."""
        if not 1 <= new_monitor_id <= 0xFF:
            raise ValueError("Monitor ID must be between 1 and 255")

        message = construct_message(self.monitor_id, SICPCommand.MONITOR_ID_SET, new_monitor_id)
        logger.debug(f"Sending set monitor ID to {new_monitor_id} for Monitor ID {self.monitor_id}")
        response = self.send_message(message)

        if response and response.is_ack:
            print("  Reminder: update your DISPLAYS map to reflect the new ID")
            return True

        return False


    def set_backlight(self, backlight_on):
        """Control display backlight state."""
        message = construct_message(self.monitor_id, SICPCommand.BACKLIGHT_SET, 0x01 if backlight_on else 0x00)
        action = "Backlight ON" if backlight_on else "Backlight OFF"
        logger.debug(f"Sending backlight control message: {action} to Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_backlight_state(self):
        """Get current display backlight state."""
        message = construct_message(self.monitor_id, SICPCommand.BACKLIGHT_GET)
        logger.debug(f"Sending get backlight state to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)
        
        if response and response.is_data_response and len(response.data_payload) >= 1:
            # Response:  DATA[0]=0x71, DATA[1]=state (0x00=On, 0x01=Off)
            state_byte = response.data_payload[0]
            state = "ON" if state_byte == 0x01 else "OFF"
            print(f"  Current backlight:  {state}")
            return state
        
        return None


    def set_android_4k_state(self, enable_4k):
        """
        Control Android 4K mode.
        
        Available from SICP 2.11+ with displays that support this feature.
        """
        message = construct_message(self.monitor_id, SICPCommand.ANDROID_4K_SET, 0x01 if enable_4k else 0x00)
        action = "Android 4K ENABLED" if enable_4k else "Android 4K DISABLED"
        logger.debug(f"Sending Android 4K control message: {action} to Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_android_4k_state(self):
        """
        Get current Android 4K state.
        
        Available from SICP 2.11+ with displays that support this feature. 
        """
        message = construct_message(self.monitor_id, SICPCommand.ANDROID_4K_GET)
        logger.debug(f"Sending get Android 4K state to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)
        
        if response and response.is_data_response and len(response.data_payload) >= 1:
            # Response: DATA[0]=0xC6, DATA[1]=state (0x00=Disabled, 0x01=Enabled)
            state_byte = response.data_payload[0]
            state = "ENABLED" if state_byte == 0x01 else "DISABLED"
            print(f"  Android 4K: {state}")
            return state
        
        return None


    def set_wol(self, enable_wol):
        """Control Wake on LAN state."""
        message = construct_message(self.monitor_id, SICPCommand.WOL_SET, 0x01 if enable_wol else 0x00)
        action = "Wake on LAN ON" if enable_wol else "Wake on LAN OFF"
        logger.debug(f"Sending set Wake on LAN message: {action} to Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_wake_on_lan(self):
        """Retrieve the Wake on LAN (WOL) setting (0x00 off, 0x01 on)."""
        message = construct_message(self.monitor_id, SICPCommand.WOL_GET)
        logger.debug(f"Sending get Wake on LAN state to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.WOL_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                state_byte = payload[0]
                state = "ON" if state_byte == 0x01 else "OFF"
                print(f"  Wake on LAN: {state}")
                return state

        return None

    def set_volume(self, speaker_level=None, audio_out_level=None):
        """Set speaker/audio-out volume (0-100, None = no change)."""
        def _validate(label, value):
            if value is None:
                return None
            if not 0 <= value <= 100:
                raise ValueError(f"{label} volume must be between 0 and 100")
            return value

        speaker_level = _validate("Speaker", speaker_level)
        audio_out_level = _validate("Audio out", audio_out_level)

        message = build_volume_set_message(self.monitor_id, speaker_level, audio_out_level)
        speaker_desc = "no change" if speaker_level is None else f"{speaker_level}%"
        audio_desc = "no change" if audio_out_level is None else f"{audio_out_level}%"
        action = f"Set volume (speaker={speaker_desc}, audio-out={audio_desc})"
        logger.debug(f"Sending set volume message: {action} to Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_volume(self):
        """Get current speaker/audio-out volume levels."""
        message = construct_message(self.monitor_id, SICPCommand.VOLUME_GET)
        logger.debug(f"Sending get volume to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response:
            payload = response.data_payload
            speaker = payload[0] if payload else None
            audio_out = payload[1] if len(payload) > 1 else None

            if speaker is not None:
                print(f"  Speaker volume: {speaker}%")
            if audio_out is not None:
                print(f"  Audio-out volume: {audio_out}%")
            elif speaker is not None:
                print("  Audio-out volume: not reported")
            return speaker

        return None


    def set_mute(self, mute_on):
        """Set mute state for both speaker and audio-out."""
        message = construct_message(self.monitor_id, SICPCommand.MUTE_SET, 0x01 if mute_on else 0x00)
        action = "Mute ON" if mute_on else "Mute OFF"
        logger.debug(f"Sending set mute message: {action} to Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_mute_status(self):
        """Get mute status."""
        message = construct_message(self.monitor_id, SICPCommand.MUTE_GET)
        logger.debug(f"Sending get mute status to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            mute_on = response.data_payload[0] == 0x01
            print(f"  Mute: {'ON' if mute_on else 'OFF'}")
            return mute_on

        return None


    def set_av_mute(self, mute_on):
        """Enable or disable A/V mute (backlight, audio, touch)."""
        message = construct_message(self.monitor_id, SICPCommand.AV_MUTE_SET, 0x01 if mute_on else 0x00)
        action = "A/V Mute ON" if mute_on else "A/V Mute OFF"
        logger.debug(f"Sending set A/V mute message: {action} to Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_av_mute_status(self):
        """Retrieve current A/V mute state."""
        message = construct_message(self.monitor_id, SICPCommand.AV_MUTE_GET)
        logger.debug(f"Sending get A/V mute to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == SICPCommand.AV_MUTE_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                av_mute_on = payload[0] == 0x01
                print(f"  A/V Mute: {'ON' if av_mute_on else 'OFF'}")
                return av_mute_on

        return None

    def get_ip_parameter(self, parameter_name, value_type_name='current'):
        """Get IP parameter or MAC address information."""
        try:
            parameter_member = _parse_enum_token(IPParameterCode, parameter_name)
        except ValueError:
            print(f"✗ Unknown IP parameter '{parameter_name}'")
            print(f"  Options: {', '.join(_enum_choice_names(IPParameterCode))}")
            return None

        try:
            value_type_member = _parse_enum_token(IPParameterValueType, value_type_name)
        except ValueError:
            options = '|'.join(_enum_choice_names(IPParameterValueType))
            print(f"✗ Unknown value type '{value_type_name}' (use {options})")
            return None

        parameter_code = parameter_member.value
        value_type_code = value_type_member.value

        message = construct_message(
            self.monitor_id,
            SICPCommand.IP_PARAMETER_GET,
            parameter_code,
            value_type_code,
        )
        action = f"Get {_enum_label(IPParameterCode, parameter_code).upper()} ({_enum_label(IPParameterValueType, value_type_code)})"
        logger.debug(f"Sending IP parameter get message: {action} to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)

        if not (response and response.is_data_response and response.data_payload):
            return None

        payload = response.data_payload
        if payload[0] == SICPCommand.IP_PARAMETER_GET and len(payload) > 1:
            payload = payload[1:]

        if len(payload) < 2:
            print("  Unexpected IP parameter response payload")
            return None

        reported_parameter = payload[0]
        reported_type = payload[1]
        value_bytes = payload[2:]

        formatted, ascii_text, raw_hex = _format_ip_parameter_value(reported_parameter, value_bytes)

        param_label = _enum_label(IPParameterCode, reported_parameter)
        type_label = _enum_label(IPParameterValueType, reported_type)

        print(f"  {param_label.upper()} [{type_label}]: {formatted}")
        if ascii_text and ascii_text != formatted:
            print(f"    ASCII: {ascii_text}")
        print(f"    HEX: {raw_hex}")

        return formatted

    def set_input_source(self, input_source_name, playlist=0, osd_style=1, effect_duration=0):
        """Set display input source."""
        try:
            input_member = _parse_enum_token(InputSource, input_source_name)
        except ValueError:
            print(f"✗ Unknown input source: {input_source_name}")
            print(f"  Options: {', '.join(_enum_choice_names(InputSource))}")
            return False

        input_code = input_member.value
        message = construct_message(
            self.monitor_id,
            SICPCommand.INPUT_SOURCE_SET,
            input_code,
            playlist,
            osd_style,
            effect_duration,
        )

        playlist_info = f" (playlist {playlist})" if playlist > 0 else ""
        action = f"Set input to {_enum_label(InputSource, input_code).upper()}{playlist_info}"
        logger.debug(f"Sending set input source message: {action} to Monitor ID {self.monitor_id}")
        response = self.send_message(message)
        return response and response.is_ack


    def get_input_source(self):
        """
        Get current display input source. 
        
        From SICP 5.1.2 Message-Report:
        Response format:  [size][monitor_id][0x01][0xAD][input_source][playlist][osd_style][effect][checksum]
        DATA[1] = Input Source Type/Number
        DATA[2] = Selected playlist/URL (0x00 = none, 0x01-0x07 = playlist 1-7, 0x08 = USB autoplay)
        DATA[3] = OSD Style
        DATA[4] = Effect duration
        """
        message = construct_message(self.monitor_id, SICPCommand.CURRENT_SOURCE_GET)
        logger.debug(f"Sending get input source to Monitor ID {self.monitor_id}")
        response = self.send_message(message, expect_data=True)
        
        if response and response.is_data_response and len(response. data_payload) >= 1:
            # Response: DATA[0]=0xAD (already in response. command), DATA[1]=input_source, DATA[2]=playlist, etc.
            input_code = response.data_payload[0]
            playlist = response.data_payload[1] if len(response.data_payload) > 1 else 0
            
            input_name = _enum_label(InputSource, input_code)
            
            playlist_info = ""
            if playlist == 0x08:
                playlist_info = " (USB autoplay)"
            elif playlist > 0:
                playlist_info = f" (playlist/URL {playlist})"
            
            print(f"  Current input: {input_name.upper()}{playlist_info}")
            return input_name
        
        return None

