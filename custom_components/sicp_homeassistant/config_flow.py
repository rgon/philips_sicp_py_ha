"""Config flow for the Philips SICP display integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector
from homeassistant.helpers.device_registry import format_mac
from homeassistant.exceptions import HomeAssistantError

from sicppy.ip_monitor import NetworkError

from .const import CONF_MAC_ADDRESS, CONF_MONITOR_ID, DEFAULT_MONITOR_ID, DOMAIN
from .coordinator import SicpDisplayClient


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidResponse(HomeAssistantError):
    """Error to indicate the device returned an unexpected payload."""

MAC_REGEX = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"

class PhilipsSicpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure new SICP displays."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        description_placeholders: dict[str, str] | None = None

        if user_input is not None:
            user_input = user_input.copy()
            monitor_id = user_input.get(CONF_MONITOR_ID, DEFAULT_MONITOR_ID)
            try:
                # coerce int
                user_input[CONF_MONITOR_ID] = int(monitor_id)
            except (TypeError, ValueError):
                errors[CONF_MONITOR_ID] = "invalid_monitor_id"

            try:
                cv.matches_regex(MAC_REGEX)(user_input[CONF_MAC_ADDRESS])
            except vol.Invalid:
                errors[CONF_MAC_ADDRESS] = "invalid_mac"

            if not errors:
                try:
                    info = await self._async_validate_input(self.hass, user_input)
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except InvalidResponse as err:
                    errors["base"] = "setup_error"
                    detail = str(err) or "See logs for details"
                    description_placeholders = {"error_detail": detail}
                except Exception:  # noqa: BLE001
                    errors["base"] = "unknown"
                else:
                    await self.async_set_unique_id(info["unique_id"])
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(title=info["title"], data=info["data"])

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_MONITOR_ID, default=DEFAULT_MONITOR_ID): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=255,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(CONF_MAC_ADDRESS): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(schema, user_input or {}),
            errors=errors,
            description_placeholders=description_placeholders,
        )

    async def _async_validate_input(
        self, hass: HomeAssistant, user_input: dict
    ) -> dict:
        """Validate the user input allows us to connect."""
        normalized_mac = format_mac(user_input[CONF_MAC_ADDRESS])
        entry_data = {
            CONF_HOST: user_input[CONF_HOST],
            CONF_MONITOR_ID: user_input[CONF_MONITOR_ID],
            CONF_MAC_ADDRESS: normalized_mac,
        }

        client = SicpDisplayClient(entry_data)
        try:
            data = await hass.async_add_executor_job(client.fetch_status)
        except NetworkError as exc:
            raise CannotConnect from exc
        except Exception as exc:  # noqa: BLE001
            raise InvalidResponse(str(exc)) from exc

        serial = data.serial_number or normalized_mac
        title = data.model_info.get("model_number") if data.model_info else None
        title = title or f"Philips Display {user_input[CONF_MONITOR_ID]}"

        return {
            "title": title,
            "unique_id": normalized_mac,
            "data": entry_data | {"serial_number": serial},
        }
