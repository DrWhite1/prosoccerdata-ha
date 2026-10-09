import logging

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import ProSoccerDataAPI
from .const import CONF_HOME_FIELD, CONF_PLAYERS, CONF_TEAM_FILTER, DOMAIN
from .coordinator import ProSoccerDataCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_create_clientsession(hass, cookie_jar=aiohttp.DummyCookieJar())
    api = ProSoccerDataAPI(session, entry.data["email"], entry.data["password"])

    if not await api.login():
        _LOGGER.error("ProSoccerData login failed for %s", entry.data["email"])
        return False

    players = entry.data.get(CONF_PLAYERS, [])
    coordinator = ProSoccerDataCoordinator(hass, api, players)
    coordinator.team_filter = entry.options.get(CONF_TEAM_FILTER, "")
    coordinator.home_field = entry.options.get(CONF_HOME_FIELD, "")
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
