## Philips Signage SICP Display Integration

This custom integration bridges Philips professional displays exposed via the Signage Control Protocol (SICP) with Home Assistant. It relies on the local `sicppy` library that ships with this repository, allowing you to monitor and control each panel without cloud dependencies.

### Features

- Registers displays via the Home Assistant config flow by providing the IP address, optional monitor ID (defaults to `1`), and the panel MAC address.
- Surfaces telemetry sensors for temperature (with all reported probes), model information, serial number, SICP firmware metadata, and the live power-state tri-state (offline/off/on).
- Adds select entities for Smart Power level, Power-On logo mode, cold-start behavior, and active input source so you can drive the panel configuration straight from Home Assistant.
- Provides a dedicated light entity that manages the panel backlight, brightness percentage, and (when SICP exposes it) precise color temperature; unsupported sources raise a friendly warning instead of crashing.
- Exposes power and mute switches plus a speaker-volume slider to emulate the classic remote-control experience.

### Network Requirements

Philips panels only accept SICP commands from IPs present in their ARP table. Ensure the display sits on the same subnet as Home Assistant or configure a static ARP entry on the panel/network infrastructure before attempting to add it.

### Setup

1. Copy the `sicp_homeassistant` folder into `custom_components/philips_sicp_display` in your Home Assistant instance.
2. Install the accompanying `sicppy` package (packaged in this repo) into the same Python environment if you are not using a workspace-aware installer.
3. Restart Home Assistant.
4. Use *Settings → Devices & Services → Add Integration* and search for **Philips SICP Display**.
5. Enter the IP, monitor ID, and MAC address when prompted; the flow validates connectivity before creating entities.

After onboarding, the coordinator polls every 60 seconds. Controls that a specific model/source combination does not expose (for example brightness/color temperature while an internal Android source is active) will gracefully report that the feature is unavailable.
