from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MCSManagerCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: MCSManagerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MCSManagerSwitch(coordinator, entry)])


class MCSManagerSwitch(CoordinatorEntity[MCSManagerCoordinator], SwitchEntity):
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_has_entity_name = True
    _attr_name = "Power"

    def __init__(self, coordinator: MCSManagerCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_power"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"MCSManager {coordinator.instance_uuid[:8]}",
            manufacturer="MCSManager",
            model="Game Server",
        )

    @property
    def is_on(self) -> bool:
        status = self.coordinator.data.get("status")
        return str(status) == "3"

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_start_instance()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_stop_instance()
        await self.coordinator.async_request_refresh()
