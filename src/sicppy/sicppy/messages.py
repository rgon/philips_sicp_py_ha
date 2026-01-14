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
CMD_MONITOR_ID_SET = 0x69
CMD_VIDEO_PARAMETERS_SET = 0x32
CMD_VIDEO_PARAMETERS_GET = 0x33
CMD_COLOR_TEMPERATURE_SET = 0x34
CMD_COLOR_TEMPERATURE_GET = 0x35
CMD_COLOR_TEMPERATURE_FINE_SET = 0x11
CMD_COLOR_TEMPERATURE_FINE_GET = 0x12
CMD_TEST_PATTERN_GET = 0x6C
CMD_TEST_PATTERN_SET = 0x6D
CMD_REMOTE_LOCK_SET = 0x1C
CMD_REMOTE_LOCK_GET = 0x1D
CMD_REMOTE_CONTROL_SIM = 0xFE
CMD_POWER_ON_LOGO_SET = 0x3E
CMD_POWER_ON_LOGO_GET = 0x3F
CMD_OSD_INFO_SET = 0x2C
CMD_OSD_INFO_GET = 0x2D
CMD_AUTO_SIGNAL_SET = 0xAE
CMD_AUTO_SIGNAL_GET = 0xAF
CMD_GROUP_ID_SET = 0x5C
CMD_GROUP_ID_GET = 0x5D
CMD_POWER_SAVE_SET = 0xD2
CMD_POWER_SAVE_GET = 0xD3
CMD_SMART_POWER_SET = 0xDD
CMD_SMART_POWER_GET = 0xDE
CMD_APM_SET = 0xD0
CMD_APM_GET = 0xD1
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

TEST_PATTERNS = {
    'off': 0x00,
    'white-100': 0x01,
    'white': 0x01,
    'red': 0x02,
    'green': 0x03,
    'blue': 0x04,
    'black': 0x05,
    'half-white-top': 0x06,
    'half-white-bottom': 0x07,
    'ramp': 0x08,
    'white-12': 0x09,
    'white-25': 0x0A,
    'white-65': 0x0B,
}

TEST_PATTERN_NAMES = {
    value: key for key, value in TEST_PATTERNS.items()
    if key in {
        'off',
        'white-100',
        'red',
        'green',
        'blue',
        'black',
        'half-white-top',
        'half-white-bottom',
        'ramp',
        'white-12',
        'white-25',
        'white-65',
    }
}

REMOTE_LOCK_STATES = {
    'unlock-all': 0x01,
    'lock-all': 0x02,
    'lock-all-but-power': 0x03,
    'lock-all-but-volume': 0x04,
    'primary': 0x05,
    'secondary': 0x06,
    'lock-all-except-power-volume': 0x07,
}

REMOTE_LOCK_STATE_NAMES = {
    0x01: 'unlock-all',
    0x02: 'lock-all',
    0x03: 'lock-all-but-power',
    0x04: 'lock-all-but-volume',
    0x05: 'primary',
    0x06: 'secondary',
    0x07: 'lock-all-except-power-volume',
}

REMOTE_KEY_CODES = {
    'key-0': 0x00,
    '0': 0x00,
    'key-1': 0x01,
    '1': 0x01,
    'key-2': 0x02,
    '2': 0x02,
    'key-3': 0x03,
    '3': 0x03,
    'key-4': 0x04,
    '4': 0x04,
    'key-5': 0x05,
    '5': 0x05,
    'key-6': 0x06,
    '6': 0x06,
    'key-7': 0x07,
    '7': 0x07,
    'key-8': 0x08,
    '8': 0x08,
    'key-9': 0x09,
    '9': 0x09,
    'back': 0x0A,
    'mute': 0x0D,
    'info': 0x0F,
    'vol+': 0x10,
    'vol-plus': 0x10,
    'volume-up': 0x10,
    'vol-': 0x11,
    'vol-minus': 0x11,
    'volume-down': 0x11,
    'fwd': 0x28,
    'forward': 0x28,
    'rwd': 0x2B,
    'rewind': 0x2B,
    'play': 0x2C,
    'pause': 0x30,
    'stop': 0x31,
    'sources': 0x38,
    'options': 0x40,
    'home': 0x54,
    'arrow-up': 0x58,
    'up': 0x58,
    'arrow-down': 0x59,
    'down': 0x59,
    'arrow-left': 0x5A,
    'left': 0x5A,
    'arrow-right': 0x5B,
    'right': 0x5B,
    'ok': 0x5C,
    'enter': 0x5C,
    'select': 0x5C,
    'red': 0x6D,
    'green': 0x6E,
    'yellow': 0x6F,
    'blue': 0x70,
    'list': 0x8B,
    'adjust': 0x90,
    'power-on': 0xBE,
    'power-off': 0xBF,
    'format': 0xF5,
}

REMOTE_KEY_NAMES = {
    0x00: 'key-0',
    0x01: 'key-1',
    0x02: 'key-2',
    0x03: 'key-3',
    0x04: 'key-4',
    0x05: 'key-5',
    0x06: 'key-6',
    0x07: 'key-7',
    0x08: 'key-8',
    0x09: 'key-9',
    0x0A: 'back',
    0x0D: 'mute',
    0x0F: 'info',
    0x10: 'vol+',
    0x11: 'vol-',
    0x28: 'fwd',
    0x2B: 'rwd',
    0x2C: 'play',
    0x30: 'pause',
    0x31: 'stop',
    0x38: 'sources',
    0x40: 'options',
    0x54: 'home',
    0x58: 'arrow-up',
    0x59: 'arrow-down',
    0x5A: 'arrow-left',
    0x5B: 'arrow-right',
    0x5C: 'ok',
    0x6D: 'red',
    0x6E: 'green',
    0x6F: 'yellow',
    0x70: 'blue',
    0x8B: 'list',
    0x90: 'adjust',
    0xBE: 'power-on',
    0xBF: 'power-off',
    0xF5: 'format',
}

POWER_ON_LOGO_MODES = {
    'off': 0x00,
    'on': 0x01,
    'user': 0x02,
}

POWER_ON_LOGO_MODE_NAMES = {
    0x00: 'off',
    0x01: 'on',
    0x02: 'user',
}

AUTO_SIGNAL_MODES = {
    'off': 0x00,
    'all': 0x01,
    'reserved': 0x02,
    'pc-only': 0x03,
    'pc-sources': 0x03,
    'video-only': 0x04,
    'video-sources': 0x04,
    'failover': 0x05,
}

AUTO_SIGNAL_MODE_NAMES = {
    0x00: 'off',
    0x01: 'all',
    0x02: 'reserved',
    0x03: 'pc-only',
    0x04: 'video-only',
    0x05: 'failover',
}

COLOR_TEMPERATURE_MODES = {
    'user1': 0x00,
    'user-1': 0x00,
    'native': 0x01,
    '11000k': 0x02,
    '10000k': 0x03,
    '9300k': 0x04,
    '7500k': 0x05,
    '6500k': 0x06,
    '5770k': 0x07,
    '5500k': 0x08,
    '5000k': 0x09,
    '4000k': 0x0A,
    '3400k': 0x0B,
    '3350k': 0x0C,
    '3000k': 0x0D,
    '2800k': 0x0E,
    '2600k': 0x0F,
    '1850k': 0x10,
    'user2': 0x12,
    'user-2': 0x12,
}

COLOR_TEMPERATURE_NAMES = {
    0x00: 'user1',
    0x01: 'native',
    0x02: '11000K',
    0x03: '10000K',
    0x04: '9300K',
    0x05: '7500K',
    0x06: '6500K',
    0x07: '5770K',
    0x08: '5500K',
    0x09: '5000K',
    0x0A: '4000K',
    0x0B: '3400K',
    0x0C: '3350K',
    0x0D: '3000K',
    0x0E: '2800K',
    0x0F: '2600K',
    0x10: '1850K',
    0x12: 'user2',
}

POWER_SAVE_MODES = {
    'rgb-off-video-off': 0x00,
    'rgb-off-video-on': 0x01,
    'rgb-on-video-off': 0x02,
    'rgb-on-video-on': 0x03,
    'mode-1': 0x04,
    'mode1': 0x04,
    'mode-2': 0x05,
    'mode2': 0x05,
    'mode-3': 0x06,
    'mode3': 0x06,
    'mode-4': 0x07,
    'mode4': 0x07,
}

POWER_SAVE_MODE_NAMES = {value: key for key, value in POWER_SAVE_MODES.items()}

SMART_POWER_LEVELS = {
    'off': 0x00,
    'low': 0x01,
    'medium': 0x02,
    'med': 0x02,
    'high': 0x03,
}

SMART_POWER_LEVEL_NAMES = {
    value: key for key, value in SMART_POWER_LEVELS.items()
    if key in {'off', 'low', 'medium', 'high'}
}

APM_MODES = {
    'off': 0x00,
    'on': 0x01,
    'mode1': 0x02,
    'mode-1': 0x02,
    'tcp-off-wol-on': 0x02,
    'mode2': 0x03,
    'mode-2': 0x03,
    'tcp-on-wol-off': 0x03,
}

APM_MODE_NAMES = {
    0x00: 'off',
    0x01: 'on',
    0x02: 'mode1',
    0x03: 'mode2',
}

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


def build_video_parameters_set_message(
    monitor_id,
    brightness=0xFF,
    color=0xFF,
    contrast=0xFF,
    sharpness=0xFF,
    tint=0xFF,
    black_level=0xFF,
    gamma=0xFF,
):
    """
    Build SICP message to set video parameters (0x32 command).
    0xFF for any parameter means "no change".
    """
    msg_size = 0x0C
    payload = [
        brightness & 0xFF,
        color & 0xFF,
        contrast & 0xFF,
        sharpness & 0xFF,
        tint & 0xFF,
        black_level & 0xFF,
        gamma & 0xFF,
    ]

    checksum = calculate_checksum(
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_VIDEO_PARAMETERS_SET,
        *payload,
    )

    return bytes([
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_VIDEO_PARAMETERS_SET,
        *payload,
        checksum,
    ])


def build_video_parameters_get_message(monitor_id):
    """Build SICP message to request video parameters (0x33 command)."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_VIDEO_PARAMETERS_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_VIDEO_PARAMETERS_GET, checksum])


def build_color_temperature_set_message(monitor_id, mode_code):
    """Build SICP message to set color temperature (0x34 command)."""
    msg_size = 0x06
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_COLOR_TEMPERATURE_SET, mode_code)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_COLOR_TEMPERATURE_SET, mode_code, checksum])


def build_color_temperature_get_message(monitor_id):
    """Build SICP message to request color temperature (0x35 command)."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_COLOR_TEMPERATURE_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_COLOR_TEMPERATURE_GET, checksum])


def build_color_temperature_fine_set_message(monitor_id, step_value):
    """Build SICP message to set 100K-step color temperature (0x11 command)."""
    msg_size = 0x06
    checksum = calculate_checksum(
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_COLOR_TEMPERATURE_FINE_SET,
        step_value,
    )
    return bytes([
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_COLOR_TEMPERATURE_FINE_SET,
        step_value,
        checksum,
    ])


def build_color_temperature_fine_get_message(monitor_id):
    """Build SICP message to request 100K-step color temperature (0x12 command)."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_COLOR_TEMPERATURE_FINE_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_COLOR_TEMPERATURE_FINE_GET, checksum])


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


def build_test_pattern_get_message(monitor_id):
    """Build SICP message to query the current internal test pattern."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_TEST_PATTERN_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_TEST_PATTERN_GET, checksum])


def build_test_pattern_set_message(monitor_id, pattern_code):
    """Build SICP message to set the internal test pattern."""
    msg_size = 0x06
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_TEST_PATTERN_SET, pattern_code)
    return bytes([
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_TEST_PATTERN_SET,
        pattern_code,
        checksum,
    ])


def build_remote_lock_get_message(monitor_id):
    """Build SICP message to get remote control lock status."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_REMOTE_LOCK_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_REMOTE_LOCK_GET, checksum])


def build_remote_lock_set_message(monitor_id, state_code):
    """Build SICP message to set remote control/keypad lock state."""
    msg_size = 0x06
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_REMOTE_LOCK_SET, state_code)
    return bytes([
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_REMOTE_LOCK_SET,
        state_code,
        checksum,
    ])


def build_power_on_logo_get_message(monitor_id):
    """Build SICP message to query power-on logo setting."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_POWER_ON_LOGO_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_POWER_ON_LOGO_GET, checksum])


def build_power_on_logo_set_message(monitor_id, mode_code):
    """Build SICP message to set power-on logo behavior."""
    msg_size = 0x06
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_POWER_ON_LOGO_SET, mode_code)
    return bytes([
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_POWER_ON_LOGO_SET,
        mode_code,
        checksum,
    ])


def build_osd_info_get_message(monitor_id):
    """Build SICP message to get information OSD timeout."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_OSD_INFO_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_OSD_INFO_GET, checksum])


def build_osd_info_set_message(monitor_id, timeout_code):
    """Build SICP message to set information OSD timeout."""
    msg_size = 0x06
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_OSD_INFO_SET, timeout_code)
    return bytes([
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_OSD_INFO_SET,
        timeout_code,
        checksum,
    ])


def build_auto_signal_get_message(monitor_id):
    """Build SICP message to query auto signal detection mode."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_AUTO_SIGNAL_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_AUTO_SIGNAL_GET, checksum])


def build_auto_signal_set_message(monitor_id, mode_code):
    """Build SICP message to set auto signal detection mode."""
    msg_size = 0x06
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_AUTO_SIGNAL_SET, mode_code)
    return bytes([
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_AUTO_SIGNAL_SET,
        mode_code,
        checksum,
    ])


def build_remote_key_simulation_message(monitor_id, key_code):
    """Build SICP message to simulate a remote control button press."""
    msg_size = 0x07
    reserved = 0x00
    checksum = calculate_checksum(
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_REMOTE_CONTROL_SIM,
        key_code,
        reserved,
    )
    return bytes([
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_REMOTE_CONTROL_SIM,
        key_code,
        reserved,
        checksum,
    ])


def build_group_id_get_message(monitor_id):
    """Build SICP message to query current group ID."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_GROUP_ID_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_GROUP_ID_GET, checksum])


def build_group_id_set_message(monitor_id, group_id):
    """Build SICP message to set the group ID."""
    msg_size = 0x06
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_GROUP_ID_SET, group_id)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_GROUP_ID_SET, group_id, checksum])


def build_monitor_id_set_message(monitor_id, new_monitor_id):
    """Build SICP message to assign a new monitor ID (SICP 7.15)."""
    msg_size = 0x06
    checksum = calculate_checksum(
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_MONITOR_ID_SET,
        new_monitor_id,
    )
    return bytes([
        msg_size,
        monitor_id,
        GROUP_ID,
        CMD_MONITOR_ID_SET,
        new_monitor_id,
        checksum,
    ])


def build_power_save_get_message(monitor_id):
    """Build SICP message to query current power save mode."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_POWER_SAVE_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_POWER_SAVE_GET, checksum])


def build_power_save_set_message(monitor_id, mode_code):
    """Build SICP message to set power save mode."""
    msg_size = 0x06
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_POWER_SAVE_SET, mode_code)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_POWER_SAVE_SET, mode_code, checksum])


def build_smart_power_get_message(monitor_id):
    """Build SICP message to query smart power level."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_SMART_POWER_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_SMART_POWER_GET, checksum])


def build_smart_power_set_message(monitor_id, level_code):
    """Build SICP message to set smart power level."""
    msg_size = 0x06
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_SMART_POWER_SET, level_code)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_SMART_POWER_SET, level_code, checksum])


def build_apm_get_message(monitor_id):
    """Build SICP message to query advanced power management state."""
    msg_size = 0x05
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_APM_GET)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_APM_GET, checksum])


def build_apm_set_message(monitor_id, mode_code):
    """Build SICP message to set advanced power management state."""
    msg_size = 0x06
    checksum = calculate_checksum(msg_size, monitor_id, GROUP_ID, CMD_APM_SET, mode_code)
    return bytes([msg_size, monitor_id, GROUP_ID, CMD_APM_SET, mode_code, checksum])


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

