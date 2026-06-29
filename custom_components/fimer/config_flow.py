from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .api import FimerApi
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_PLANT_ID,
)


class FimerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow voor FIMER Aurora Vision."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            api = FimerApi(
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                user_input[CONF_PLANT_ID],
            )

            try:
                # Test de verbinding
                await self.hass.async_add_executor_job(api.generation_power)

                await self.async_set_unique_id(
                    user_input[CONF_PLANT_ID]
                )

                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"FIMER {user_input[CONF_PLANT_ID]}",
                    data=user_input,
                )

            except Exception:
                errors["base"] = "cannot_connect"

        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_PLANT_ID): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return FimerOptionsFlow(config_entry)


class FimerOptionsFlow(config_entries.OptionsFlow):

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return self.async_create_entry(title="", data={})