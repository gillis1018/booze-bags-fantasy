"""Check what years of league history are available."""
from espn_api.football import League

LEAGUE_ID = 335765
SWID = "{BEAF1BB3-8FF6-4D3F-AF1B-B38FF64D3F97}"
ESPN_S2 = "AECISC2k7PschLKHD0K6p0jYPhyogh86Qqjf5wHjMF4XaXd0zZE%2Fz%2Fp94XnUBLNw4e06NIsBa%2Be0o2p%2FeGjSWlMXU9V%2BvJY9Jb3PXqfC0fSTChVtTJ8XWIpCRfrNpigSrw7lA9RCVw3FrNK3bZMER2hpANt7kR9NqqrWFFgvNfa1QAPZn6TLFVI2Sgp9hmLDVvZ0GnvEsVw3PuDsspj5DZJH2xy6wfxIbuYSjJE%2FLDAoVx6mZpa9FSRitY%2FVl6Jk2%2FWceAJtz7yQoK2c61gCl8MmQ5TvG3vxwq0LAsnHdcnJEdAsVPb5vedr5r1J4X5xYBBicyUOKHVxqsY2ks1xd8IcUboFJH%2FnTTlAojdh%2BISs9UIPzA9FX%2FplPLxmtPFEurnFJz7S1nVi1CQ7qlNtosHKgwECGOJhtinOAJ2ln1v%2Bf%2FC9Vs0LgiGofhAB%2BIdh5fXhWsMnyuYD5wJHKcxVls74wclxjSodXwkfoRazXwYKsoCOrQWgswVtubjf8sLQAeBfwb5q5u89BOh2y%2BCGbD%2BQ"

print("Checking available years...\n")

available_years = []
for year in range(2015, 2026):
    try:
        league = League(league_id=LEAGUE_ID, year=year, espn_s2=ESPN_S2, swid=SWID)
        available_years.append(year)
        print(f"  {year}: Found - {league.settings.name} ({len(league.teams)} teams)")
    except Exception as e:
        print(f"  {year}: Not available")

print(f"\n=== Available Years: {available_years} ===")
print(f"Total seasons: {len(available_years)}")
