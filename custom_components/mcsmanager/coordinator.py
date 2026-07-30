from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_INSTANCE_UUID,
    CONF_REMOTE_UUID,
    DOMAIN,
    SCAN_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


class MCSManagerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry_data: dict) -> None:
        self._host = entry_data[CONF_HOST].rstrip("/")
        self._api_key = entry_data[CONF_API_KEY]
        self._remote_uuid = entry_data[CONF_REMOTE_UUID]
        self._instance_uuid = entry_data[CONF_INSTANCE_UUID]
        self._session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )

    @property
    def instance_uuid(self) -> str:
        return self._instance_uuid

    def _build_url(self, endpoint: str) -> str:
        return (
            f"{self._host}/api/protected_instance/{endpoint}"
            f"?apikey={self._api_key}"
            f"&remote_uuid={self._remote_uuid}"
            f"&uuid={self._instance_uuid}"
        )

    async def _async_update_data(self) -> dict:
        try:
            async with self._session.get(
                self._build_url("detail"), timeout=10
            ) as resp:
                resp.raise_for_status()
                payload = await resp.json()
        except Exception as err:
            raise UpdateFailed(f"MCSManager API error: {err}") from err

        data = payload.get("data", {})
        if not data:
            raise UpdateFailed("Empty data in MCSManager response")
        return data

    async def async_start_instance(self) -> None:
        async with self._session.get(self._build_url("open"), timeout=10) as resp:
            resp.raise_for_status()

    async def async_stop_instance(self) -> None:
        async with self._session.get(self._build_url("stop"), timeout=10) as resp:
            resp.raise_for_status()
