from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    county = entry.data["county"]
    async_add_entities([AnmBinarySensor(coordinator, county)])

class AnmBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, county):
        super().__init__(coordinator)
        self.county = county
        self._attr_name = f"Alerta ANM {county}"
        self.entity_id = f"binary_sensor.avertizare_anm_{county.lower()}"
        self._attr_unique_id = f"anm_binary_{county.lower()}"
        self._attr_device_class = BinarySensorDeviceClass.SAFETY

    @property
    def is_on(self):
        if self.coordinator.data:
            return self.coordinator.data.get("stare", "inactiv") != "inactiv"
        return False