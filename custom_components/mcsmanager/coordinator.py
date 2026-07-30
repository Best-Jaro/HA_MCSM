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
    CONF_DAEMON_ID,
    DOMAIN,
    SCAN_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


class MCSManagerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry_data: dict) -> None:
        self._host = entry_data[CONF_HOST].rstrip("/")
        self._api_key = entry_data[CONF_API_KEY]
        self._daemon_id = entry_data[CONF_DAEMON_ID]
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

    def _base_params(self) -> str:
        return f"apikey={self._api_key}&daemonId={self._daemon_id}&uuid={self._instance_uuid}"

    async def _async_update_data(self) -> dict:
        # GET /api/instance/?daemonId=...&uuid=...&apikey=...
        url = f"{self._host}/api/instance/?{self._base_params()}"
        try:
            async with self._session.get(url, timeout=10) as resp:
                resp.raise_for_status()
                payload = await resp.json()
        except Exception as err:
            raise UpdateFailed(f"MCSManager API error: {err}") from err

        # Response: { status: 200, data: { instanceUuid, status, info: {...}, config: {...} } }
        data = payload.get("data") if isinstance(payload, dict) else None
        if not data:
            raise UpdateFailed(f"Empty or invalid MCSManager response: {payload}")
        return data

    async def async_start_instance(self) -> None:
        url = f"{self._host}/api/protected_instance/open?{self._base_params()}"
        async with self._session.get(url, timeout=10) as resp:
            resp.raise_for_status()

    async def async_stop_instance(self) -> None:
        url = f"{self._host}/api/protected_instance/stop?{self._base_params()}"
        async with self._session.get(url, timeout=10) as resp:
            resp.raise_for_status()
