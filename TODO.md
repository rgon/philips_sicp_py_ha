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
+ [ ] CLI get_smart_power_level shall return the enum, not just '22'

GENERAL:
+ [ ] make async? easycli async.

# SICP HA integration
+ [x] remove "requirements": ["sicppy==0.2.0"] manifest.json
+ [x] release script
+ [x] test via ssh script
+ [x] fix incorrect repo (goes to rgon/philipsSignageHA)
+ [x] Setup flow fixes:
    + [x] move ARP note to bottom, where the MAC address is
    + [x] note on top to indicate it should be turned on
    + [x] monitor ID should be ticker/field input, not range slider
    + [x] keep the entered data, on error, don't reset fields
+ [x] fix flow:
    + [x] more descriptive payload
     The display responded with an unexpected payload. 
+ [-] develop script: uv sync --all-packages --all-groups

+ [x] no verbose '75BDLxxxxxxx power_xxxx'
+ [x] ensure entity is synced to other integrations: with unifi
+ [x] remove serial from sensor

+ [x] fix switches not saving status
+ [x] remove logs

+ [x] online/offline status
+ [x] if offline, call wol
+ [x] sleep after turn off to prevent race condition, since it takes some time to turn off

+ [ ] browser update command: modern HTML5/CSS support -> chromium 95

+ [ ] fix smart power not displaying
+ [ ] fix power on logo not displaying

+ [ ] how to access browser 1,2,3 inputs or mediaplayer inputs 1,2,3 from the select? -> browser-menu, browser-1 etc? SICP supports it as a second arg

+ [ ] disable all options if display is off except power on




+ [ ] relax requires-python to 3.13 since HA is not on 3.14
+ [ ] release action
+ [ ] ensure publishes with HACS https://www.hacs.xyz/docs/publish/




TEST WORKING:
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
    + [ ] merged mute and volume
As light:
    > Keep in mind that brightness and color temperature is not available if source is internal
    + [ ] get_precise_color_temperature | set_precise_color_temperature
    + [ ] get_brightness_level | set_brightness_level
