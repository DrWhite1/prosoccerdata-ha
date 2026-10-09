import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ProSoccerDataAPI
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ProSoccerDataCoordinator(DataUpdateCoordinator):
    """Fetch match data and the club calendar for all selected players."""

    team_filter: str = ""
    home_field: str = ""

    def __init__(self, hass: HomeAssistant, api: ProSoccerDataAPI, players: list[dict]) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.api = api
        self.players = players

    async def _async_update_data(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for player in self.players:
            member_id = player["platformMemberId"]
            name = (
                f"{player.get('platformUserFirstName') or player.get('platformMemberFirstName', '?')}"
                f" {player.get('platformUserLastName') or player.get('platformMemberLastName', '?')}"
            )
            try:
                raw_matches = await self.api.get_previous_matches(player)
                parsed = [self.api.parse_match(m) for m in raw_matches]
                schedule = await self.api.get_schedule(player)
                result[str(member_id)] = {
                    "player": player,
                    "matches": parsed,
                    "last_match": parsed[0] if parsed else None,
                    "schedule": schedule,
                }
                _LOGGER.debug(
                    "Fetched %d matches and %d calendar items for %s",
                    len(parsed),
                    len(schedule),
                    name,
                )
            except Exception as err:
                _LOGGER.error("Error fetching data for %s: %s", name, err)
                if str(member_id) not in result:
                    result[str(member_id)] = {
                        "player": player,
                        "matches": [],
                        "last_match": None,
                        "schedule": [],
                    }
        if not result:
            raise UpdateFailed("No data returned for any player")
        return result
