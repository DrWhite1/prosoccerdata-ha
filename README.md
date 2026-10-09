[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/hyronimous)

# ProSoccerData for Home Assistant

Track a child's matches and trainings from [app.prosoccerdata.com](https://app.prosoccerdata.com). The club host comes from the account. The team is an option, so the same install works for any club.


## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=DrWhite1&repository=prosoccerdata-ha&category=Integration)

1. Add this GitHub repository to HACS as a custom repository, or click the button above.
2. Install ProSoccerData via HACS.
3. Restart Home Assistant.
4. Settings → Devices & services → Add integration → ProSoccerData.
5. Log in with the parent account and pick the player.
6. Open the integration and choose Configure. Set the team to the name as it appears on the club calendar, for example `U12 Teamname`. Several teams can be comma separated. Set the usual field to a distinctive part of its address, for example `Sportlaan`.

A transfer is a change in that Configure screen, not a code edit.

If the button does not open your repository, the `owner` and `repository` in the link must match the GitHub page. HACS has to be installed first.

## Sensor

One sensor per player. The state is the date of the next event. Attributes:

| Attribute | Meaning |
| --- | --- |
| `next_event` | Next match or training after the team filter |
| `upcoming` | Up to 12 coming events |
| `team_filter` | The configured teams |
| `other_field` | On each upcoming row, true when the location does not contain the usual field |
| `recent_matches` | Last played matches |

`upcoming` rows have `kind` (`match` or `training`), `start`, `date`, `team`, `opponent`, `home_away`, `location` and `other_field`.

## Card

Replace `sensor.player_last_match` with the entity created for the connected player. Home Assistant builds it from the player name on the account, lowercased, ending in `_last_match`. Requires [card-mod](https://github.com/thomasloven/lovelace-card-mod). A training on another pitch shows the street name because `other_field` is set from the home-field option.

```yaml
type: markdown
entity_id: sensor.player_last_match
content: |
  {% set s = 'sensor.player_last_match' %}
  {% set rows = state_attr(s, 'upcoming') or [] %}
  {% set ordered = rows | sort(attribute='start') %}
  {% set n = ordered[0] if ordered else none %}
  {% if n %}
  <p class="kicker">Volgende · {{ 'training' if n.kind == 'training' else 'wedstrijd' }}</p>
  <p class="when">{{ n.date[8:10] }}/{{ n.date[5:7] }} · {{ n.start[11:16] }}</p>
  <p class="title">{{ n.opponent }}</p>
  {% if n.location %}<p class="where">{{ n.location }}</p>{% endif %}
  {% endif %}
  {% for m in ordered %}
  - {{ '⚽' if m.kind != 'training' else '🏃' }} {{ m.date[8:10] }}/{{ m.date[5:7] }} {{ m.start[11:16] }} · {{ 'thuis' if m.home_away == 'home' else 'uit' if m.kind != 'training' else 'training' }} · {{ m.opponent }}{% if m.other_field %} · {{ m.location.split(',')[0] }}{% endif %}
  {% endfor %}
card_mod:
  style: |
    ha-card { background: #1A2420; color: #F4F1EA; border: none; border-radius: 18px; }
    ha-markdown { padding: 14px 16px 10px; }
    .kicker { margin: 0; color: #8FB3A6; letter-spacing: 0.14em; text-transform: uppercase; font-size: 11px; }
    .when { margin: 6px 0 0; font-size: 28px; font-weight: 650; letter-spacing: -0.03em; }
    .title { margin: 4px 0 0; font-size: 16px; }
    .where { margin: 2px 0 12px; color: #C9D4CE; font-size: 13px; }
    ul { list-style: none; margin: 8px 0 0; padding: 0; border-top: 1px solid #2C3A34; }
    li { margin: 0; padding: 9px 0; border-bottom: 1px solid #2C3A34; color: #E7F0EC; font-size: 13px; }
    li::marker { content: none; }
```

If you find this useful, you can [buy me a coffee](https://ko-fi.com/hyronimous).
