from enum import IntEnum

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
class PowerState(IntEnum):
    POWER_OFF = 0x01
    POWER_ON = 0x02

# Cold-start Power States
class ColdStartPowerState(IntEnum):
    COLD_START_POWER_OFF = 0x00
    COLD_START_FORCED_ON = 0x01
    COLD_START_LAST_STATUS = 0x02


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

# IP Parameter identifiers
class IPParameterCode(IntEnum):
    IP = 0x01
    SUBNET = 0x02
    GATEWAY = 0x03
    DNS1 = 0x04
    DNS2 = 0x05
    ETH_MAC = 0x06
    WIFI_MAC = 0x07


class IPParameterValueType(IntEnum):
    CURRENT = 0x01
    QUEUED = 0x02

# Group ID
GROUP_ID = 0x00

class InputSource(IntEnum):
    NONE = 0x00
    VIDEO = 0x01
    SVIDEO = 0x02
    COMPONENT = 0x03
    CVI2 = 0x04
    VGA = 0x05
    HDMI2 = 0x06
    DISPLAYPORT2 = 0x07
    USB2 = 0x08
    CARDDVI_D = 0x09
    DISPLAYPORT1 = 0x0A
    CARDOPS = 0x0B
    USB1 = 0x0C
    HDMI1 = 0x0D
    DVI_D = 0x0E
    HDMI3 = 0x0F
    BROWSER = 0x10
    SMARTCMS = 0x11
    DMS = 0x12
    INTERNALSTORAGE = 0x13
    MEDIAPLAYER = 0x16
    PDFPLAYER = 0x17
    CUSTOMAPP = 0x18
    HDMI4 = 0x19
    VGA2 = 0x1A
    VGA3 = 0x1B
    IWB = 0x1C
    CMNDPLAY = 0x1D
    HOME = 0x1E
    USBTYPEC = 0x1F
    KIOSK = 0x20
    SMARTINFO = 0x21
    TUNER = 0x22
    GOOGLECAST = 0x23
    INTERACT = 0x24
    USBTYPEC2 = 0x25
    SCREENSHARE = 0x26

    S_VIDEO = SVIDEO
    CUSTOM = CUSTOMAPP
    CMNDPLAYWEB = CMNDPLAY
    LAUNCHER = HOME
    HDMI = HDMI1
    USBC = USBTYPEC
    DIGITALMEDIASERVER = DMS
    USBC2 = USBTYPEC2

class PictureStyle(IntEnum):
    HIGHBRIGHT = 0x00
    SRGB = 0x01
    VIVID = 0x02
    NATURAL = 0x03
    STANDARD = 0x04
    VIDEO = 0x05
    STATIC_SIGNAGE = 0x06
    TEXT = 0x07
    ENERGY_SAVING = 0x08
    SOFT = 0x09
    USER = 0x0A

class TestPattern(IntEnum):
    OFF = 0x00
    WHITE_100 = 0x01
    WHITE = WHITE_100
    RED = 0x02
    GREEN = 0x03
    BLUE = 0x04
    BLACK = 0x05
    HALF_WHITE_TOP = 0x06
    HALF_WHITE_BOTTOM = 0x07
    RAMP = 0x08
    WHITE_12 = 0x09
    WHITE_25 = 0x0A
    WHITE_65 = 0x0B

class RemoteLockState(IntEnum):
    UNLOCK_ALL = 0x01
    LOCK_ALL = 0x02
    LOCK_ALL_BUT_POWER = 0x03
    LOCK_ALL_BUT_VOLUME = 0x04
    PRIMARY = 0x05
    SECONDARY = 0x06
    LOCK_ALL_EXCEPT_POWER_VOLUME = 0x07


class RemoteKey(IntEnum):
    KEY_0 = 0x00
    KEY_1 = 0x01
    KEY_2 = 0x02
    KEY_3 = 0x03
    KEY_4 = 0x04
    KEY_5 = 0x05
    KEY_6 = 0x06
    KEY_7 = 0x07
    KEY_8 = 0x08
    KEY_9 = 0x09
    BACK = 0x0A
    MUTE = 0x0D
    INFO = 0x0F
    VOL_PLUS = 0x10
    VOL_MINUS = 0x11
    FWD = 0x28
    RWD = 0x2B
    PLAY = 0x2C
    PAUSE = 0x30
    STOP = 0x31
    SOURCES = 0x38
    OPTIONS = 0x40
    HOME = 0x54
    ARROW_UP = 0x58
    ARROW_DOWN = 0x59
    ARROW_LEFT = 0x5A
    ARROW_RIGHT = 0x5B
    OK = 0x5C
    RED = 0x6D
    GREEN = 0x6E
    YELLOW = 0x6F
    BLUE = 0x70
    LIST = 0x8B
    ADJUST = 0x90
    POWER_ON = 0xBE
    POWER_OFF = 0xBF
    FORMAT = 0xF5

    VOLUME_UP = VOL_PLUS
    VOLUME_DOWN = VOL_MINUS
    VOL_PLUS_SYM = VOL_PLUS
    VOL_MINUS_SYM = VOL_MINUS
    FORWARD = FWD
    REWIND = RWD
    ENTER = OK
    SELECT = OK
    UP = ARROW_UP
    DOWN = ARROW_DOWN
    LEFT = ARROW_LEFT
    RIGHT = ARROW_RIGHT

class PowerOnLogoMode(IntEnum):
    OFF = 0x00
    ON = 0x01
    USER = 0x02


class AutoSignalMode(IntEnum):
    OFF = 0x00
    ALL = 0x01
    RESERVED = 0x02
    PC_ONLY = 0x03
    VIDEO_ONLY = 0x04
    FAILOVER = 0x05


class ColorTemperatureMode(IntEnum):
    USER1 = 0x00
    NATIVE = 0x01
    K11000 = 0x02
    K10000 = 0x03
    K9300 = 0x04
    K7500 = 0x05
    K6500 = 0x06
    K5770 = 0x07
    K5500 = 0x08
    K5000 = 0x09
    K4000 = 0x0A
    K3400 = 0x0B
    K3350 = 0x0C
    K3000 = 0x0D
    K2800 = 0x0E
    K2600 = 0x0F
    K1850 = 0x10
    USER2 = 0x12

    USER_1 = USER1
    USER_2 = USER2

class PowerSaveMode(IntEnum):
    RGB_OFF_VIDEO_OFF = 0x00
    RGB_OFF_VIDEO_ON = 0x01
    RGB_ON_VIDEO_OFF = 0x02
    RGB_ON_VIDEO_ON = 0x03
    MODE_1 = 0x04
    MODE_2 = 0x05
    MODE_3 = 0x06
    MODE_4 = 0x07


class SmartPowerLevel(IntEnum):
    OFF = 0x00
    LOW = 0x01
    MEDIUM = 0x02
    HIGH = 0x03


class ApmMode(IntEnum):
    OFF = 0x00
    ON = 0x01
    MODE1 = 0x02
    MODE2 = 0x03


def calculate_checksum(*bytes_list):
    """Calculate XOR checksum of all bytes."""
    checksum = 0
    for byte in bytes_list:
        checksum ^= byte
    return checksum


def build_power_message(monitor_id, power_on):
    """Build SICP message for screen power control (set)."""
    msg_size = 0x06
    param = PowerState.POWER_ON if power_on else PowerState.POWER_OFF
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
    param = 0x01 if backlight_on else 0x00
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
    param = 0x01 if enable_4k else 0x00
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
    param = 0x01 if enable_wol else 0x00
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

