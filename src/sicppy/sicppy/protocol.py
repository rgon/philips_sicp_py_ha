import string
from abc import abstractmethod

from .messages import build_power_message, build_power_get_message, POWER_ON, POWER_OFF, build_cold_start_get_message, \
    COLD_START_STATE_NAMES, build_cold_start_set_message, build_temperature_get_message, CMD_TEMPERATURE_GET, \
    build_sicp_info_get_message, SICP_INFO_LABELS, CMD_SICP_INFO_GET, build_model_info_get_message, MODEL_INFO_LABELS, \
    CMD_MODEL_INFO_GET, build_serial_get_message, CMD_SERIAL_GET, build_video_signal_get_message, CMD_VIDEO_SIGNAL_GET, \
    build_picture_style_get_message, PICTURE_STYLE_NAMES, CMD_PICTURE_STYLE_GET, build_picture_style_set_message, \
    build_video_parameters_set_message, build_video_parameters_get_message, CMD_VIDEO_PARAMETERS_GET, \
    build_color_temperature_set_message, COLOR_TEMPERATURE_NAMES, CMD_COLOR_TEMPERATURE_GET, COLOR_TEMPERATURE_MODES, \
    build_color_temperature_get_message, build_color_temperature_fine_set_message, \
    build_color_temperature_fine_get_message, CMD_COLOR_TEMPERATURE_FINE_GET, build_test_pattern_get_message, \
    TEST_PATTERN_NAMES, CMD_TEST_PATTERN_GET, build_test_pattern_set_message, build_remote_lock_get_message, \
    REMOTE_LOCK_STATE_NAMES, CMD_REMOTE_LOCK_GET, build_remote_lock_set_message, build_remote_key_simulation_message, \
    REMOTE_KEY_NAMES, build_power_on_logo_get_message, POWER_ON_LOGO_MODE_NAMES, CMD_POWER_ON_LOGO_GET, \
    build_power_on_logo_set_message, build_osd_info_get_message, CMD_OSD_INFO_GET, build_osd_info_set_message, \
    build_auto_signal_get_message, AUTO_SIGNAL_MODE_NAMES, CMD_AUTO_SIGNAL_GET, build_auto_signal_set_message, \
    build_power_save_get_message, POWER_SAVE_MODE_NAMES, CMD_POWER_SAVE_GET, build_power_save_set_message, \
    build_smart_power_get_message, SMART_POWER_LEVEL_NAMES, CMD_SMART_POWER_GET, build_smart_power_set_message, \
    build_apm_get_message, APM_MODE_NAMES, CMD_APM_GET, build_apm_set_message, build_group_id_get_message, \
    CMD_GROUP_ID_GET, build_group_id_set_message, build_monitor_id_set_message, build_backlight_set_message, \
    BACKLIGHT_ON, build_backlight_get_message, build_android_4k_set_message, ANDROID_4K_ENABLED, \
    build_android_4k_get_message, build_wol_set_message, build_wol_get_message, WOL_ENABLED, CMD_WOL_GET, \
    build_volume_set_message, build_volume_get_message, build_mute_get_message, build_mute_set_message, \
    build_av_mute_get_message, build_av_mute_set_message, CMD_AV_MUTE_GET, \
    build_ip_parameter_get_message, CMD_IP_PARAMETER_GET, IP_PARAMETER_NAMES, IP_PARAMETER_VALUE_TYPES, IP_PARAMETER_VALUE_TYPE_NAMES, IP_PARAMETER_CODES, \
    build_input_source_message, build_get_input_source_message, INPUT_SOURCES, INPUT_SOURCE_NAMES

from .response import SicpResponse

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
    @abstractmethod
    def send_message(self, message, action_description, expect_data=False) -> SicpResponse | None:
        """Abstract method to send a SICP message to the display."""
        pass

    def power_control(self, monitor_id, power_on):
        """Control display power state."""
        message = build_power_message(monitor_id, power_on)
        action_description = "Screen ON" if power_on else "Screen OFF"
        response = self.send_message(message, action_description)
        return response and response.is_ack


    def get_power_state(self, monitor_id):
        """Query current power state (returns 0x01 off, 0x02 on)."""
        message = build_power_get_message(monitor_id)
        response = self.send_message(message, "Get power state", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            state_code = response.data_payload[0]
            if state_code == POWER_ON:
                print("  Power state: ON")
            elif state_code == POWER_OFF:
                print("  Power state: OFF")
            else:
                print(f"  Power state: 0x{state_code:02X} (unknown)")
            return state_code

        return None


    def get_cold_start_power_state(self, monitor_id):
        """Query cold-start power behavior (0x00 off, 0x01 forced on, 0x02 last status)."""
        message = build_cold_start_get_message(monitor_id)
        response = self.send_message(message, "Get cold-start power state", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            state_code = response.data_payload[0]
            label = COLD_START_STATE_NAMES.get(state_code, f"0x{state_code:02X}")
            print(f"  Cold-start power state: {label}")
            return state_code

        return None


    def set_cold_start_power_state(self, monitor_id, state_code):
        """Set cold-start power behavior."""
        message = build_cold_start_set_message(monitor_id, state_code)
        label = COLD_START_STATE_NAMES.get(state_code, f"0x{state_code:02X}")
        action = f"Set cold-start power state to {label}"
        response = self.send_message(message, action)
        return response and response.is_ack


    def get_temperature(self, monitor_id):
        """Read temperature sensors (returns list of Celsius values)."""
        message = build_temperature_get_message(monitor_id)
        response = self.send_message(message, "Get temperature", expect_data=True)

        if response and response.is_data_response:
            payload = response.data_payload
            if payload and payload[0] == CMD_TEMPERATURE_GET:
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


    def get_sicp_info(self, monitor_id, label_code):
        """Retrieve SICP version/platform info text for the requested label code."""
        message = build_sicp_info_get_message(monitor_id, label_code)
        label = SICP_INFO_LABELS.get(label_code, f"0x{label_code:02X}")
        response = self.send_message(message, f"Get SICP info ({label})", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_SICP_INFO_GET and len(payload) > 1:
                payload = payload[1:]

            info_text = ''.join(chr(b) for b in payload if 32 <= b <= 126)
            print(f"  {label}: {info_text or '(no data)'}")
            return info_text

        return None


    def get_model_info(self, monitor_id, label_code):
        """Retrieve model/firmware/build information for the given label code."""
        message = build_model_info_get_message(monitor_id, label_code)
        label = MODEL_INFO_LABELS.get(label_code, f"0x{label_code:02X}")
        response = self.send_message(message, f"Get model info ({label})", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_MODEL_INFO_GET and len(payload) > 1:
                payload = payload[1:]

            text = ''.join(chr(b) for b in payload if 32 <= b <= 126)
            print(f"  {label}: {text or '(no data)'}")
            return text

        return None


    def get_serial_number(self, monitor_id):
        """Fetch the 14-character display serial number."""
        message = build_serial_get_message(monitor_id)
        response = self.send_message(message, "Get serial number", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_SERIAL_GET and len(payload) > 1:
                payload = payload[1:]

            serial_chars = [chr(b) for b in payload if 32 <= b <= 126]
            serial = ''.join(serial_chars)
            print(f"  Serial number: {serial or '(no data)'}")
            return serial

        return None


    def get_video_signal_status(self, monitor_id):
        """Determine if a video signal is present on the active input."""
        message = build_video_signal_get_message(monitor_id)
        response = self.send_message(message, "Get video signal status", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_VIDEO_SIGNAL_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                status = payload[0]
                present = status == 0x01
                print(f"  Video signal: {'present' if present else 'not present'}")
                return present

        return None


    def get_picture_style(self, monitor_id):
        """Retrieve the current picture style value."""
        message = build_picture_style_get_message(monitor_id)
        response = self.send_message(message, "Get picture style", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_PICTURE_STYLE_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                style_code = payload[0]
                style_name = PICTURE_STYLE_NAMES.get(style_code, f"0x{style_code:02X}")
                print(f"  Picture style: {style_name}")
                return style_code

        return None


    def set_picture_style(self, monitor_id, style_code):
        """Set the picture style to the provided code."""
        message = build_picture_style_set_message(monitor_id, style_code)
        style_name = PICTURE_STYLE_NAMES.get(style_code, f"0x{style_code:02X}")
        response = self.send_message(message, f"Set picture style to {style_name}")
        return response and response.is_ack


    def set_brightness_level(self, monitor_id, brightness_percent):
        """Set user brightness (0-100%) via video parameters (SICP 8.10)."""
        try:
            brightness_value = int(brightness_percent)
        except (TypeError, ValueError) as exc:
            raise ValueError("Brightness value must be an integer") from exc

        clamped_value = max(0, min(100, brightness_value))

        message = build_video_parameters_set_message(monitor_id, brightness=clamped_value)
        action = f"Set brightness to {clamped_value}%"
        response = self.send_message(message, action)
        return response and response.is_ack


    def get_brightness_level(self, monitor_id):
        """Retrieve current brightness percentage via video parameters (SICP 8.10)."""
        message = build_video_parameters_get_message(monitor_id)
        response = self.send_message(message, "Get brightness", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_VIDEO_PARAMETERS_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                brightness = payload[0]
                print(f"  Brightness: {brightness}%")
                return brightness

        return None

    def set_color_temperature_mode(self, monitor_id, mode_code):
        """Set the color temperature preset (SICP 8.11)."""
        if not (0 <= mode_code <= 0xFF):
            raise ValueError("Color temperature code must be between 0 and 255")

        message = build_color_temperature_set_message(monitor_id, mode_code)
        label = COLOR_TEMPERATURE_NAMES.get(mode_code, f"0x{mode_code:02X}")
        response = self.send_message(message, f"Set color temperature to {label}")
        return response and response.is_ack


    def get_color_temperature_mode(self, monitor_id):
        """Retrieve the active color temperature preset (SICP 8.11)."""
        message = build_color_temperature_get_message(monitor_id)
        response = self.send_message(message, "Get color temperature", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_COLOR_TEMPERATURE_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                mode_code = payload[0]
                label = COLOR_TEMPERATURE_NAMES.get(mode_code, f"0x{mode_code:02X}")
                print(f"  Color temperature: {label}")
                return mode_code

        return None


    def set_precise_color_temperature(self, monitor_id, kelvin_value):
        """Set User 2 color temperature in 100K steps (SICP 8.12)."""
        step_value, resolved_kelvin = _coerce_kelvin_to_step_value(kelvin_value)

        user2_code = COLOR_TEMPERATURE_MODES.get('user2', 0x12)
        if user2_code is not None:
            if not self.set_color_temperature_mode(monitor_id, user2_code):
                print("  Failed to set base color temperature to User 2; precise adjustment skipped")
                return False

        message = build_color_temperature_fine_set_message(monitor_id, step_value)
        action = f"Set precise color temperature to {resolved_kelvin}K"
        response = self.send_message(message, action)
        return response and response.is_ack


    def get_precise_color_temperature(self, monitor_id):
        """Read the current User 2 color temperature in 100K steps (SICP 8.12)."""
        message = build_color_temperature_fine_get_message(monitor_id)
        response = self.send_message(message, "Get precise color temperature", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_COLOR_TEMPERATURE_FINE_GET and len(payload) > 1:
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


    def get_test_pattern(self, monitor_id):
        """Retrieve the current internal test pattern (SICP 8.24)."""
        message = build_test_pattern_get_message(monitor_id)
        response = self.send_message(message, "Get test pattern", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_TEST_PATTERN_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                pattern_code = payload[0]
                pattern_name = TEST_PATTERN_NAMES.get(pattern_code, f"0x{pattern_code:02X}")
                print(f"  Test pattern: {pattern_name}")
                return pattern_code

        return None


    def set_test_pattern(self, monitor_id, pattern_code):
        """Enable an internal test pattern (unsupported on some BDL models)."""
        message = build_test_pattern_set_message(monitor_id, pattern_code)
        pattern_name = TEST_PATTERN_NAMES.get(pattern_code, f"0x{pattern_code:02X}")
        response = self.send_message(message, f"Set test pattern to {pattern_name}")
        return response and response.is_ack


    def get_remote_lock_state(self, monitor_id):
        """Retrieve the current remote control/keypad lock mode."""
        message = build_remote_lock_get_message(monitor_id)
        response = self.send_message(message, "Get remote lock state", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_REMOTE_LOCK_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                state_code = payload[0]
                state_name = REMOTE_LOCK_STATE_NAMES.get(state_code, f"0x{state_code:02X}")
                print(f"  Remote lock state: {state_name}")
                return state_code

        return None


    def set_remote_lock_state(self, monitor_id, state_code):
        """Set the remote control/keypad lock mode."""
        message = build_remote_lock_set_message(monitor_id, state_code)
        state_name = REMOTE_LOCK_STATE_NAMES.get(state_code, f"0x{state_code:02X}")
        response = self.send_message(message, f"Set remote lock to {state_name}")
        return response and response.is_ack


    def simulate_remote_key(self, monitor_id, key_code):
        """Simulate a button press on the remote control (SICP 7.2)."""
        message = build_remote_key_simulation_message(monitor_id, key_code)
        key_name = REMOTE_KEY_NAMES.get(key_code, f"0x{key_code:02X}")
        response = self.send_message(message, f"Simulate remote key {key_name}")
        return response and response.is_ack


    def get_power_on_logo_mode(self, monitor_id):
        """Retrieve the power-on logo mode (off|on|user)."""
        message = build_power_on_logo_get_message(monitor_id)
        response = self.send_message(message, "Get power-on logo", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_POWER_ON_LOGO_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                mode_code = payload[0]
                mode_name = POWER_ON_LOGO_MODE_NAMES.get(mode_code, f"0x{mode_code:02X}")
                print(f"  Power-on logo: {mode_name}")
                return mode_code

        return None


    def set_power_on_logo_mode(self, monitor_id, mode_code):
        """Set the power-on logo mode (SICP 11.1)."""
        message = build_power_on_logo_set_message(monitor_id, mode_code)
        mode_name = POWER_ON_LOGO_MODE_NAMES.get(mode_code, f"0x{mode_code:02X}")
        response = self.send_message(message, f"Set power-on logo to {mode_name}")
        return response and response.is_ack


    def get_osd_info_timeout(self, monitor_id):
        """Retrieve the information OSD timeout (0=off, 1-60 seconds)."""
        message = build_osd_info_get_message(monitor_id)
        response = self.send_message(message, "Get information OSD", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_OSD_INFO_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                timeout_code = payload[0]
                if timeout_code == 0:
                    print("  Information OSD: off")
                else:
                    print(f"  Information OSD: {timeout_code} sec")
                return timeout_code

        return None


    def set_osd_info_timeout(self, monitor_id, timeout_code):
        """Set the information OSD timeout (0=off, 1-60 seconds)."""
        if not (0 <= timeout_code <= 0x3C):
            raise ValueError("OSD timeout must be 0 (off) or between 1 and 60 seconds")

        message = build_osd_info_set_message(monitor_id, timeout_code)
        label = "off" if timeout_code == 0 else f"{timeout_code} sec"
        response = self.send_message(message, f"Set information OSD to {label}")
        return response and response.is_ack


    def get_auto_signal_mode(self, monitor_id):
        """Retrieve the auto signal detection mode (SICP 5.4)."""
        message = build_auto_signal_get_message(monitor_id)
        response = self.send_message(message, "Get auto signal detection", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_AUTO_SIGNAL_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                mode_code = payload[0]
                mode_name = AUTO_SIGNAL_MODE_NAMES.get(mode_code, f"0x{mode_code:02X}")
                print(f"  Auto signal detection: {mode_name}")
                return mode_code

        return None


    def set_auto_signal_mode(self, monitor_id, mode_code):
        """Set the auto signal detection mode."""
        if not (0 <= mode_code <= 0x05):
            raise ValueError("Auto signal mode must be between 0 and 5")

        message = build_auto_signal_set_message(monitor_id, mode_code)
        mode_name = AUTO_SIGNAL_MODE_NAMES.get(mode_code, f"0x{mode_code:02X}")
        response = self.send_message(message, f"Set auto signal detection to {mode_name}")
        return response and response.is_ack


    def get_power_save_mode(self, monitor_id):
        """Retrieve the current power save mode."""
        message = build_power_save_get_message(monitor_id)
        response = self.send_message(message, "Get power save mode", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_POWER_SAVE_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                mode_code = payload[0]
                mode_name = POWER_SAVE_MODE_NAMES.get(mode_code, f"0x{mode_code:02X}")
                print(f"  Power save mode: {mode_name}")
                return mode_code

        return None


    def set_power_save_mode(self, monitor_id, mode_code):
        """Set the display power save mode."""
        message = build_power_save_set_message(monitor_id, mode_code)
        mode_name = POWER_SAVE_MODE_NAMES.get(mode_code, f"0x{mode_code:02X}")
        response = self.send_message(message, f"Set power save mode to {mode_name}")
        return response and response.is_ack


    def get_smart_power_level(self, monitor_id):
        """Retrieve the current smart power level."""
        message = build_smart_power_get_message(monitor_id)
        response = self.send_message(message, "Get smart power level", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_SMART_POWER_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                level_code = payload[0]
                level_name = SMART_POWER_LEVEL_NAMES.get(level_code, f"0x{level_code:02X}")
                print(f"  Smart power level: {level_name}")
                return level_code

        return None


    def set_smart_power_level(self, monitor_id, level_code):
        """Set the smart power level."""
        message = build_smart_power_set_message(monitor_id, level_code)
        level_name = SMART_POWER_LEVEL_NAMES.get(level_code, f"0x{level_code:02X}")
        response = self.send_message(message, f"Set smart power level to {level_name}")
        return response and response.is_ack


    def get_apm_mode(self, monitor_id):
        """Retrieve the current advanced power management mode."""
        message = build_apm_get_message(monitor_id)
        response = self.send_message(message, "Get advanced power management", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_APM_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                mode_code = payload[0]
                mode_name = APM_MODE_NAMES.get(mode_code, f"0x{mode_code:02X}")
                print(f"  Advanced power management: {mode_name}")
                return mode_code

        return None


    def set_apm_mode(self, monitor_id, mode_code):
        """Set the advanced power management mode."""
        message = build_apm_set_message(monitor_id, mode_code)
        mode_name = APM_MODE_NAMES.get(mode_code, f"0x{mode_code:02X}")
        response = self.send_message(message, f"Set advanced power management to {mode_name}")
        return response and response.is_ack


    def get_group_id(self, monitor_id):
        """Retrieve the current group ID (1-254, or 0xFF for off)."""
        message = build_group_id_get_message(monitor_id)
        response = self.send_message(message, "Get group ID", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_GROUP_ID_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                group_value = payload[0]
                label = "off" if group_value == 0xFF else str(group_value)
                print(f"  Group ID: {label}")
                return group_value

        return None


    def set_group_id(self, monitor_id, group_value):
        """Set the display group ID."""
        if not ((1 <= group_value <= 0xFE) or group_value == 0xFF):
            raise ValueError("Group ID must be 1-254 or 0xFF for off")

        message = build_group_id_set_message(monitor_id, group_value)
        label = "off" if group_value == 0xFF else str(group_value)
        response = self.send_message(message, f"Set group ID to {label}")
        return response and response.is_ack


    def set_monitor_id(self, monitor_id, new_monitor_id):
        """Assign a new monitor ID (1-255; 0 is reserved for broadcast)."""
        if not 1 <= new_monitor_id <= 0xFF:
            raise ValueError("Monitor ID must be between 1 and 255")

        message = build_monitor_id_set_message(monitor_id, new_monitor_id)
        response = self.send_message(message, f"Set monitor ID to {new_monitor_id}")

        if response and response.is_ack:
            print("  Reminder: update your DISPLAYS map to reflect the new ID")
            return True

        return False


    def backlight_control(self, monitor_id, backlight_on):
        """Control display backlight state."""
        message = build_backlight_set_message(monitor_id, backlight_on)
        action = "Backlight ON" if backlight_on else "Backlight OFF"
        response = self.send_message(message, action)
        return response and response.is_ack


    def get_backlight_state(self, monitor_id):
        """Get current display backlight state."""
        message = build_backlight_get_message(monitor_id)
        response = self.send_message(message, "Get backlight state", expect_data=True)
        
        if response and response.is_data_response and len(response.data_payload) >= 1:
            # Response:  DATA[0]=0x71, DATA[1]=state (0x00=On, 0x01=Off)
            state_byte = response.data_payload[0]
            state = "ON" if state_byte == BACKLIGHT_ON else "OFF"
            print(f"  Current backlight:  {state}")
            return state
        
        return None


    def android_4k_control(self, monitor_id, enable_4k):
        """
        Control Android 4K mode.
        
        Available from SICP 2.11+ with displays that support this feature.
        """
        message = build_android_4k_set_message(monitor_id, enable_4k)
        action = "Android 4K ENABLED" if enable_4k else "Android 4K DISABLED"
        response = self.send_message(message, action)
        return response and response.is_ack


    def get_android_4k_state(self, monitor_id):
        """
        Get current Android 4K state.
        
        Available from SICP 2.11+ with displays that support this feature. 
        """
        message = build_android_4k_get_message(monitor_id)
        response = self.send_message(message, "Get Android 4K state", expect_data=True)
        
        if response and response.is_data_response and len(response.data_payload) >= 1:
            # Response: DATA[0]=0xC6, DATA[1]=state (0x00=Disabled, 0x01=Enabled)
            state_byte = response.data_payload[0]
            state = "ENABLED" if state_byte == ANDROID_4K_ENABLED else "DISABLED"
            print(f"  Android 4K: {state}")
            return state
        
        return None


    def wol_control(self, monitor_id, enable_wol):
        """Control Wake on LAN state."""
        message = build_wol_set_message(monitor_id, enable_wol)
        action = "Wake on LAN ON" if enable_wol else "Wake on LAN OFF"
        response = self.send_message(message, action)
        return response and response.is_ack


    def get_wake_on_lan(self, monitor_id):
        """Retrieve the Wake on LAN (WOL) setting (0x00 off, 0x01 on)."""
        message = build_wol_get_message(monitor_id)
        response = self.send_message(message, "Get Wake on LAN state", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_WOL_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                state_byte = payload[0]
                state = "ON" if state_byte == WOL_ENABLED else "OFF"
                print(f"  Wake on LAN: {state}")
                return state

        return None

    def set_volume(self, monitor_id, speaker_level=None, audio_out_level=None):
        """Set speaker/audio-out volume (0-100, None = no change)."""
        def _validate(label, value):
            if value is None:
                return None
            if not 0 <= value <= 100:
                raise ValueError(f"{label} volume must be between 0 and 100")
            return value

        speaker_level = _validate("Speaker", speaker_level)
        audio_out_level = _validate("Audio out", audio_out_level)

        message = build_volume_set_message(monitor_id, speaker_level, audio_out_level)
        speaker_desc = "no change" if speaker_level is None else f"{speaker_level}%"
        audio_desc = "no change" if audio_out_level is None else f"{audio_out_level}%"
        action = f"Set volume (speaker={speaker_desc}, audio-out={audio_desc})"
        response = self.send_message(message, action)
        return response and response.is_ack


    def get_volume(self, monitor_id):
        """Get current speaker/audio-out volume levels."""
        message = build_volume_get_message(monitor_id)
        response = self.send_message(message, "Get volume", expect_data=True)

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


    def set_mute(self, monitor_id, mute_on):
        """Set mute state for both speaker and audio-out."""
        message = build_mute_set_message(monitor_id, mute_on)
        action = "Mute ON" if mute_on else "Mute OFF"
        response = self.send_message(message, action)
        return response and response.is_ack


    def get_mute_status(self, monitor_id):
        """Get mute status."""
        message = build_mute_get_message(monitor_id)
        response = self.send_message(message, "Get mute status", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            mute_on = response.data_payload[0] == 0x01
            print(f"  Mute: {'ON' if mute_on else 'OFF'}")
            return mute_on

        return None


    def set_av_mute(self, monitor_id, mute_on):
        """Enable or disable A/V mute (backlight, audio, touch)."""
        message = build_av_mute_set_message(monitor_id, mute_on)
        action = "A/V Mute ON" if mute_on else "A/V Mute OFF"
        response = self.send_message(message, action)
        return response and response.is_ack


    def get_av_mute_status(self, monitor_id):
        """Retrieve current A/V mute state."""
        message = build_av_mute_get_message(monitor_id)
        response = self.send_message(message, "Get A/V mute", expect_data=True)

        if response and response.is_data_response and response.data_payload:
            payload = response.data_payload
            if payload[0] == CMD_AV_MUTE_GET and len(payload) > 1:
                payload = payload[1:]

            if payload:
                av_mute_on = payload[0] == 0x01
                print(f"  A/V Mute: {'ON' if av_mute_on else 'OFF'}")
                return av_mute_on

        return None

    def get_ip_parameter(self, monitor_id, parameter_name, value_type_name='current'):
        """Get IP parameter or MAC address information."""
        if parameter_name not in IP_PARAMETER_CODES:
            print(f"✗ Unknown IP parameter '{parameter_name}'")
            print(f"  Options: {', '.join(IP_PARAMETER_CODES.keys())}")
            return None

        if value_type_name not in IP_PARAMETER_VALUE_TYPES:
            print(f"✗ Unknown value type '{value_type_name}' (use current|queued)")
            return None

        parameter_code = IP_PARAMETER_CODES[parameter_name]
        value_type_code = IP_PARAMETER_VALUE_TYPES[value_type_name]

        message = build_ip_parameter_get_message(monitor_id, parameter_code, value_type_code)
        action = f"Get {parameter_name.upper()} ({value_type_name})"
        response = self.send_message(message, action, expect_data=True)

        if not (response and response.is_data_response and response.data_payload):
            return None

        payload = response.data_payload
        if payload[0] == CMD_IP_PARAMETER_GET and len(payload) > 1:
            payload = payload[1:]

        if len(payload) < 2:
            print("  Unexpected IP parameter response payload")
            return None

        reported_parameter = payload[0]
        reported_type = payload[1]
        value_bytes = payload[2:]

        formatted, ascii_text, raw_hex = _format_ip_parameter_value(reported_parameter, value_bytes)

        param_label = IP_PARAMETER_NAMES.get(reported_parameter, f"0x{reported_parameter:02X}")
        type_label = IP_PARAMETER_VALUE_TYPE_NAMES.get(reported_type, f"0x{reported_type:02X}")

        print(f"  {param_label.upper()} [{type_label}]: {formatted}")
        if ascii_text and ascii_text != formatted:
            print(f"    ASCII: {ascii_text}")
        print(f"    HEX: {raw_hex}")

        return formatted

    def set_input_source(self, monitor_id, input_source_name, playlist=0):
        """Set display input source."""
        if input_source_name not in INPUT_SOURCES:
            print(f"✗ Unknown input source: {input_source_name}")
            print(f"Available sources: {', '.join(sorted(set(INPUT_SOURCES.keys())))}")
            return False
        
        input_code = INPUT_SOURCES[input_source_name]
        message = build_input_source_message(monitor_id, input_code, playlist=playlist)
        
        playlist_info = f" (playlist {playlist})" if playlist > 0 else ""
        action = f"Set input to {input_source_name. upper()}{playlist_info}"
        response = self.send_message(message, action)
        return response and response.is_ack


    def get_input_source(self, monitor_id):
        """
        Get current display input source. 
        
        From SICP 5.1.2 Message-Report:
        Response format:  [size][monitor_id][0x01][0xAD][input_source][playlist][osd_style][effect][checksum]
        DATA[1] = Input Source Type/Number
        DATA[2] = Selected playlist/URL (0x00 = none, 0x01-0x07 = playlist 1-7, 0x08 = USB autoplay)
        DATA[3] = OSD Style
        DATA[4] = Effect duration
        """
        message = build_get_input_source_message(monitor_id)
        response = self.send_message(message, "Get input source", expect_data=True)
        
        if response and response.is_data_response and len(response. data_payload) >= 1:
            # Response: DATA[0]=0xAD (already in response. command), DATA[1]=input_source, DATA[2]=playlist, etc.
            input_code = response.data_payload[0]
            playlist = response.data_payload[1] if len(response.data_payload) > 1 else 0
            
            input_name = INPUT_SOURCE_NAMES.get(input_code, f"unknown (0x{input_code:02x})")
            
            playlist_info = ""
            if playlist == 0x08:
                playlist_info = " (USB autoplay)"
            elif playlist > 0:
                playlist_info = f" (playlist/URL {playlist})"
            
            print(f"  Current input: {input_name. upper()}{playlist_info}")
            return input_name
        
        return None

