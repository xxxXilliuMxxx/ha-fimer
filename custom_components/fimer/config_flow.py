from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    CONF_PASSWORD,
    CONF_PLANT_ID,
    CONF_USERNAME,
    DOMAIN,
)


class FimerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):

        errors = {}

        if user_input is not None:

            return self.async_create_entry(
                title=f"Plant {user_input[CONF_PLANT_ID]}",
                data=user_input,
            )

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
