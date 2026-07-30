from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_API_KEY, CONF_HOST, CONF_INSTANCE_UUID, CONF_REMOTE_UUID, DOMAIN

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_API_KEY): str,
        vol.Required(CONF_REMOTE_UUID): str,
        vol.Required(CONF_INSTANCE_UUID): str,
    }
)


class MCSManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_REMOTE_UUID]}_{user_input[CONF_INSTANCE_UUID]}"
            )
            self._abort_if_unique_id_configured()

            try:
                session = async_get_clientsession(self.hass)
                url = (
                    f"{user_input[CONF_HOST].rstrip('/')}/api/protected_instance/detail"
                    f"?apikey={user_input[CONF_API_KEY]}"
                    f"&remote_uuid={user_input[CONF_REMOTE_UUID]}"
                    f"&uuid={user_input[CONF_INSTANCE_UUID]}"
                )
                async with session.get(url, timeout=10) as resp:
                    if resp.status != 200:
                        errors["base"] = "cannot_connect"
                    else:
                        data = await resp.json()
                        if not isinstance(data, dict) or "data" not in data:
                            errors["base"] = "invalid_response"
            except Exception:
                errors["base"] = "cannot_connect"

            if not errors:
                return self.async_create_entry(
                    title=f"MCSManager {user_input[CONF_INSTANCE_UUID][:8]}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
