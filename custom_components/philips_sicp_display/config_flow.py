"""Config flow for the Philips SICP display integration."""
from __future__ import annotations

import ipaddress
from typing import Any, Mapping

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

from .const import (
    CONF_BROADCAST_ADDRESS,
    CONF_MAC_ADDRESS,
    CONF_MONITOR_ID,
    DATA_COORDINATOR,
    DEFAULT_MONITOR_ID,
    DOMAIN,
)
from .coordinator import PhilipsSicpCoordinator, SicpDisplayClient
from .wol import default_broadcast_address


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidResponse(HomeAssistantError):
    """Error to indicate the device returned an unexpected payload."""

MAC_REGEX = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"

STEP_USER_DATA_SCHEMA = vol.Schema(
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
        vol.Optional(CONF_BROADCAST_ADDRESS): cv.string,
    }
)

class PhilipsSicpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure new SICP displays."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        description_placeholders: dict[str, str] | None = None
        info: dict | None = None

        if user_input is not None:
            (
                user_input,
                errors,
                description_placeholders,
                info,
            ) = await self._async_validate_form(user_input)

            if not errors and info is not None:
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=info["data"])

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(STEP_USER_DATA_SCHEMA, user_input or {}),
            errors=errors,
            description_placeholders=description_placeholders,
        )

    async def async_step_reconfigure(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of an existing entry."""
        entry = self._get_reconfigure_entry()
        # The entry may not be loaded (or may have failed to set up), in which
        # case there is no coordinator to serialize against.
        coordinator: PhilipsSicpCoordinator | None = (
            self.hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get(DATA_COORDINATOR)
        )
        errors: dict[str, str] = {}
        description_placeholders: dict[str, str] | None = None
        info: dict | None = None

        if user_input is not None:
            (
                user_input,
                errors,
                description_placeholders,
                info,
            ) = await self._async_validate_form(
                user_input,
                existing=entry.data,
                coordinator=coordinator,
            )

            if not errors and info is not None:
                # The unique id is the normalized MAC: pointing the entry at a
                # different display must not silently hijack it.
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_mismatch()
                return self.async_update_reload_and_abort(
                    entry,
                    # data_updates merges, so keys the form does not cover
                    # (serial_number, anything added later) survive the update.
                    # Aborts with "reconfigure_successful" and reloads the entry.
                    data_updates=info["data"],
                )

        # Pre-fill with what is configured today, falling back to what the user
        # just typed so a validation error does not discard their edits.
        if user_input is None:
            suggested = dict(entry.data)
            # The stored broadcast is always concrete, even when the user left
            # the field blank to mean "derive it". Show it blank again in that
            # case, so changing the host to another subnet re-derives instead
            # of silently keeping the old subnet's broadcast address.
            stored_broadcast = suggested.get(CONF_BROADCAST_ADDRESS)
            if stored_broadcast and stored_broadcast == default_broadcast_address(
                entry.data.get(CONF_HOST, "")
            ):
                suggested.pop(CONF_BROADCAST_ADDRESS)
        else:
            suggested = user_input

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(STEP_USER_DATA_SCHEMA, suggested),
            errors=errors,
            description_placeholders=description_placeholders,
        )

    async def _async_validate_form(
        self,
        user_input: dict,
        existing: Mapping[str, Any] | None = None,
        coordinator: PhilipsSicpCoordinator | None = None,
    ) -> tuple[dict, dict[str, str], dict[str, str] | None, dict | None]:
        """Normalize and validate submitted form values.

        Returns the normalized input (suitable for re-seeding the form), the
        field errors, optional description placeholders and, when everything
        checks out, the validated entry info.
        """
        errors: dict[str, str] = {}
        description_placeholders: dict[str, str] | None = None
        info: dict | None = None

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

        # Blank means "same subnet as the display", the common case.
        broadcast = (user_input.get(CONF_BROADCAST_ADDRESS) or "").strip()
        broadcast = broadcast or default_broadcast_address(
            user_input[CONF_HOST]
        )
        user_input[CONF_BROADCAST_ADDRESS] = broadcast
        try:
            ipaddress.IPv4Address(broadcast)
        except ValueError:
            errors[CONF_BROADCAST_ADDRESS] = "invalid_broadcast_address"

        if not errors:
            try:
                info = await self._async_validate_input(
                    self.hass,
                    user_input,
                    existing=existing,
                    coordinator=coordinator,
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidResponse as err:
                errors["base"] = "setup_error"
                detail = str(err) or "See logs for details"
                description_placeholders = {"error_detail": detail}
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"

        return user_input, errors, description_placeholders, info

    async def _async_validate_input(
        self,
        hass: HomeAssistant,
        user_input: dict,
        existing: Mapping[str, Any] | None = None,
        coordinator: PhilipsSicpCoordinator | None = None,
    ) -> dict:
        """Validate the user input allows us to connect.

        ``existing`` is the entry data being reconfigured, if any: it keeps a
        previously discovered serial number when the display cannot be reached
        right now. ``coordinator`` is the running coordinator for that entry,
        used only to borrow its lock — SICP displays accept a single connection
        at a time, so validation must not run alongside a poll.
        """
        normalized_mac = format_mac(user_input[CONF_MAC_ADDRESS])
        entry_data = {
            CONF_HOST: user_input[CONF_HOST],
            CONF_MONITOR_ID: user_input[CONF_MONITOR_ID],
            CONF_MAC_ADDRESS: normalized_mac,
            CONF_BROADCAST_ADDRESS: user_input.get(CONF_BROADCAST_ADDRESS)
            or default_broadcast_address(user_input[CONF_HOST]),
        }

        # Always validate against the freshly submitted target: reconfigure may
        # be pointing the entry at a different host than the coordinator's own
        # client knows about.
        client = SicpDisplayClient(entry_data)
        try:
            if coordinator is not None:
                identity = await coordinator.async_call_client(client.fetch_identity)
            else:
                identity = await client.fetch_identity()
        except NetworkError as exc:
            raise CannotConnect from exc
        except Exception as exc:  # noqa: BLE001
            raise InvalidResponse(str(exc)) from exc

        # An unreachable display must not block reconfiguration (the panels are
        # typically off, waiting for Wake-on-LAN), so fall back to what we
        # already know before finally settling on the MAC.
        serial = (
            identity.serial_number
            or (existing or {}).get("serial_number")
            or normalized_mac
        )
        title = identity.model_number or f"Philips Display {user_input[CONF_MONITOR_ID]}"

        return {
            "title": title,
            "unique_id": normalized_mac,
            "data": entry_data | {"serial_number": serial},
        }
