from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATUS_MAP
from .coordinator import MCSManagerCoordinator


@dataclass(frozen=True)
class MCSManagerSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict], Any] = lambda _: None


def _get_status(data: dict) -> str:
    return STATUS_MAP.get(int(data.get("status", 0)), "Unknown")


def _get_cpu(data: dict) -> float | None:
    val = data.get("info", {}).get("cpu")
    return round(float(val), 1) if val is not None else None


def _get_mem(data: dict) -> float | None:
    val = data.get("info", {}).get("mem")
    return round(float(val) / 1024, 2) if val is not None else None


def _get_players_current(data: dict) -> int | None:
    val = data.get("info", {}).get("players", {}).get("current")
    return int(val) if val is not None else None


def _get_players_max(data: dict) -> int | None:
    val = data.get("info", {}).get("players", {}).get("max")
    return int(val) if val is not None else None


SENSOR_DESCRIPTIONS: tuple[MCSManagerSensorDescription, ...] = (
    MCSManagerSensorDescription(
        key="status",
        name="Status",
        icon="mdi:server",
        value_fn=_get_status,
    ),
    MCSManagerSensorDescription(
        key="cpu",
        name="CPU Usage",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cpu-64-bit",
        value_fn=_get_cpu,
    ),
    MCSManagerSensorDescription(
        key="mem",
        name="Memory Usage",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:memory",
        value_fn=_get_mem,
    ),
    MCSManagerSensorDescription(
        key="players_current",
        name="Players Online",
        icon="mdi:account-group",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_get_players_current,
    ),
    MCSManagerSensorDescription(
        key="players_max",
        name="Players Max",
        icon="mdi:account-group-outline",
        value_fn=_get_players_max,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: MCSManagerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        MCSManagerSensor(coordinator, entry, desc) for desc in SENSOR_DESCRIPTIONS
    )


class MCSManagerSensor(CoordinatorEntity[MCSManagerCoordinator], SensorEntity):
    _attr_has_entity_name = True
    entity_description: MCSManagerSensorDescription

    def __init__(
        self,
        coordinator: MCSManagerCoordinator,
        entry: ConfigEntry,
        description: MCSManagerSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"MCSManager {coordinator.instance_uuid[:8]}",
            manufacturer="MCSManager",
            model="Game Server",
        )

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
