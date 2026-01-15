# SICPpy
+ [x] Implement the cold-start-power-state methods
+ [x] implement a method to get temperature
+ [x] implement a method to get the SICP version
+ [x] implement a method to get the model & firmware Information
+ [x] implement a method to get the serial number
+ [x] implement an A/V mute get/set method
+ [x] implement the video style methods
+ [x] implement the power save mode get/set methods
+ [x] implement the smart power get/set mode
+ [x] implement the advanced power management get/set methods
+ [x] get monitor ID and group
+ [x] implement the test pattern method

+ [x] implement the remote lock/unlock methods
+ [x] implement remote control simulation, converting key codes to the given remote code with a dict/mapping

+ [x] implement power on logo settings
+ [x] implement osd information methods

+ [x] implement auto source methods

+ [x] set brightness
+ [x] get and set the color temperature
+ [x] precise color

+ [x] refactor: split to package and separate files
+ [x] refactor: OOP structure, independant of protocol 
+ [x] refactor: use logging instead of print, print on call and not transport implementation

+ [x] refactor: use enums instead of bodge dicts
+ [x] refactor: no longer all those build_xxx -> single build_message with parameters

+ [x] save monitor ID, group id in the class instance

+ [x] response errors to parse response
+ [x] return proper types on class methods

+ [x] protocol: remove useless _enum_label and _parse_enum_token and _enum_choice_names

CLI:
+ [ ] save configured monitors in file/env. Do NOT hardcode
+ [ ] get mac/save mac

# SICP HA integration
+ [ ] configure monitors: set IP, monitor ID (optional, default = 1), MAC address
SETUP UI NOTE:
> NOTE: the displays MUST be powered on manually right now.
+ [ ] expose status (polling):
    + [ ] get_temperature
    + [ ] get_model_info
    + [ ] get_serial_number
    + [ ] get_sicp_info

CONFIG/dropdown:
    + [ ] get_cold_start_power_state | set_cold_start_power_state
    + [ ] get_smart_power_level | set_smart_power_level
    + [ ] get_power_on_logo_mode | set_power_on_logo_mode
    + [ ] get_input_source | set_input_source
On/Off:
    + [ ] get_power_state power:offline/off/on
    + [ ] get_backlight_state | set_backlight (or as light on/off!)
Volume slider:
    + [ ] get_mute | set_mute
    + [ ] get_volume | set_volume
As light:
    > Keep in mind that brightness and color temperature is not available if source is internal
    + [ ] get_precise_color_temperature | set_precise_color_temperature
    + [ ] get_brightness_level | set_brightness_level

## WOL
+ [ ] get mac from SICP
    + if not possible, use getmac
    + if else, don't use scapy (requires root): ignore

+ [ ] resolve mac of device given ip python? NOTE: works only in current subnet
> static ARP entry on router note:

    arp -i br45 -s 192.168.xx.xxx 18:65:yy:yy:yy:yy
    arp -i br45 -s 192.168.xx.xxx 18:65:yy:yy:yy:yy