#!/usr/bin/env python3

import socket
import string
import sys

# Hardcoded display configuration
DISPLAYS = {
    0: ("192.168.45.210", 1),  # Monitor ID 1
    1: ("192.168.45.211", 1),  # Monitor ID 1
}

PORT = 5000
TIMEOUT = 2

# SICP message structure:      [size][monitor_id][group_id][command][param][checksum]
# size = total message length (including size and checksum bytes)
# monitor_id = 0-255 (0 for broadcast, 1-255 for specific display)
# group_id = 0-255 (0 for broadcast, 1-254 for groups, 255 for "off")
# command = SICP command byte
# param(s) = command-specific parameters
# checksum = XOR of all previous bytes

# SICP Commands
CMD_COMMUNICATION_CONTROL = 0x00
CMD_POWER_STATE_SET = 0x18
CMD_POWER_STATE_GET = 0x19
CMD_BACKLIGHT_GET = 0x71
CMD_BACKLIGHT_SET = 0x72
CMD_INPUT_SOURCE_SET = 0xAC
CMD_CURRENT_SOURCE_GET = 0xAD
CMD_ANDROID_4K_GET = 0xC6
CMD_ANDROID_4K_SET = 0xC7
CMD_WOL_GET = 0x9C
CMD_WOL_SET = 0x9D
CMD_IP_PARAMETER_GET = 0x82
CMD_COLD_START_SET = 0xA3
CMD_COLD_START_GET = 0xA4
CMD_TEMPERATURE_GET = 0x2F
CMD_SICP_INFO_GET = 0xA2
CMD_MODEL_INFO_GET = 0xA1
CMD_SERIAL_GET = 0x15
CMD_VIDEO_SIGNAL_GET = 0x59
CMD_AV_MUTE_GET = 0x7A
CMD_AV_MUTE_SET = 0x7B
CMD_PICTURE_STYLE_GET = 0x65
CMD_PICTURE_STYLE_SET = 0x66
CMD_VOLUME_SET = 0x44
CMD_VOLUME_GET = 0x45
CMD_MUTE_GET = 0x46
CMD_MUTE_SET = 0x47

# Communication Control Response Codes
RESPONSE_ACK = 0x06   # Command well executed
RESPONSE_NAV = 0x18   # Command not supported/available
RESPONSE_NACK = 0x15  # Checksum/Format error

# Power State Parameters
POWER_OFF = 0x01
POWER_ON = 0x02

# Cold-start Power States
COLD_START_POWER_OFF = 0x00
COLD_START_FORCED_ON = 0x01
COLD_START_LAST_STATUS = 0x02

COLD_START_STATE_NAMES = {
    COLD_START_POWER_OFF: "power-off",
    COLD_START_FORCED_ON: "forced-on",
    COLD_START_LAST_STATUS: "last-status",
}


SICP_INFO_LABELS = {
    0x00: "sicp-version",
    0x01: "platform-label",
    0x02: "platform-version",
    0x03: "custom-intent-version",
}

MODEL_INFO_LABELS = {
    0x00: "model-number",
    0x01: "firmware-version",
    0x02: "build-date",
    0x03: "android-firmware",
    0x04: "hdmi-switch-version",
    0x05: "lan-firmware",
    0x06: "hdmi-switch2-version",
}

# Backlight State Parameters
BACKLIGHT_ON = 0x00
BACKLIGHT_OFF = 0x01

# Android 4K Parameters
ANDROID_4K_DISABLED = 0x00
ANDROID_4K_ENABLED = 0x01

# Wake on LAN Parameters
WOL_DISABLED = 0x00
WOL_ENABLED = 0x01

# IP Parameter identifiers
IP_PARAMETER_CODES = {
    'ip': 0x01,
    'subnet': 0x02,
    'gateway': 0x03,
    'dns1': 0x04,
    'dns2': 0x05,
    'eth-mac': 0x06,
    'wifi-mac': 0x07,
}

IP_PARAMETER_NAMES = {value: key for key, value in IP_PARAMETER_CODES.items()}

IP_PARAMETER_VALUE_TYPES = {
    'current': 0x01,
    'queued': 0x02,
}

IP_PARAMETER_VALUE_TYPE_NAMES = {value: key for key, value in IP_PARAMETER_VALUE_TYPES.items()}

# Group ID
GROUP_ID = 0x00

# Input Source Values (from SICP 5.1 specification)
INPUT_SOURCES = {
    'none': 0x00,
    'video': 0x01,
    'svideo': 0x02,
    's-video': 0x02,
    'component': 0x03,
    'cvi2': 0x04,
    'vga': 0x05,
    'hdmi2': 0x06,
    'displayport2': 0x07,
    'usb2': 0x08,
    'carddvi-d': 0x09,
    'displayport1': 0x0A,
    'cardops': 0x0B,
    'usb1': 0x0C,
    'hdmi':  0x0D,
    'hdmi1': 0x0D,
    'dvi-d': 0x0E,
    'hdmi3': 0x0F,
    'browser': 0x10,
    'smartcms': 0x11,
    'dms': 0x12,
    'digitalmediaserver': 0x12,
    'internalstorage': 0x13,
    'mediaplayer': 0x16,
    'pdfplayer': 0x17,
    'custom': 0x18,
    'customapp': 0x18,
    'hdmi4': 0x19,
    'vga2': 0x1A,
    'vga3': 0x1B,
    'iwb': 0x1C,
    'cmndplay': 0x1D,
    'cmndplayweb': 0x1D,
    'home': 0x1E,
    'launcher': 0x1E,
    'usbtypec': 0x1F,
    'usbc': 0x1F,
    'kiosk': 0x20,
    'smartinfo': 0x21,
    'tuner': 0x22,
    'googlecast': 0x23,
    'interact': 0x24,
    'usbtypec2': 0x25,
    'usbc2': 0x25,
    'screenshare': 0x26,
}

# Reverse lookup for display
INPUT_SOURCE_NAMES = {
    0x00: 'none',
    0x01: 'video',
    0x02: 's-video',
    0x03: 'component',
    0x04: 'cvi2',
    0x05: 'vga',
    0x06: 'hdmi2',
    0x07: 'displayport2',
    0x08: 'usb2',
    0x09: 'carddvi-d',
    0x0A: 'displayport1',
    0x0B: 'cardops',
    0x0C: 'usb1',
    0x0D: 'hdmi1',
    0x0E:  'dvi-d',
    0x0F: 'hdmi3',
    0x10: 'browser',
    0x11: 'smartcms',
    0x12: 'dms',
    0x13: 'internalstorage',
    0x16: 'mediaplayer',
    0x17: 'pdfplayer',
    0x18: 'customapp',
    0x19: 'hdmi4',
    0x1A: 'vga2',
    0x1B: 'vga3',
    0x1C: 'iwb',
    0x1D: 'cmndplayweb',
    0x1E: 'home/launcher',
    0x1F: 'usb-typec',
    0x20: 'kiosk',
    0x21: 'smartinfo',
    0x22: 'tuner',
    0x23: 'googlecast',
    0x24: 'interact',
    0x25: 'usb-typec2',
    0x26: 'screenshare',
}

PICTURE_STYLES = {
    'highbright': 0x00,
    'srgb': 0x01,
    'vivid': 0x02,
    'natural': 0x03,
    'standard': 0x04,
    'video': 0x05,
    'static-signage': 0x06,
    'text': 0x07,
    'energy-saving': 0x08,
    'soft': 0x09,
    'user': 0x0A,
}

PICTURE_STYLE_NAMES = {value: key for key, value in PICTURE_STYLES.items()}


class SicpResponse:
    """Parse and represent a SICP response."""
    
    def __init__(self, data):
        self.raw_data = data
        self. valid = False
        self.is_ack = False
        self.is_nav = False
        self.is_nack = False
        self.is_data_response = False
        self.command = None
        self.data_payload = []
        self.error_message = None
        
        if not data or len(data) < 5:
            self.error_message = "Response too short"
            return
        
        self.size = data[0]
        self.monitor_id = data[1]
        
        # Check if this is a Communication Control response (ACK/NAV/NACK)
        if len(data) >= 6 and data[3] == CMD_COMMUNICATION_CONTROL: 
            self.command = CMD_COMMUNICATION_CONTROL
            response_code = data[4]
            
            if response_code == RESPONSE_ACK:
                self. is_ack = True
                self.valid = True
            elif response_code == RESPONSE_NAV:
                self.is_nav = True
                self. valid = True
                self.error_message = "Command not supported/available (NAV)"
            elif response_code == RESPONSE_NACK:
                self.is_nack = True
                self.valid = True
                self.error_message = "Checksum or format error (NACK)"
            else:
                self.error_message = f"Unknown response code: 0x{response_code:02x}"
        
        # Otherwise it's a data response (e.g., from a GET command)
        elif len(data) >= 5:
            self.is_data_response = True
            self.valid = True
            self.command = data[3]
            # Data payload starts at byte 4 and goes until checksum (last byte)
            self.data_payload = list(data[4:-1])
    
    def __str__(self):
        hex_data = ' '.join(f'{b:02x}' for b in self.raw_data)
        if self.is_ack:
            return f"ACK - {hex_data}"
        elif self.is_nav:
            return f"NAV (Not Available) - {hex_data}"
        elif self.is_nack:
            return f"NACK (Error) - {hex_data}"
        elif self.is_data_response:
            return f"DATA (cmd=0x{self.command:02x}) - {hex_data}"
        else:
            return f"UNKNOWN - {hex_data}"


def calculate_checksum(*bytes_list):
    """Calculate XOR checksum of all bytes."""
    checksum = 0
    for byte in bytes_list:
        checksum ^= byte
    return checksum


def build_power_message(monitor_id, power_on):
    """Build SICP message for screen power control (set)."""
    msg_size = 0x06
    param = POWER_ON if power_on else POWER_OFF
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_POWER_STATE_SET, param)
    
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_POWER_STATE_SET, param, checksum])


def build_power_get_message(monitor_id):
    """Build SICP message to query current power state."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_POWER_STATE_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_POWER_STATE_GET, checksum])


def build_cold_start_get_message(monitor_id):
    """Build SICP message to query cold-start power state."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_COLD_START_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_COLD_START_GET, checksum])


def build_cold_start_set_message(monitor_id, cold_state):
    """Build SICP message to set cold-start power behavior."""
    msg_size = 0x06
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_COLD_START_SET, cold_state)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_COLD_START_SET, cold_state, checksum])


def build_temperature_get_message(monitor_id):
    """Build SICP message to query onboard temperature sensors."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_TEMPERATURE_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_TEMPERATURE_GET, checksum])


def build_sicp_info_get_message(monitor_id, label_code):
    """Build SICP message to get version/platform information."""
    msg_size = 0x06
    checksum = calculate_checksum(
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_SICP_INFO_GET,
        label_code,
    )
    return bytes([
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_SICP_INFO_GET,
        label_code,
        checksum,
    ])


def build_serial_get_message(monitor_id):
    """Build SICP message to request serial number."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_SERIAL_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_SERIAL_GET, checksum])


def build_video_signal_get_message(monitor_id):
    """Build SICP message to query video signal presence."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_VIDEO_SIGNAL_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_VIDEO_SIGNAL_GET, checksum])


def build_av_mute_get_message(monitor_id):
    """Build SICP message to query A/V mute state."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_AV_MUTE_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_AV_MUTE_GET, checksum])


def build_av_mute_set_message(monitor_id, mute_on):
    """Build SICP message to set A/V mute state."""
    msg_size = 0x06
    param = 0x01 if mute_on else 0x00
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_AV_MUTE_SET, param)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_AV_MUTE_SET, param, checksum])


def build_picture_style_get_message(monitor_id):
    """Build SICP message to query current picture style."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_PICTURE_STYLE_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_PICTURE_STYLE_GET, checksum])


def build_picture_style_set_message(monitor_id, style_code):
    """Build SICP message to set picture style."""
    msg_size = 0x06
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_PICTURE_STYLE_SET, style_code)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_PICTURE_STYLE_SET, style_code, checksum])


def build_model_info_get_message(monitor_id, label_code):
    """Build SICP message to get model/firmware/build details."""
    msg_size = 0x06
    checksum = calculate_checksum(
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_MODEL_INFO_GET,
        label_code,
    )
    return bytes([
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_MODEL_INFO_GET,
        label_code,
        checksum,
    ])


def build_backlight_set_message(monitor_id, backlight_on):
    """
    Build SICP message for backlight control.
    
    From SICP 4.5.3 Message-Set:
    Command: 0x72
    Parameters: 
    - 0x00 = Backlight On
    - 0x01 = Backlight Off
    """
    msg_size = 0x06
    param = BACKLIGHT_ON if backlight_on else BACKLIGHT_OFF
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_BACKLIGHT_SET, param)
    
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_BACKLIGHT_SET, param, checksum])


def build_backlight_get_message(monitor_id):
    """
    Build SICP message to get current backlight state.
    
    From SICP 4.5.1 Message-Get:
    Command: 0x71
    """
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_BACKLIGHT_GET)
    
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_BACKLIGHT_GET, checksum])


def build_volume_get_message(monitor_id):
    """Build SICP message to get speaker/audio-out volume levels."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_VOLUME_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_VOLUME_GET, checksum])


def build_volume_set_message(monitor_id, speaker_level, audio_out_level=None):
    """Build SICP message to set speaker/audio-out volume (0-100, use 0xFF for no change)."""
    if speaker_level is None:
        speaker_level = 0xFF
    if audio_out_level is None:
        audio_out_level = 0xFF

    msg_size = 0x07
    checksum = calculate_checksum(
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_VOLUME_SET,
        speaker_level,
        audio_out_level,
    )
    return bytes([
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_VOLUME_SET,
        speaker_level,
        audio_out_level,
        checksum,
    ])


def build_mute_get_message(monitor_id):
    """Build SICP message to read mute status."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_MUTE_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_MUTE_GET, checksum])


def build_mute_set_message(monitor_id, mute_on):
    """Build SICP message to set mute state (True=on)."""
    msg_size = 0x06
    param = 0x01 if mute_on else 0x00
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_MUTE_SET, param)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_MUTE_SET, param, checksum])


def build_android_4k_set_message(monitor_id, enable_4k):
    """
    Build SICP message for Android 4K control.
    
    From SICP 8.17.3 Message-Set:
    Command:  0xC7
    Parameters:
    - 0x00 = Disable
    - 0x01 = Enable
    
    Available from SICP 2.11+ with displays that support this feature.
    """
    msg_size = 0x06
    param = ANDROID_4K_ENABLED if enable_4k else ANDROID_4K_DISABLED
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_ANDROID_4K_SET, param)
    
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_ANDROID_4K_SET, param, checksum])


def build_android_4k_get_message(monitor_id):
    """
    Build SICP message to get current Android 4K state.
    
    From SICP 8.17.1 Message-Get:
    Command:  0xC6
    
    Available from SICP 2.11+ with displays that support this feature.
    """
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_ANDROID_4K_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_ANDROID_4K_GET, checksum])


def build_wol_get_message(monitor_id):
    """Build SICP message to get Wake on LAN status."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_WOL_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_WOL_GET, checksum])


def build_wol_set_message(monitor_id, enable_wol):
    """Build SICP message to set Wake on LAN status."""
    msg_size = 0x06
    param = WOL_ENABLED if enable_wol else WOL_DISABLED
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_WOL_SET, param)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_WOL_SET, param, checksum])


def build_ip_parameter_get_message(monitor_id, parameter_code, value_type_code):
    """Build SICP message to get IP parameter data."""
    msg_size = 0x07
    checksum = calculate_checksum(
        msg_size, monitor_id, GROUP_ID, CMD_IP_PARAMETER_GET, parameter_code, value_type_code
    )
    return bytes([
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_IP_PARAMETER_GET,
        parameter_code,
        value_type_code,
        checksum,
    ])


def build_input_source_message(monitor_id, input_source_code, playlist=0, osd_style=1, effect_duration=0):
    """
    Build SICP message for input source control.
    
    From SICP 5.1.3 Message-Set:
    Command: 0xAC
    DATA[1] = Input Source Type/Number
    DATA[2] = Start playlist/URL number (0x00-0x08)
              0x00 = no playlist or URL
              0x01-0x07 = playlist file 1-7 or URL 1-7
              0x08 = USB autoplay
    DATA[3] = OSD Style
              0x00 = Source label not displayed
              0x01 = Source label displayed
    DATA[4] = Effect duration (SICP 2.12+)
              0x00 = don't change
              0x05 = 5 secs
              0x0A = 10 secs
              0x0F = 15 secs
              0x14 = 20 secs
    """
    msg_size = 0x09
    
    checksum = calculate_checksum(
        msg_size, monitor_id, GROUP_ID, CMD_INPUT_SOURCE_SET,
        input_source_code, playlist, osd_style, effect_duration
    )
    
    return bytes([
        msg_size, monitor_id, GROUP_ID, CMD_INPUT_SOURCE_SET,
        input_source_code, playlist, osd_style, effect_duration,
        checksum
    ])


def build_get_input_source_message(monitor_id):
    """
    Build SICP message to get current input source. 
    
    From SICP 5.1.1 Message-Get:
    Command: 0xAD
    """
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_CURRENT_SOURCE_GET)
    
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_CURRENT_SOURCE_GET, checksum])


def send_message(monitor_id, ip, message, action_description, expect_data=False):
    """
    Send SICP message to display and return parsed response.
    
    Args:
        monitor_id: Monitor ID
        ip: IP address
        message: Message bytes to send
        action_description: Description for logging
        expect_data: True if expecting data response (GET command), False for ACK (SET command)
    
    Returns:
        SicpResponse object or None on error
    """
    try: 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT)
            sock.connect((ip, PORT))
            sock.sendall(message)
            
            # Receive response
            response_data = sock.recv(1024)
            
        # Parse response
        response = SicpResponse(response_data)
        
        # Log the action and response
        if response.is_ack:
            print(f"✓ {action_description} - {ip} (Monitor {monitor_id})")
            # print(f"  Response: {response}")
        elif response.is_nav:
            print(f"⚠ {action_description} - {ip} (Monitor {monitor_id})")
            # print(f"  Response: {response}")
            print("  Error: Command not supported by this display")
            return None
        elif response.is_nack:
            print(f"✗ {action_description} - {ip} (Monitor {monitor_id})")
            print(f"  Response: {response}")
            print("  Error: Checksum or format error")
            return None
        elif response.is_data_response:
            print(f"✓ {action_description} - {ip} (Monitor {monitor_id})")
            # print(f"  Response: {response}")
        else:
            print(f"⚠ {action_description} - {ip} (Monitor {monitor_id})")
            print(f"  Response: {response}")
            if response.error_message:
                print(f"  Error: {response.error_message}")
        
        return response
        
    except socket.timeout:
        print(f"✗ Connection timeout to {ip} (Monitor ID: {monitor_id})")
        print(f"  No response within {TIMEOUT} seconds")
        return None
    except socket.error as e:
        print(f"✗ Socket error for {ip} (Monitor ID: {monitor_id}): {e}")
        return None
    except Exception as e:
        print(f"✗ Error for {ip} (Monitor ID: {monitor_id}): {e}")
        return None


def power_control(monitor_id, ip, power_on):
    """Control display power state."""
    message = build_power_message(monitor_id, power_on)
    action = "Screen ON" if power_on else "Screen OFF"
    response = send_message(monitor_id, ip, message, action)
    return response and response.is_ack


def get_power_state(monitor_id, ip):
    """Query current power state (returns 0x01 off, 0x02 on)."""
    message = build_power_get_message(monitor_id)
    response = send_message(monitor_id, ip, message, "Get power state", expect_data=True)

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


def get_cold_start_power_state(monitor_id, ip):
    """Query cold-start power behavior (0x00 off, 0x01 forced on, 0x02 last status)."""
    message = build_cold_start_get_message(monitor_id)
    response = send_message(monitor_id, ip, message, "Get cold-start power state", expect_data=True)

    if response and response.is_data_response and response.data_payload:
        state_code = response.data_payload[0]
        label = COLD_START_STATE_NAMES.get(state_code, f"0x{state_code:02X}")
        print(f"  Cold-start power state: {label}")
        return state_code

    return None


def set_cold_start_power_state(monitor_id, ip, state_code):
    """Set cold-start power behavior."""
    message = build_cold_start_set_message(monitor_id, state_code)
    label = COLD_START_STATE_NAMES.get(state_code, f"0x{state_code:02X}")
    action = f"Set cold-start power state to {label}"
    response = send_message(monitor_id, ip, message, action)
    return response and response.is_ack


def get_temperature(monitor_id, ip):
    """Read temperature sensors (returns list of Celsius values)."""
    message = build_temperature_get_message(monitor_id)
    response = send_message(monitor_id, ip, message, "Get temperature", expect_data=True)

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


def get_sicp_info(monitor_id, ip, label_code):
    """Retrieve SICP version/platform info text for the requested label code."""
    message = build_sicp_info_get_message(monitor_id, label_code)
    label = SICP_INFO_LABELS.get(label_code, f"0x{label_code:02X}")
    response = send_message(
        monitor_id,
        ip,
        message,
        f"Get SICP info ({label})",
        expect_data=True,
    )

    if response and response.is_data_response and response.data_payload:
        payload = response.data_payload
        if payload[0] == CMD_SICP_INFO_GET and len(payload) > 1:
            payload = payload[1:]

        info_text = ''.join(chr(b) for b in payload if 32 <= b <= 126)
        print(f"  {label}: {info_text or '(no data)'}")
        return info_text

    return None


def get_model_info(monitor_id, ip, label_code):
    """Retrieve model/firmware/build information for the given label code."""
    message = build_model_info_get_message(monitor_id, label_code)
    label = MODEL_INFO_LABELS.get(label_code, f"0x{label_code:02X}")
    response = send_message(
        monitor_id,
        ip,
        message,
        f"Get model info ({label})",
        expect_data=True,
    )

    if response and response.is_data_response and response.data_payload:
        payload = response.data_payload
        if payload[0] == CMD_MODEL_INFO_GET and len(payload) > 1:
            payload = payload[1:]

        text = ''.join(chr(b) for b in payload if 32 <= b <= 126)
        print(f"  {label}: {text or '(no data)'}")
        return text

    return None


def get_serial_number(monitor_id, ip):
    """Fetch the 14-character display serial number."""
    message = build_serial_get_message(monitor_id)
    response = send_message(monitor_id, ip, message, "Get serial number", expect_data=True)

    if response and response.is_data_response and response.data_payload:
        payload = response.data_payload
        if payload[0] == CMD_SERIAL_GET and len(payload) > 1:
            payload = payload[1:]

        serial_chars = [chr(b) for b in payload if 32 <= b <= 126]
        serial = ''.join(serial_chars)
        print(f"  Serial number: {serial or '(no data)'}")
        return serial

    return None


def get_video_signal_status(monitor_id, ip):
    """Determine if a video signal is present on the active input."""
    message = build_video_signal_get_message(monitor_id)
    response = send_message(monitor_id, ip, message, "Get video signal status", expect_data=True)

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


def get_picture_style(monitor_id, ip):
    """Retrieve the current picture style value."""
    message = build_picture_style_get_message(monitor_id)
    response = send_message(monitor_id, ip, message, "Get picture style", expect_data=True)

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


def set_picture_style(monitor_id, ip, style_code):
    """Set the picture style to the provided code."""
    message = build_picture_style_set_message(monitor_id, style_code)
    style_name = PICTURE_STYLE_NAMES.get(style_code, f"0x{style_code:02X}")
    response = send_message(monitor_id, ip, message, f"Set picture style to {style_name}")
    return response and response.is_ack


def backlight_control(monitor_id, ip, backlight_on):
    """Control display backlight state."""
    message = build_backlight_set_message(monitor_id, backlight_on)
    action = "Backlight ON" if backlight_on else "Backlight OFF"
    response = send_message(monitor_id, ip, message, action)
    return response and response.is_ack


def get_backlight_state(monitor_id, ip):
    """Get current display backlight state."""
    message = build_backlight_get_message(monitor_id)
    response = send_message(monitor_id, ip, message, "Get backlight state", expect_data=True)
    
    if response and response.is_data_response and len(response.data_payload) >= 1:
        # Response:  DATA[0]=0x71, DATA[1]=state (0x00=On, 0x01=Off)
        state_byte = response.data_payload[0]
        state = "ON" if state_byte == BACKLIGHT_ON else "OFF"
        print(f"  Current backlight:  {state}")
        return state
    
    return None


def android_4k_control(monitor_id, ip, enable_4k):
    """
    Control Android 4K mode.
    
    Available from SICP 2.11+ with displays that support this feature.
    """
    message = build_android_4k_set_message(monitor_id, enable_4k)
    action = "Android 4K ENABLED" if enable_4k else "Android 4K DISABLED"
    response = send_message(monitor_id, ip, message, action)
    return response and response.is_ack


def get_android_4k_state(monitor_id, ip):
    """
    Get current Android 4K state.
    
    Available from SICP 2.11+ with displays that support this feature. 
    """
    message = build_android_4k_get_message(monitor_id)
    response = send_message(monitor_id, ip, message, "Get Android 4K state", expect_data=True)
    
    if response and response.is_data_response and len(response.data_payload) >= 1:
        # Response: DATA[0]=0xC6, DATA[1]=state (0x00=Disabled, 0x01=Enabled)
        state_byte = response.data_payload[0]
        state = "ENABLED" if state_byte == ANDROID_4K_ENABLED else "DISABLED"
        print(f"  Android 4K: {state}")
        return state
    
    return None


def wol_control(monitor_id, ip, enable_wol):
    """Control Wake on LAN state."""
    message = build_wol_set_message(monitor_id, enable_wol)
    action = "Wake on LAN ON" if enable_wol else "Wake on LAN OFF"
    response = send_message(monitor_id, ip, message, action)
    return response and response.is_ack


def get_wol_state(monitor_id, ip):
    """Get current Wake on LAN state."""
    message = build_wol_get_message(monitor_id)
    response = send_message(monitor_id, ip, message, "Get Wake on LAN state", expect_data=True)

    if response and response.is_data_response and len(response.data_payload) >= 1:
        # Some firmware echoes the command (0x9C) as the first payload byte.
        if response.data_payload[0] == CMD_WOL_GET and len(response.data_payload) >= 2:
            state_byte = response.data_payload[1]
        else:
            state_byte = response.data_payload[0]

        state = "ON" if state_byte == WOL_ENABLED else "OFF"
        print(f"  Wake on LAN: {state}")
        return state

    return None


def set_volume(monitor_id, ip, speaker_level=None, audio_out_level=None):
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
    response = send_message(monitor_id, ip, message, action)
    return response and response.is_ack


def get_volume(monitor_id, ip):
    """Get current speaker/audio-out volume levels."""
    message = build_volume_get_message(monitor_id)
    response = send_message(monitor_id, ip, message, "Get volume", expect_data=True)

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


def set_mute(monitor_id, ip, mute_on):
    """Set mute state for both speaker and audio-out."""
    message = build_mute_set_message(monitor_id, mute_on)
    action = "Mute ON" if mute_on else "Mute OFF"
    response = send_message(monitor_id, ip, message, action)
    return response and response.is_ack


def get_mute_status(monitor_id, ip):
    """Get mute status."""
    message = build_mute_get_message(monitor_id)
    response = send_message(monitor_id, ip, message, "Get mute status", expect_data=True)

    if response and response.is_data_response and response.data_payload:
        mute_on = response.data_payload[0] == 0x01
        print(f"  Mute: {'ON' if mute_on else 'OFF'}")
        return mute_on

    return None


def set_av_mute(monitor_id, ip, mute_on):
    """Enable or disable A/V mute (backlight, audio, touch)."""
    message = build_av_mute_set_message(monitor_id, mute_on)
    action = "A/V Mute ON" if mute_on else "A/V Mute OFF"
    response = send_message(monitor_id, ip, message, action)
    return response and response.is_ack


def get_av_mute_status(monitor_id, ip):
    """Retrieve current A/V mute state."""
    message = build_av_mute_get_message(monitor_id)
    response = send_message(monitor_id, ip, message, "Get A/V mute", expect_data=True)

    if response and response.is_data_response and response.data_payload:
        payload = response.data_payload
        if payload[0] == CMD_AV_MUTE_GET and len(payload) > 1:
            payload = payload[1:]

        if payload:
            av_mute_on = payload[0] == 0x01
            print(f"  A/V Mute: {'ON' if av_mute_on else 'OFF'}")
            return av_mute_on

    return None


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


def get_ip_parameter(monitor_id, ip, parameter_name, value_type_name='current'):
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
    response = send_message(monitor_id, ip, message, action, expect_data=True)

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


def set_input_source(monitor_id, ip, input_source_name, playlist=0):
    """Set display input source."""
    if input_source_name not in INPUT_SOURCES:
        print(f"✗ Unknown input source: {input_source_name}")
        print(f"Available sources: {', '.join(sorted(set(INPUT_SOURCES.keys())))}")
        return False
    
    input_code = INPUT_SOURCES[input_source_name]
    message = build_input_source_message(monitor_id, input_code, playlist=playlist)
    
    playlist_info = f" (playlist {playlist})" if playlist > 0 else ""
    action = f"Set input to {input_source_name. upper()}{playlist_info}"
    response = send_message(monitor_id, ip, message, action)
    return response and response.is_ack


def get_input_source(monitor_id, ip):
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
    response = send_message(monitor_id, ip, message, "Get input source", expect_data=True)
    
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


def print_usage():
    """Print usage information."""
    print(f"Usage: {sys.argv[0]} <monitor_id|all> <command> [args]")
    print("\nAvailable monitors:")
    for key, (ip, mon_id) in DISPLAYS.items():
        print(f"  {key}: Monitor ID {mon_id}: {ip}")
    print("\nCommands:")
    print("  on                        Turn screen on")
    print("  off                       Turn screen off")
    print("  set-power <on|off>        Explicit power set command")
    print("  get-power                 Get current power state")
    print("  get-cold-start            Get cold-start power behavior")
    print("  set-cold-start <mode>     Set cold-start power (off|forced|last)")
    print("  get-temperature           Read temperature sensors")
    print("  get-sicp-info <label>     Get SICP info (version/platform)")
    print("  get-model-info <label>    Get model/firmware/build info")
    print("  get-serial                Get display serial number")
    print("  get-video-signal          Check if active input has signal")
    print("  get-picture-style         Get current picture style")
    print("  set-picture-style <name>  Set picture style (highbright, srgb, ...)")
    print("  backlight-on              Turn backlight on")
    print("  backlight-off             Turn backlight off")
    print("  get-backlight             Get current backlight state")
    print("  4k-on                     Enable Android 4K mode (SICP 2.11+)")
    print("  4k-off                    Disable Android 4K mode (SICP 2.11+)")
    print("  get-4k                    Get current Android 4K state")
    print("  wol-on                    Enable Wake on LAN (SICP 2.07+)")
    print("  wol-off                   Disable Wake on LAN (SICP 2.07+)")
    print("  get-wol                   Get current Wake on LAN state")
    print("  get-volume                Get speaker/audio-out volume levels")
    print("  set-volume <spk> [out]    Set speaker/audio-out volume (0-100 or nc)")
    print("  get-mute                  Get mute status")
    print("  mute-on|mute-off          Enable or disable mute")
    print("  get-av-mute               Get A/V mute status")
    print("  av-mute-on|av-mute-off    Enable or disable A/V mute")
    print("  get-ip <param> [type]     Get IP/MAC info (type=current|queued)")
    print("  input <source> [playlist] Set input source (optional playlist 1-7)")
    print("  get-input                 Get current input source")
    print("\nPopular input sources:")
    print("  browser, mediaplayer, pdfplayer, customapp")
    print("  hdmi1, hdmi2, hdmi3, hdmi4")
    print("  displayport1, displayport2")
    print("  vga, dvi-d, usb1, usb2, usbtypec")
    print("  home, kiosk, screenshare, googlecast")
    print("\nExamples:")
    print(f"  {sys.argv[0]} 0 off                      # Turn off monitor 0")
    print(f"  {sys.argv[0]} all get-input                   # Check Android 4K status")
    print(f"  {sys.argv[0]} 0 input mediaplayer 1      # Set to media player, playlist 2")

def main():
    """Main entry point."""
    if len(sys. argv) < 3:
        print_usage()
        sys.exit(1)
    
    monitor_arg = sys.argv[1]
    command = sys.argv[2]. lower()
    
    # Parse monitor ID(s)
    if monitor_arg.lower() == "all":
        monitor_ids = list(DISPLAYS.values())
    else:
        try:
            monitor_key = int(monitor_arg)
            if monitor_key not in DISPLAYS:
                print(f"Error: Unknown monitor ID {monitor_key}")
                print(f"Available monitors: {', '. join(map(str, DISPLAYS.keys()))}")
                sys.exit(1)
            monitor_ids = [DISPLAYS[monitor_key]]
        except ValueError:
            print("Error: Monitor ID must be a number or 'all'")
            sys.exit(1)
    
    # Execute command
    success_count = 0
    
    if command == "on": 
        for (mon_ip, mon_id) in monitor_ids: 
            if power_control(mon_id, mon_ip, True):
                success_count += 1
    
    elif command == "off": 
        for (mon_ip, mon_id) in monitor_ids:
            if power_control(mon_id, mon_ip, False):
                success_count += 1

    elif command == "set-power":
        if len(sys.argv) < 4:
            print("Error: set-power requires 'on' or 'off'")
            sys.exit(1)

        target = sys.argv[3].lower()
        if target in {"on", "0x02", "2"}:
            desired_on = True
        elif target in {"off", "0", "0x01", "1"}:
            desired_on = False
        else:
            print("Error: set-power argument must be 'on' or 'off'")
            sys.exit(1)

        for (mon_ip, mon_id) in monitor_ids:
            if power_control(mon_id, mon_ip, desired_on):
                success_count += 1
    
    elif command == "backlight-on":
        for (mon_ip, mon_id) in monitor_ids:
            if backlight_control(mon_id, mon_ip, True):
                success_count += 1
    
    elif command == "backlight-off": 
        for (mon_ip, mon_id) in monitor_ids:
            if backlight_control(mon_id, mon_ip, False):
                success_count += 1
    
    elif command == "get-backlight":
        for (mon_ip, mon_id) in monitor_ids: 
            if get_backlight_state(mon_id, mon_ip):
                success_count += 1
    
    elif command == "4k-on": 
        for (mon_ip, mon_id) in monitor_ids:
            if android_4k_control(mon_id, mon_ip, True):
                success_count += 1
    
    elif command == "4k-off":
        for (mon_ip, mon_id) in monitor_ids:
            if android_4k_control(mon_id, mon_ip, False):
                success_count += 1
    
    elif command == "get-4k":
        for (mon_ip, mon_id) in monitor_ids: 
            if get_android_4k_state(mon_id, mon_ip):
                success_count += 1

    elif command == "get-power":
        for (mon_ip, mon_id) in monitor_ids:
            if get_power_state(mon_id, mon_ip) is not None:
                success_count += 1

    elif command == "get-cold-start":
        for (mon_ip, mon_id) in monitor_ids:
            if get_cold_start_power_state(mon_id, mon_ip) is not None:
                success_count += 1

    elif command == "set-cold-start":
        if len(sys.argv) < 4:
            print("Error: set-cold-start requires a mode (off|forced|last)")
            sys.exit(1)

        mode = sys.argv[3].lower()
        if mode in {"off", "power-off", "0", "0x00"}:
            cold_state = COLD_START_POWER_OFF
        elif mode in {"forced", "forced-on", "on", "1", "0x01"}:
            cold_state = COLD_START_FORCED_ON
        elif mode in {"last", "last-status", "2", "0x02"}:
            cold_state = COLD_START_LAST_STATUS
        else:
            print("Error: set-cold-start mode must be off|forced|last")
            sys.exit(1)

        for (mon_ip, mon_id) in monitor_ids:
            if set_cold_start_power_state(mon_id, mon_ip, cold_state):
                success_count += 1

    elif command == "get-temperature":
        for (mon_ip, mon_id) in monitor_ids:
            if get_temperature(mon_id, mon_ip) is not None:
                success_count += 1

    elif command == "get-sicp-info":
        if len(sys.argv) < 4:
            print("Error: get-sicp-info requires a label (sicp-version|platform-label|platform-version|custom-intent)")
            sys.exit(1)

        label_arg = sys.argv[3].lower()
        label_map = {
            "sicp-version": 0x00,
            "version": 0x00,
            "platform-label": 0x01,
            "label": 0x01,
            "platform-version": 0x02,
            "custom-intent": 0x03,
            "custom-intent-version": 0x03,
        }

        if label_arg not in label_map:
            print("Error: Unknown label. Use sicp-version, platform-label, platform-version, custom-intent")
            sys.exit(1)

        label_code = label_map[label_arg]

        for (mon_ip, mon_id) in monitor_ids:
            if get_sicp_info(mon_id, mon_ip, label_code) is not None:
                success_count += 1

    elif command == "get-model-info":
        if len(sys.argv) < 4:
            print("Error: get-model-info requires a label (model|firmware|build|android|hdmi|lan)")
            sys.exit(1)

        label_arg = sys.argv[3].lower()
        model_map = {
            "model": 0x00,
            "model-number": 0x00,
            "fw": 0x01,
            "firmware": 0x01,
            "firmware-version": 0x01,
            "build": 0x02,
            "build-date": 0x02,
            "android": 0x03,
            "android-fw": 0x03,
            "hdmi": 0x04,
            "hdmi-switch": 0x04,
            "lan": 0x05,
            "lan-fw": 0x05,
            "hdmi2": 0x06,
            "hdmi-switch2": 0x06,
        }

        if label_arg not in model_map:
            print("Error: Unknown label. Use model, firmware, build, android, hdmi, lan, hdmi2")
            sys.exit(1)

        label_code = model_map[label_arg]

        for (mon_ip, mon_id) in monitor_ids:
            if get_model_info(mon_id, mon_ip, label_code) is not None:
                success_count += 1

    elif command == "get-serial":
        for (mon_ip, mon_id) in monitor_ids:
            if get_serial_number(mon_id, mon_ip) is not None:
                success_count += 1

    elif command == "get-video-signal":
        for (mon_ip, mon_id) in monitor_ids:
            if get_video_signal_status(mon_id, mon_ip) is not None:
                success_count += 1

    elif command == "get-picture-style":
        for (mon_ip, mon_id) in monitor_ids:
            if get_picture_style(mon_id, mon_ip) is not None:
                success_count += 1

    elif command == "set-picture-style":
        if len(sys.argv) < 4:
            print("Error: set-picture-style requires a style name or numeric code")
            print(f"Available styles: {', '.join(sorted(PICTURE_STYLES.keys()))}")
            sys.exit(1)

        style_arg_raw = sys.argv[3]
        normalized = style_arg_raw.lower().replace('_', '-').strip()
        style_code = None

        if normalized in PICTURE_STYLES:
            style_code = PICTURE_STYLES[normalized]
        else:
            try:
                parsed = int(style_arg_raw, 0)
            except ValueError:
                parsed = None

            if parsed is None or not (0 <= parsed <= 0xFF):
                print("Error: Unknown picture style. Use a known name or 0-255 code.")
                print(f"Available styles: {', '.join(sorted(PICTURE_STYLES.keys()))}")
                sys.exit(1)

            style_code = parsed

        for (mon_ip, mon_id) in monitor_ids:
            if set_picture_style(mon_id, mon_ip, style_code):
                success_count += 1

    elif command == "get-volume":
        for (mon_ip, mon_id) in monitor_ids:
            if get_volume(mon_id, mon_ip) is not None:
                success_count += 1

    elif command == "set-volume":
        if len(sys.argv) < 4:
            print("Error: set-volume requires at least a speaker value (0-100 or nc)")
            sys.exit(1)

        def _parse_volume_arg(arg):
            if arg is None:
                return None
            if arg.lower() in {"nc", "none"}:
                return None
            try:
                return int(arg)
            except ValueError:
                print("Error: Volume values must be integers 0-100 or 'nc'")
                sys.exit(1)

        speaker_value = _parse_volume_arg(sys.argv[3])
        audio_value = _parse_volume_arg(sys.argv[4]) if len(sys.argv) >= 5 else None

        for (mon_ip, mon_id) in monitor_ids:
            try:
                if set_volume(mon_id, mon_ip, speaker_value, audio_value):
                    success_count += 1
            except ValueError as exc:
                print(f"Error: {exc}")
                sys.exit(1)

    elif command == "get-mute":
        for (mon_ip, mon_id) in monitor_ids:
            if get_mute_status(mon_id, mon_ip) is not None:
                success_count += 1

    elif command == "mute-on":
        for (mon_ip, mon_id) in monitor_ids:
            if set_mute(mon_id, mon_ip, True):
                success_count += 1

    elif command == "mute-off":
        for (mon_ip, mon_id) in monitor_ids:
            if set_mute(mon_id, mon_ip, False):
                success_count += 1

    elif command == "get-av-mute":
        for (mon_ip, mon_id) in monitor_ids:
            if get_av_mute_status(mon_id, mon_ip) is not None:
                success_count += 1

    elif command == "av-mute-on":
        for (mon_ip, mon_id) in monitor_ids:
            if set_av_mute(mon_id, mon_ip, True):
                success_count += 1

    elif command == "av-mute-off":
        for (mon_ip, mon_id) in monitor_ids:
            if set_av_mute(mon_id, mon_ip, False):
                success_count += 1

    elif command == "get-ip":
        if len(sys.argv) < 4:
            print("Error: get-ip requires a parameter name")
            print(f"Available parameters: {', '.join(IP_PARAMETER_CODES.keys())}")
            sys.exit(1)

        parameter_name = sys.argv[3].lower()
        value_type = 'current'

        if len(sys.argv) >= 5:
            value_type = sys.argv[4].lower()

        for (mon_ip, mon_id) in monitor_ids:
            if get_ip_parameter(mon_id, mon_ip, parameter_name, value_type):
                success_count += 1

    elif command == "wol-on":
        for (mon_ip, mon_id) in monitor_ids:
            if wol_control(mon_id, mon_ip, True):
                success_count += 1

    elif command == "wol-off":
        for (mon_ip, mon_id) in monitor_ids:
            if wol_control(mon_id, mon_ip, False):
                success_count += 1

    elif command == "get-wol":
        for (mon_ip, mon_id) in monitor_ids:
            if get_wol_state(mon_id, mon_ip):
                success_count += 1
    
    elif command == "input":
        if len(sys. argv) < 4:
            print("Error: input command requires a source name")
            print("Example sources: browser, mediaplayer, pdfplayer, hdmi1, hdmi2, displayport1")
            sys.exit(1)
        
        input_source_name = sys.argv[3]. lower()
        playlist = 0
        
        # Optional playlist parameter
        if len(sys.argv) >= 5:
            try:
                playlist = int(sys.argv[4])
                if playlist < 0 or playlist > 8:
                    print("Error:  Playlist must be 0-8 (0=none, 1-7=playlist, 8=USB autoplay)")
                    sys.exit(1)
            except ValueError:
                print("Error: Playlist must be a number (0-8)")
                sys. exit(1)
        
        for (mon_ip, mon_id) in monitor_ids: 
            if set_input_source(mon_id, mon_ip, input_source_name, playlist):
                success_count += 1
    
    elif command == "get-input": 
        for (mon_ip, mon_id) in monitor_ids:
            print(f"\nMonitor ID {mon_id} ({mon_ip}):")
            if get_input_source(mon_id, mon_ip):
                success_count += 1
    
    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)
    
    # Print summary for multi-monitor operations
    if len(monitor_ids) > 1:
        print(f"\n{'✓' if success_count == len(monitor_ids) else '⚠'} Command succeeded on {success_count}/{len(monitor_ids)} displays")
    
    sys.exit(0 if success_count == len(monitor_ids) else 1)


if __name__ == "__main__":
    main()