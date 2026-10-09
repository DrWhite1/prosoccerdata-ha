import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_ATTENDANCE,
    ATTR_COMPETITION,
    ATTR_HOME_AWAY,
    ATTR_LOCATION,
    ATTR_MATCH_END,
    ATTR_MATCH_START,
    ATTR_MEETING_HOUR,
    ATTR_OPPONENT,
    ATTR_RECENT_MATCHES,
    ATTR_SCORE,
    ATTR_TEAM,
    DOMAIN,
)
from .coordinator import ProSoccerDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ProSoccerDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(ProSoccerDataSensor(coordinator, player) for player in coordinator.players)


def _location(value: Any) -> str:
    if isinstance(value, dict):
        return value.get("fullAddress") or value.get("name") or ""
    return value or ""


def _team_filters(raw: str) -> list[str]:
    return [part.strip().lower() for part in (raw or "").split(",") if part.strip()]


def _upcoming(schedule: list[dict], team_filter: str, home_field: str) -> list[dict]:
    filters = _team_filters(team_filter)
    home = (home_field or "").strip().lower()
    items = []
    for item in schedule:
        if item.get("cancelled"):
            continue
        title = item.get("fullTitle") or item.get("title") or ""
        raw_type = str(item.get("eventType") or item.get("type") or item.get("subtype") or "")
        blob = f"{raw_type} {title}".lower()
        if "kantine" in blob:
            continue
        start = item.get("start") or ""
        team = item.get("teamNames") or ""
        location = _location(item.get("location"))
        row = {
            "kind": "training" if "train" in blob or "groepstraining" in blob else "match",
            "start": start,
            "date": start[:10],
            "team": team,
            "opponent": title,
            "home_away": item.get("subtype") or "",
            "competition": item.get("competitionType") or "",
            "location": location,
            "other_field": bool(home and location and home not in location.lower()),
            "meeting_hour": item.get("meetingHour") or "",
        }
        haystack = f"{team} {title}".lower()
        if filters and not any(team_name in haystack for team_name in filters):
            continue
        items.append(row)
    items.sort(key=lambda row: row.get("start") or "")
    return items[:12]


class ProSoccerDataSensor(CoordinatorEntity, SensorEntity):
    """One sensor per tracked player."""

    _attr_icon = "mdi:soccer"

    def __init__(self, coordinator: ProSoccerDataCoordinator, player: dict) -> None:
        super().__init__(coordinator)
        self._player = player
        member_id = player["platformMemberId"]
        first = player.get("platformUserFirstName") or player.get("platformMemberFirstName", "?")
        last = player.get("platformUserLastName") or player.get("platformMemberLastName", "?")
        club = player.get("platform", "ProSoccerData")
        self._attr_unique_id = f"prosoccerdata_{member_id}_last_match"
        self._attr_name = f"{first} {last} – Last Match"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(member_id))},
            name=f"{first} {last}",
            manufacturer="ProSoccerData",
            model=club,
            configuration_url=player.get("platformURL"),
        )

    @property
    def _player_data(self) -> dict | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(str(self._player["platformMemberId"]))

    def _calendar(self) -> list[dict]:
        data = self._player_data
        if not data:
            return []
        return _upcoming(
            data.get("schedule") or [],
            self.coordinator.team_filter,
            self.coordinator.home_field,
        )

    @property
    def native_value(self) -> str | None:
        upcoming = self._calendar()
        if upcoming:
            return upcoming[0].get("date")
        data = self._player_data
        if data and data.get("last_match"):
            return data["last_match"].get("date")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self._player_data
        if not data:
            return {}
        last = data.get("last_match") or {}
        recent = data.get("matches", [])
        recent_summary = [
            {
                "date": m.get("date"),
                "opponent": m.get("opponent"),
                "score": m.get("score"),
                "home_away": m.get("home_away"),
                "competition": m.get("competition"),
                "cancelled": m.get("cancelled"),
            }
            for m in recent[:10]
        ]
        upcoming = self._calendar()
        return {
            ATTR_MATCH_START: last.get("start"),
            ATTR_MATCH_END: last.get("end"),
            ATTR_TEAM: last.get("team"),
            ATTR_OPPONENT: last.get("opponent"),
            ATTR_SCORE: last.get("score"),
            ATTR_HOME_AWAY: last.get("home_away"),
            ATTR_COMPETITION: last.get("competition"),
            ATTR_LOCATION: last.get("location"),
            ATTR_MEETING_HOUR: last.get("meeting_hour"),
            ATTR_ATTENDANCE: last.get("attendance"),
            "full_title": last.get("full_title"),
            "team_filter": self.coordinator.team_filter,
            "home_field": self.coordinator.home_field,
            ATTR_RECENT_MATCHES: recent_summary,
            "next_event": upcoming[0] if upcoming else None,
            "upcoming": upcoming,
        }
