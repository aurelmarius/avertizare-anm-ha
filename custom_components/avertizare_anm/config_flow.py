import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_COUNTY, COUNTIES

class AnmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            county_code = user_input[CONF_COUNTY]
            county_name = COUNTIES[county_code]
            
            await self.async_set_unique_id(county_code)
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=f"Avertizare ANM {county_name}",
                data=user_input
            )

        data_schema = vol.Schema({
            vol.Required(CONF_COUNTY): vol.In(COUNTIES)
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AnmOptionsFlowHandler(config_entry)

class AnmOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Optional("scan_interval", default=self._config_entry.options.get("scan_interval", 15)): vol.All(vol.Coerce(int), vol.Range(min=1, max=120))
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))