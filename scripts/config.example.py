"""Configuration template for ESPN Fantasy Football data fetcher.

Copy this file to config.py and fill in your credentials.
DO NOT commit config.py to git - it contains sensitive data.
"""

LEAGUE_ID = 0  # Your ESPN league ID
SWID = ""  # Your ESPN SWID cookie
ESPN_S2 = ""  # Your ESPN espn_s2 cookie

# Years the league has been active
YEARS = list(range(2015, 2026))

# Output directory for JSON data
DATA_DIR = "../data"
