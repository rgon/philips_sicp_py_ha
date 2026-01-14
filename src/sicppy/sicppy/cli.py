import sys

from .ip_monitor import SICPIPMonitor
from .protocol import _coerce_kelvin_to_step_value, _enum_choice_names, _parse_enum_token
from .messages import (
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
)

# Hardcoded display configuration
DISPLAYS = {
    0: ("192.168.45.210", 1),  # Monitor ID 1
    1: ("192.168.45.211", 1),  # Monitor ID 1
}


def _normalize_choice(value):
    return value.lower().replace('_', '-').replace(' ', '-').strip()


def _enum_choice_list(enum_cls):
    return _enum_choice_names(enum_cls)


def _enum_choice_strings(enum_cls, aliases=None):
    choices = list(_enum_choice_list(enum_cls))
    if aliases:
        choices.extend(aliases.keys())
    # dict.fromkeys preserves insertion order while removing duplicates
    return list(dict.fromkeys(sorted(choices)))


def _resolve_enum_choice(enum_cls, raw_value, *, aliases=None, min_value=0, max_value=0xFF):
    normalized = _normalize_choice(raw_value)
    alias_map = aliases or {}
    if normalized in alias_map:
        return alias_map[normalized]

    try:
        return _parse_enum_token(enum_cls, raw_value).value
    except ValueError:
        pass

    try:
        parsed = int(raw_value, 0)
    except ValueError:
        parsed = None

    if parsed is None or not (min_value <= parsed <= max_value):
        raise ValueError(f"Invalid value '{raw_value}' for {enum_cls.__name__}")

    return parsed


AUTO_SIGNAL_ALIASES = {
    'pc-sources': AutoSignalMode.PC_ONLY.value,
    'video-sources': AutoSignalMode.VIDEO_ONLY.value,
}

POWER_SAVE_ALIASES = {
    'mode1': PowerSaveMode.MODE_1.value,
    'mode2': PowerSaveMode.MODE_2.value,
    'mode3': PowerSaveMode.MODE_3.value,
    'mode4': PowerSaveMode.MODE_4.value,
}

SMART_POWER_ALIASES = {
    'med': SmartPowerLevel.MEDIUM.value,
}

APM_ALIASES = {
    'mode-1': ApmMode.MODE1.value,
    'tcp-off-wol-on': ApmMode.MODE1.value,
    'mode-2': ApmMode.MODE2.value,
    'tcp-on-wol-off': ApmMode.MODE2.value,
}

REMOTE_KEY_ALIASES = {
    'vol+': RemoteKey.VOL_PLUS.value,
    'vol-': RemoteKey.VOL_MINUS.value,
    'volume+': RemoteKey.VOL_PLUS.value,
    'volume-': RemoteKey.VOL_MINUS.value,
    'volume-plus': RemoteKey.VOL_PLUS.value,
    'volume-minus': RemoteKey.VOL_MINUS.value,
    'volumeup': RemoteKey.VOL_PLUS.value,
    'volup': RemoteKey.VOL_PLUS.value,
    'voldown': RemoteKey.VOL_MINUS.value,
    'volume-down': RemoteKey.VOL_MINUS.value,
}

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
    print("  get-brightness            Get brightness percentage (0-100)")
    print("  set-brightness <0-100>    Set brightness via video parameters")
    print("  get-color-temp            Get color temperature preset")
    print("  set-color-temp <mode>     Set color temperature (native, 6500K, ...)")
    print("  get-color-temp-precise    Get User 2 color temperature in 100K steps")
    print("  set-color-temp-precise <kelvin|step>  Set User 2 color temp in 100K steps")
    print("  get-test-pattern          Get current internal test pattern")
    print("  set-test-pattern <name>   Set internal test pattern (off|white|red|...)")
    print("  get-remote-lock           Get remote control/keypad lock state")
    print("  set-remote-lock <mode>    Set remote lock (unlock-all|lock-all|...)")
    print("  remote-key <name>         Simulate remote control key press")
    print("  get-power-on-logo         Get power-on logo mode")
    print("  set-power-on-logo <mode>  Set power-on logo (off|on|user)")
    print("  get-osd-info              Get information OSD timeout")
    print("  set-osd-info <sec|off>    Set information OSD timeout (off|1-60)")
    print("  get-auto-signal           Get auto signal detection mode")
    print("  set-auto-signal <mode>    Set auto signal detection (off|all|pc-only|...)")
    print("  get-power-save            Get power save mode")
    print("  set-power-save <mode>     Set power save mode (rgb-off-video-off, ...)")
    print("  get-smart-power           Get smart power level")
    print("  set-smart-power <level>   Set smart power level (off|low|medium|high)")
    print("  get-apm                   Get advanced power management mode")
    print("  set-apm <mode>            Set advanced power management (off|on|mode1|mode2)")
    print("  get-group-id              Get current group ID")
    print("  set-group-id <id|off>     Set group ID (1-254 or ff for off)")
    print("  set-monitor-id <id>       Set monitor ID (1-255)")
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
        monitor_ids = [SICPIPMonitor(ip=ip, monitor_id=mon_id) for (ip, mon_id) in DISPLAYS.values()]
    else:
        try:
            monitor_key = int(monitor_arg)
            if monitor_key not in DISPLAYS:
                print(f"Error: Unknown monitor ID {monitor_key}")
                print(f"Available monitors: {', '. join(map(str, DISPLAYS.keys()))}")
                sys.exit(1)
            this_selection = DISPLAYS[monitor_key]
            monitor_ids = [SICPIPMonitor(ip=this_selection[0], monitor_id=this_selection[1])]
        except ValueError:
            print("Error: Monitor ID must be a number or 'all'")
            sys.exit(1)
    
    # Execute command
    success_count = 0
    
    if command == "on": 
        for monitor in monitor_ids: 
            if monitor.set_power(monitor.monitor_id, True):
                success_count += 1
    
    elif command == "off": 
        for monitor in monitor_ids:
            if monitor.set_power(monitor.monitor_id, False):
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

        for monitor in monitor_ids:
            if monitor.set_power(monitor.monitor_id, desired_on):
                success_count += 1
    
    elif command == "backlight-on":
        for monitor in monitor_ids:
            if monitor.set_backlight(monitor.monitor_id, True):
                success_count += 1
    
    elif command == "backlight-off": 
        for monitor in monitor_ids:
            if monitor.set_backlight(monitor.monitor_id, False):
                success_count += 1
    
    elif command == "get-backlight":
        for monitor in monitor_ids: 
            if monitor.get_backlight_state(monitor.monitor_id):
                success_count += 1
    
    elif command == "4k-on": 
        for monitor in monitor_ids:
            if monitor.set_android_4k_state(monitor.monitor_id, True):
                success_count += 1
    
    elif command == "4k-off":
        for monitor in monitor_ids:
            if monitor.set_android_4k_state(monitor.monitor_id, False):
                success_count += 1
    
    elif command == "get-4k":
        for monitor in monitor_ids: 
            if monitor.get_android_4k_state(monitor.monitor_id):
                success_count += 1

    elif command == "get-power":
        for monitor in monitor_ids:
            if monitor.get_power_state(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "get-cold-start":
        for monitor in monitor_ids:
            if monitor.get_cold_start_power_state(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "set-cold-start":
        if len(sys.argv) < 4:
            print("Error: set-cold-start requires a mode (off|forced|last)")
            sys.exit(1)

        mode = sys.argv[3].lower()
        if mode in {"off", "power-off", "0", "0x00"}:
            cold_state = ColdStartPowerState.COLD_START_POWER_OFF
        elif mode in {"forced", "forced-on", "on", "1", "0x01"}:
            cold_state = ColdStartPowerState.COLD_START_FORCED_ON
        elif mode in {"last", "last-status", "2", "0x02"}:
            cold_state = ColdStartPowerState.COLD_START_LAST_STATUS
        else:
            print("Error: set-cold-start mode must be off|forced|last")
            sys.exit(1)

        for monitor in monitor_ids:
            if monitor.set_cold_start_power_state(monitor.monitor_id, cold_state):
                success_count += 1

    elif command == "get-temperature":
        for monitor in monitor_ids:
            if monitor.get_temperature(monitor.monitor_id) is not None:
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

        for monitor in monitor_ids:
            if monitor.get_sicp_info(monitor.monitor_id, label_code) is not None:
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

        for monitor in monitor_ids:
            if monitor.get_model_info(monitor.monitor_id, label_code) is not None:
                success_count += 1

    elif command == "get-serial":
        for monitor in monitor_ids:
            if monitor.get_serial_number(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "get-video-signal":
        for monitor in monitor_ids:
            if monitor.get_video_signal_status(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "get-picture-style":
        for monitor in monitor_ids:
            if monitor.get_picture_style(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "set-picture-style":
        if len(sys.argv) < 4:
            print("Error: set-picture-style requires a style name or numeric code")
            print(f"Available styles: {', '.join(_enum_choice_list(PictureStyle))}")
            sys.exit(1)

        style_arg_raw = sys.argv[3]

        try:
            style_code = _resolve_enum_choice(PictureStyle, style_arg_raw)
        except ValueError:
            print("Error: Unknown picture style. Use a known name or 0-255 code.")
            print(f"Available styles: {', '.join(_enum_choice_list(PictureStyle))}")
            sys.exit(1)

        for monitor in monitor_ids:
            if monitor.set_picture_style(monitor.monitor_id, style_code):
                success_count += 1

    elif command == "get-brightness":
        for monitor in monitor_ids:
            if monitor.get_brightness_level(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "set-brightness":
        """
        Note 2: This command is only supported on external sources(HDMI, DVI, …) and not on Android sources(Browser,
        Mediaplayer, Custom App) on all models where video parameters are greyed out in the menu when an internal
        source is active. This includes but is not restricted to the following models:
        xxBDL3452T, xxBDL3651T, xxBDL3552T, xxBDL3652T, xxBDL3052E, xxBDL4052E/00 & /02, xxBDL3550Q,
        xxBDL3650Q, xxBDL4550D
        """
        if len(sys.argv) < 4:
            print("Error: set-brightness requires a value between 0 and 100")
            sys.exit(1)

        try:
            requested_value = int(sys.argv[3], 0)
        except ValueError:
            print("Error: Brightness must be an integer between 0 and 100")
            sys.exit(1)

        clamped_value = max(0, min(100, requested_value))
        if clamped_value != requested_value:
            print(f"Warning: brightness {requested_value} out of range, clamped to {clamped_value}")

        for monitor in monitor_ids:
            if monitor.set_brightness_level(monitor.monitor_id, clamped_value):
                success_count += 1

    elif command == "get-color-temp":
        for monitor in monitor_ids:
            if monitor.get_color_temperature_mode(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "set-color-temp":
        """
        This command shares the same platform limitations as other video parameter adjustments (see SICP 8.1 notes).
        It is typically only available on external sources when the video parameter menu is active.
        """
        if len(sys.argv) < 4:
            print("Error: set-color-temp requires a mode name or numeric code")
            print(f"Available modes: {', '.join(_enum_choice_list(ColorTemperatureMode))}")
            sys.exit(1)

        mode_arg_raw = sys.argv[3]
        try:
            mode_code = _parse_enum_token(ColorTemperatureMode, mode_arg_raw).value
        except ValueError:
            try:
                parsed = int(mode_arg_raw, 0)
            except ValueError:
                parsed = None

            if parsed is None or not (0 <= parsed <= 0xFF):
                print("Error: Color temperature must match a known preset name or be a 0-255 code")
                print(f"Available modes: {', '.join(_enum_choice_list(ColorTemperatureMode))}")
                sys.exit(1)

            mode_code = parsed

        for monitor in monitor_ids:
            try:
                if monitor.set_color_temperature_mode(monitor.monitor_id, mode_code):
                    success_count += 1
            except ValueError as exc:
                print(f"Error: {exc}")
                sys.exit(1)

    elif command == "get-color-temp-precise":
        for monitor in monitor_ids:
            if monitor.get_precise_color_temperature(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "set-color-temp-precise":
        """
        Uses the 100K-step SICP command and automatically switches the preset to User 2 before applying.
        """
        if len(sys.argv) < 4:
            print("Error: set-color-temp-precise requires a Kelvin value or step (20-100)")
            sys.exit(1)

        raw_arg = sys.argv[3].strip().lower()
        if raw_arg.endswith('k'):
            raw_arg = raw_arg[:-1]

        try:
            parsed_value = int(raw_arg, 0)
        except ValueError:
            print("Error: Color temperature must be an integer Kelvin value or step (20-100)")
            sys.exit(1)

        if 20 <= parsed_value <= 100:
            desired_kelvin = parsed_value * 100
        else:
            desired_kelvin = parsed_value

        try:
            _, resolved_kelvin = _coerce_kelvin_to_step_value(desired_kelvin)
        except ValueError as exc:
            print(f"Error: {exc}")
            sys.exit(1)

        if resolved_kelvin != desired_kelvin:
            print(f"Info: Requested {desired_kelvin}K adjusted to {resolved_kelvin}K (100K steps)")

        for monitor in monitor_ids:
            if monitor.set_precise_color_temperature(monitor.monitor_id, resolved_kelvin):
                success_count += 1

    elif command == "get-test-pattern":
        for monitor in monitor_ids:
            if monitor.get_test_pattern(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "set-test-pattern":
        if len(sys.argv) < 4:
            print("Error: set-test-pattern requires a pattern name or numeric code")
            print(f"Available patterns: {', '.join(_enum_choice_list(TestPattern))}")
            sys.exit(1)

        pattern_arg_raw = sys.argv[3]
        try:
            pattern_code = _parse_enum_token(TestPattern, pattern_arg_raw).value
        except ValueError:
            try:
                parsed = int(pattern_arg_raw, 0)
            except ValueError:
                parsed = None

            if parsed is None or not (0 <= parsed <= 0xFF):
                print("Error: Unknown test pattern. Use a known name or 0-255 code.")
                print(f"Available patterns: {', '.join(_enum_choice_list(TestPattern))}")
                sys.exit(1)

            pattern_code = parsed

        for monitor in monitor_ids:
            if monitor.set_test_pattern(monitor.monitor_id, pattern_code):
                success_count += 1

    elif command == "get-remote-lock":
        for monitor in monitor_ids:
            if monitor.get_remote_lock_state(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "set-remote-lock":
        if len(sys.argv) < 4:
            print("Error: set-remote-lock requires a mode name or numeric code")
            print(f"Available modes: {', '.join(_enum_choice_list(RemoteLockState))}")
            sys.exit(1)

        mode_arg_raw = sys.argv[3]
        try:
            mode_code = _resolve_enum_choice(RemoteLockState, mode_arg_raw)
        except ValueError:
            print("Error: Unknown remote lock mode. Use a known name or 0-255 code.")
            print(f"Available modes: {', '.join(_enum_choice_list(RemoteLockState))}")
            sys.exit(1)

        for monitor in monitor_ids:
            if monitor.set_remote_lock_state(monitor.monitor_id, mode_code):
                success_count += 1

    elif command == "remote-key":
        if len(sys.argv) < 4:
            print("Error: remote-key requires a button name or numeric code")
            print(f"Available keys: {', '.join(_enum_choice_strings(RemoteKey, REMOTE_KEY_ALIASES))}")
            sys.exit(1)

        key_arg_raw = sys.argv[3]
        try:
            key_code = _resolve_enum_choice(
                RemoteKey,
                key_arg_raw,
                aliases=REMOTE_KEY_ALIASES,
            )
        except ValueError:
            print("Error: Unknown remote key. Use a known name or 0-255 code.")
            print(f"Available keys: {', '.join(_enum_choice_strings(RemoteKey, REMOTE_KEY_ALIASES))}")
            sys.exit(1)

        for monitor in monitor_ids:
            if monitor.simulate_remote_key(monitor.monitor_id, key_code):
                success_count += 1

    elif command == "get-power-on-logo":
        for monitor in monitor_ids:
            if monitor.get_power_on_logo_mode(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "set-power-on-logo":
        if len(sys.argv) < 4:
            print("Error: set-power-on-logo requires a mode name or numeric code")
            print(f"Available modes: {', '.join(_enum_choice_list(PowerOnLogoMode))}")
            sys.exit(1)

        mode_arg_raw = sys.argv[3]
        try:
            mode_code = _resolve_enum_choice(PowerOnLogoMode, mode_arg_raw)
        except ValueError:
            print("Error: Unknown power-on logo mode. Use off|on|user or 0-255 code.")
            print(f"Available modes: {', '.join(_enum_choice_list(PowerOnLogoMode))}")
            sys.exit(1)

        for monitor in monitor_ids:
            if monitor.set_power_on_logo_mode(monitor.monitor_id, mode_code):
                success_count += 1

    elif command == "get-osd-info":
        for monitor in monitor_ids:
            if monitor.get_osd_info_timeout(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "set-osd-info":
        if len(sys.argv) < 4:
            print("Error: set-osd-info requires 'off' or a numeric timeout (1-60)")
            sys.exit(1)

        timeout_arg = sys.argv[3].strip().lower()
        if timeout_arg in {"off", "0", "0x00"}:
            timeout_code = 0
        else:
            try:
                timeout_code = int(sys.argv[3], 0)
            except ValueError:
                print("Error: Timeout must be 'off' or an integer between 1 and 60")
                sys.exit(1)

        if timeout_code != 0 and not (1 <= timeout_code <= 60):
            print("Error: Timeout must be 1-60 seconds or 'off'")
            sys.exit(1)

        for monitor in monitor_ids:
            try:
                if monitor.set_osd_info_timeout(monitor.monitor_id, timeout_code):
                    success_count += 1
            except ValueError as exc:
                print(f"Error: {exc}")
                sys.exit(1)

    elif command == "get-auto-signal":
        for monitor in monitor_ids:
            if monitor.get_auto_signal_mode(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "set-auto-signal":
        if len(sys.argv) < 4:
            print("Error: set-auto-signal requires a mode name or numeric code (0-5)")
            print(f"Available modes: {', '.join(_enum_choice_strings(AutoSignalMode, AUTO_SIGNAL_ALIASES))}")
            sys.exit(1)

        mode_arg_raw = sys.argv[3]
        try:
            mode_code = _resolve_enum_choice(
                AutoSignalMode,
                mode_arg_raw,
                aliases=AUTO_SIGNAL_ALIASES,
                max_value=0x05,
            )
        except ValueError:
            print("Error: Auto signal mode must be off|all|pc-only|video-only|failover or 0-5")
            print(f"Available modes: {', '.join(_enum_choice_strings(AutoSignalMode, AUTO_SIGNAL_ALIASES))}")
            sys.exit(1)

        for monitor in monitor_ids:
            try:
                if monitor.set_auto_signal_mode(monitor.monitor_id, mode_code):
                    success_count += 1
            except ValueError as exc:
                print(f"Error: {exc}")
                sys.exit(1)

    elif command == "get-power-save":
        for monitor in monitor_ids:
            if monitor.get_power_save_mode(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "set-power-save":
        if len(sys.argv) < 4:
            print("Error: set-power-save requires a mode name or numeric code")
            print(f"Available modes: {', '.join(_enum_choice_strings(PowerSaveMode, POWER_SAVE_ALIASES))}")
            sys.exit(1)

        mode_arg_raw = sys.argv[3]
        try:
            mode_code = _resolve_enum_choice(
                PowerSaveMode,
                mode_arg_raw,
                aliases=POWER_SAVE_ALIASES,
            )
        except ValueError:
            print("Error: Unknown power save mode. Use a known name or 0-255 code.")
            print(f"Available modes: {', '.join(_enum_choice_strings(PowerSaveMode, POWER_SAVE_ALIASES))}")
            sys.exit(1)

        for monitor in monitor_ids:
            if monitor.set_power_save_mode(monitor.monitor_id, mode_code):
                success_count += 1

    elif command == "get-smart-power":
        for monitor in monitor_ids:
            if monitor.get_smart_power_level(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "set-smart-power":
        if len(sys.argv) < 4:
            print("Error: set-smart-power requires a level name or numeric code")
            print(f"Available levels: {', '.join(_enum_choice_strings(SmartPowerLevel, SMART_POWER_ALIASES))}")
            sys.exit(1)

        level_arg_raw = sys.argv[3]
        try:
            level_code = _resolve_enum_choice(
                SmartPowerLevel,
                level_arg_raw,
                aliases=SMART_POWER_ALIASES,
            )
        except ValueError:
            print("Error: Unknown smart power level. Use off|low|medium|high or 0-255 code.")
            print(f"Available levels: {', '.join(_enum_choice_strings(SmartPowerLevel, SMART_POWER_ALIASES))}")
            sys.exit(1)

        for monitor in monitor_ids:
            if monitor.set_smart_power_level(monitor.monitor_id, level_code):
                success_count += 1

    elif command == "get-apm":
        for monitor in monitor_ids:
            if monitor.get_apm_mode(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "set-apm":
        if len(sys.argv) < 4:
            print("Error: set-apm requires a mode name or numeric code")
            print(f"Available modes: {', '.join(_enum_choice_strings(ApmMode, APM_ALIASES))}")
            sys.exit(1)

        apm_arg_raw = sys.argv[3]
        try:
            apm_code = _resolve_enum_choice(
                ApmMode,
                apm_arg_raw,
                aliases=APM_ALIASES,
            )
        except ValueError:
            print("Error: Unknown APM mode. Use off|on|mode1|mode2 or 0-255 code.")
            print(f"Available modes: {', '.join(_enum_choice_strings(ApmMode, APM_ALIASES))}")
            sys.exit(1)

        for monitor in monitor_ids:
            if monitor.set_apm_mode(monitor.monitor_id, apm_code):
                success_count += 1

    elif command == "get-group-id":
        for monitor in monitor_ids:
            if monitor.get_group_id(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "set-group-id":
        if len(sys.argv) < 4:
            print("Error: set-group-id requires a numeric value or 'off'")
            sys.exit(1)

        raw_value = sys.argv[3].strip().lower()
        if raw_value in {"off", "0xff", "ff"}:
            group_value = 0xFF
        else:
            try:
                group_value = int(sys.argv[3], 0)
            except ValueError:
                print("Error: Group ID must be a number (1-254) or 'off'")
                sys.exit(1)

        if not ((1 <= group_value <= 254) or group_value == 0xFF):
            print("Error: Group ID must be 1-254 or 'off' (0xFF)")
            sys.exit(1)

        for monitor in monitor_ids:
            try:
                if monitor.set_group_id(monitor.monitor_id, group_value):
                    success_count += 1
            except ValueError as exc:
                print(f"Error: {exc}")
                sys.exit(1)

    elif command == "set-monitor-id":
        if len(sys.argv) < 4:
            print("Error: set-monitor-id requires a numeric value (1-255)")
            sys.exit(1)

        try:
            new_monitor_id = int(sys.argv[3], 0)
        except ValueError:
            print("Error: Monitor ID must be a number between 1 and 255")
            sys.exit(1)

        if not 1 <= new_monitor_id <= 0xFF:
            print("Error: Monitor ID must be between 1 and 255")
            sys.exit(1)

        for monitor in monitor_ids:
            try:
                if monitor.set_monitor_id(monitor.monitor_id, new_monitor_id):
                    success_count += 1
            except ValueError as exc:
                print(f"Error: {exc}")
                sys.exit(1)

    elif command == "get-volume":
        for monitor in monitor_ids:
            if monitor.get_volume(monitor.monitor_id) is not None:
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

        for monitor in monitor_ids:
            try:
                if monitor.set_volume(monitor.monitor_id, speaker_value, audio_value):
                    success_count += 1
            except ValueError as exc:
                print(f"Error: {exc}")
                sys.exit(1)

    elif command == "get-mute":
        for monitor in monitor_ids:
            if monitor.get_mute_status(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "mute-on":
        for monitor in monitor_ids:
            if monitor.set_mute(monitor.monitor_id, True):
                success_count += 1

    elif command == "mute-off":
        for monitor in monitor_ids:
            if monitor.set_mute(monitor.monitor_id, False):
                success_count += 1

    elif command == "get-av-mute":
        for monitor in monitor_ids:
            if monitor.get_av_mute_status(monitor.monitor_id) is not None:
                success_count += 1

    elif command == "av-mute-on":
        for monitor in monitor_ids:
            if monitor.set_av_mute(monitor.monitor_id, True):
                success_count += 1

    elif command == "av-mute-off":
        for monitor in monitor_ids:
            if monitor.set_av_mute(monitor.monitor_id, False):
                success_count += 1

    elif command == "get-ip":
        if len(sys.argv) < 4:
            print("Error: get-ip requires a parameter name")
            print(f"Available parameters: {', '.join(_enum_choice_list(IPParameterCode))}")
            sys.exit(1)

        parameter_name = sys.argv[3].lower()
        value_type = 'current'

        if len(sys.argv) >= 5:
            value_type = sys.argv[4].lower()

        for monitor in monitor_ids:
            if monitor.get_ip_parameter(monitor.monitor_id, parameter_name, value_type):
                success_count += 1

    elif command == "wol-on":
        for monitor in monitor_ids:
            if monitor.set_wol(monitor.monitor_id, True):
                success_count += 1

    elif command == "wol-off":
        for monitor in monitor_ids:
            if monitor.set_wol(monitor.monitor_id, False):
                success_count += 1

    elif command == "get-wol":
        for monitor in monitor_ids:
            if monitor.get_wake_on_lan(monitor.monitor_id):
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
        
        for monitor in monitor_ids: 
            if monitor.set_input_source(monitor.monitor_id, input_source_name, playlist):
                success_count += 1
    
    elif command == "get-input": 
        for monitor in monitor_ids:
            if monitor.get_input_source(monitor.monitor_id):
                success_count += 1
    
    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)
    
    # Print summary for multi-monitor operations
    if len(monitor_ids) > 1:
        print(f"\n{'✓' if success_count == len(monitor_ids) else '⚠'} Command succeeded on {success_count}/{len(monitor_ids)} displays")
    
    sys.exit(0 if success_count == len(monitor_ids) else 1)
