"""Sensor entities for the Philips SICP display integration."""
from __future__ import annotations

from collections.abc import Mapping

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from sicppy.messages import PowerState

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import PhilipsSicpCoordinator
from .entity import PhilipsSicpEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Philips SICP sensors from a config entry."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PhilipsSicpCoordinator = entry_data[DATA_COORDINATOR]

    entities: list[PhilipsSicpSensorEntity] = [
        PhilipsSicpTemperatureSensor(coordinator, entry),
        PhilipsFirmwareVersionSensor(coordinator, entry),
        # PhilipsSicpSerialNumberSensor(coordinator, entry),
        PhilipsSicpSicpInfoSensor(coordinator, entry),
        PhilipsSicpPowerStateSensor(coordinator, entry),
    ]

    async_add_entities(entities)


class PhilipsSicpSensorEntity(PhilipsSicpEntity, SensorEntity):
    """Shared base class for sensors."""


class PhilipsSicpTemperatureSensor(PhilipsSicpSensorEntity):
    """Primary temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "temperature")

    @property
    def extra_state_attributes(self) -> Mapping[str, list[int]] | None:
        data = self.coordinator.data
        temps = data.temperatures if data else None
        if not temps:
            return None
        return {"temperature_sensors": temps}

    @property
    def native_value(self) -> int | None:
        data = self.coordinator.data
        temps = data.temperatures if data else None
        if not temps or len(temps) == 0:
            return None
        return temps[0]


class PhilipsFirmwareVersionSensor(PhilipsSicpSensorEntity):
    """Sensor exposing model information."""

    _attr_icon = "mdi:label"

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "model_info")

    @property
    def extra_state_attributes(self) -> Mapping[str, str] | None:
        data = self.coordinator.data
        model_info = data.model_info if data else None
        if not model_info:
            return None
        return model_info

    @property
    def native_value(self) -> str | None:
        data = self.coordinator.data
        model_info = data.model_info if data else None
        if not model_info:
            return None
        return model_info.get("firmware_version")

class PhilipsSicpSicpInfoSensor(PhilipsSicpSensorEntity):
    """Sensor exposing the SICP firmware information."""

    _attr_icon = "mdi:information"

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "sicp_info")

    @property
    def extra_state_attributes(self) -> Mapping[str, str] | None:
        data = self.coordinator.data
        sicp_info = data.sicp_info if data else None
        if not sicp_info:
            return None
        return sicp_info

    @property
    def native_value(self) -> str | None:
        data = self.coordinator.data
        sicp_info = data.sicp_info if data else None
        if not sicp_info:
            return None
        return sicp_info.get("platform_version")


class PhilipsSicpPowerStateSensor(PhilipsSicpSensorEntity):
    """Sensor exposing the tri-state power status (offline/off/on)."""

    _attr_icon = "mdi:power"

    def __init__(self, coordinator: PhilipsSicpCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "power_state")

    @property
    def native_value(self) -> str:
        data = self.coordinator.data
        if not data or not data.power_state:
            return "offline"
        return "on" if data.power_state == PowerState.POWER_ON else "off"