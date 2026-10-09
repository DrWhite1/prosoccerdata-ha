from datetime import timedelta

DOMAIN = "prosoccerdata"

APP_URL = "https://app.prosoccerdata.com"
API_URL = "https://psd.prosoccerdata.com"

LOGIN_URL = f"{API_URL}/api/v2/login/oauth/token"
POSSIBLE_USERS_URL = f"{API_URL}/api/v2/central-users/current/possible-users"
CENTRAL_TOKEN_HEADER = "central-token"

CONF_PLAYERS = "players"
CONF_PLAYER_IDS = "player_ids"
CONF_TEAM_FILTER = "team_filter"
CONF_HOME_FIELD = "home_field"

SCAN_INTERVAL = timedelta(minutes=30)

ATTR_TEAM = "team"
ATTR_OPPONENT = "opponent"
ATTR_SCORE = "score"
ATTR_HOME_AWAY = "home_away"
ATTR_COMPETITION = "competition"
ATTR_LOCATION = "location"
ATTR_MEETING_HOUR = "meeting_hour"
ATTR_TEAM_LOGO = "team_logo_url"
ATTR_OPPONENT_LOGO = "opponent_logo_url"
ATTR_RECENT_MATCHES = "recent_matches"
ATTR_MATCH_START = "match_start"
ATTR_MATCH_END = "match_end"
ATTR_ATTENDANCE = "attendance_state"
