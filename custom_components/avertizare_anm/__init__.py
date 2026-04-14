import logging
import xml.etree.ElementTree as ET
import re
import html
import asyncio
import aiohttp
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, CONF_COUNTY, URL

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

def parse_xml(xml_string, county):
    try:
        root = ET.fromstring(xml_string)
        severity = {"rosu": 3, "portocaliu": 2, "galben": 1, "inactiv": 0}
        
        current_alert = {"stare": "inactiv", "avertizari": []}
        max_sev = 0

        for avertizare in root.findall('avertizare'):
            judete = avertizare.findall('judet')
            is_affected = any(j.get('cod') == county for j in judete)

            if is_affected:
                culoare = avertizare.get('numeCuloare', 'inactiv').lower()
                sev = severity.get(culoare, 0)
                
                if sev > max_sev:
                    max_sev = sev
                    current_alert['stare'] = culoare
                    
                raw_mesaj = avertizare.get('mesaj', '')
                
                clean_mesaj = re.sub(r'<\s*br\s*/?\s*>|<\s*/\s*p\s*>', '\n', raw_mesaj, flags=re.IGNORECASE)
                clean_mesaj = re.sub(r'<[^>]+>', ' ', clean_mesaj)
                clean_mesaj = html.unescape(clean_mesaj)
                clean_mesaj = re.sub(r'[^\S\n]+', ' ', clean_mesaj)
                clean_mesaj = re.sub(r'\n\s*\n+', '\n', clean_mesaj).strip()

                current_alert['avertizari'].append({
                    "stare": culoare,
                    "dataAparitiei": avertizare.get('dataAparitiei'),
                    "dataExpirarii": avertizare.get('dataExpirarii'),
                    "fenomeneVizate": avertizare.get('fenomeneVizate'),
                    "mesaj": clean_mesaj
                })
                    
        return current_alert
    except ET.ParseError as e:
        _LOGGER.error(f"Eroare la parsarea XML-ului ANM: {e}")
        return {"stare": "inactiv", "avertizari": []}

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    county = entry.data[CONF_COUNTY]
    scan_interval = entry.options.get("scan_interval", 15)
    session = async_get_clientsession(hass)

    async def async_update_data():
        try:
            async with asyncio.timeout(10):
                async with session.get(URL) as response:
                    response.raise_for_status()
                    text = await response.text()
                    return await hass.async_add_executor_job(parse_xml, text, county)
        except asyncio.TimeoutError:
            raise UpdateFailed("Timp expirat (timeout) la conectarea cu site-ul ANM.")
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Eroare de rețea la comunicarea cu ANM: {err}")
        except Exception as err:
            raise UpdateFailed(f"Eroare neașteptată la actualizarea datelor: {err}")

    coordinator = DataUpdateCoordinator(
        hass, _LOGGER, name=f"anm_{county}",
        update_method=async_update_data,
        update_interval=timedelta(minutes=scan_interval),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok