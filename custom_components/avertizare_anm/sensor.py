from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    county = entry.data["county"]
    async_add_entities([AnmSensor(coordinator, county)])


class AnmSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, county):
        super().__init__(coordinator)
        self.county = county
        self._attr_name = f"Avertizare ANM {county}"
        
        self.entity_id = f"sensor.avertizare_anm_{county.lower()}"
        self._attr_unique_id = f"anm_{county.lower()}"
        self._attr_icon = "mdi:alert"

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data.get("stare", "inactiv")
        return "inactiv"

    @property
    def extra_state_attributes(self):
        if self.coordinator.data:
            return {"avertizari": self.coordinator.data.get("avertizari", [])}
        return {"avertizari": []}