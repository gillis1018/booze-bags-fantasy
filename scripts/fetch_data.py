"""Fetch all historical data from ESPN Fantasy Football API."""
import json
import os
from datetime import datetime
from espn_api.football import League
from config import LEAGUE_ID, SWID, ESPN_S2, YEARS, DATA_DIR

def get_owner_name(team):
    """Extract owner name from team object."""
    if team.owners:
        owner = team.owners[0]
        first = owner.get('firstName', '').strip()
        last = owner.get('lastName', '').strip()
        # Normalize whitespace - replace multiple spaces with single space
        name = f"{first} {last}".strip()
        return ' '.join(name.split())
    return "Unknown"

def fetch_season_data(year):
    """Fetch all data for a single season."""
    print(f"  Fetching {year}...")

    try:
        league = League(league_id=LEAGUE_ID, year=year, espn_s2=ESPN_S2, swid=SWID)
    except Exception as e:
        print(f"    Error: {e}")
        return None

    season = {
        "year": year,
        "league_name": league.settings.name,
        "teams": [],
        "standings": [],
        "matchups": [],
        "playoffs": [],
        "draft": [],
        "trades": []
    }

    # Teams and standings
    for team in sorted(league.teams, key=lambda t: t.final_standing if t.final_standing else 99):
        team_data = {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "owner": get_owner_name(team),
            "wins": team.wins,
            "losses": team.losses,
            "ties": getattr(team, 'ties', 0),
            "points_for": round(team.points_for, 2),
            "points_against": round(team.points_against, 2),
            "final_standing": team.final_standing,
            "playoff_seed": getattr(team, 'playoff_seed', None)
        }
        season["teams"].append(team_data)
        season["standings"].append({
            "rank": team.final_standing,
            "team_name": team.team_name,
            "owner": get_owner_name(team),
            "record": f"{team.wins}-{team.losses}" + (f"-{team.ties}" if getattr(team, 'ties', 0) > 0 else ""),
            "points_for": round(team.points_for, 2)
        })

    # Regular season matchups
    try:
        for week in range(1, 18):  # NFL regular season weeks
            try:
                box_scores = league.box_scores(week)
                for matchup in box_scores:
                    if matchup.home_team and matchup.away_team:
                        season["matchups"].append({
                            "week": week,
                            "home_team": matchup.home_team.team_name,
                            "home_score": round(matchup.home_score, 2),
                            "away_team": matchup.away_team.team_name,
                            "away_score": round(matchup.away_score, 2),
                            "is_playoff": week > 14  # Typical playoff start
                        })
            except:
                pass  # Week might not exist
    except Exception as e:
        print(f"    Warning: Could not fetch matchups - {e}")

    # Draft picks
    try:
        if hasattr(league, 'draft') and league.draft:
            for pick in league.draft:
                season["draft"].append({
                    "round": pick.round_num,
                    "pick": pick.round_pick,
                    "overall": (pick.round_num - 1) * len(league.teams) + pick.round_pick,
                    "team": pick.team.team_name if pick.team else "Unknown",
                    "player": pick.playerName if hasattr(pick, 'playerName') else str(pick.playerId)
                })
    except Exception as e:
        print(f"    Warning: Could not fetch draft - {e}")

    # Trades (recent activity)
    try:
        activities = league.recent_activity(size=100)
        for activity in activities:
            if hasattr(activity, 'actions') and 'TRADED' in str(activity.actions):
                season["trades"].append({
                    "date": str(activity.date) if hasattr(activity, 'date') else "Unknown",
                    "details": str(activity.actions)
                })
    except Exception as e:
        print(f"    Warning: Could not fetch trades - {e}")

    return season

def calculate_all_time_records(all_seasons):
    """Calculate all-time records across all seasons."""
    owners = {}

    for season in all_seasons:
        for team in season["teams"]:
            owner = team["owner"]
            if owner not in owners:
                owners[owner] = {
                    "owner": owner,
                    "seasons": 0,
                    "wins": 0,
                    "losses": 0,
                    "ties": 0,
                    "points_for": 0,
                    "points_against": 0,
                    "championships": 0,
                    "playoff_appearances": 0,
                    "best_finish": 99,
                    "teams": []
                }

            owners[owner]["seasons"] += 1
            owners[owner]["wins"] += team["wins"]
            owners[owner]["losses"] += team["losses"]
            owners[owner]["ties"] += team.get("ties", 0)
            owners[owner]["points_for"] += team["points_for"]
            owners[owner]["points_against"] += team["points_against"]
            owners[owner]["teams"].append({
                "year": season["year"],
                "team_name": team["team_name"],
                "record": f"{team['wins']}-{team['losses']}",
                "standing": team["final_standing"]
            })

            if team["final_standing"] == 1:
                owners[owner]["championships"] += 1
            if team["final_standing"] and team["final_standing"] <= 6:  # Top 6 make playoffs typically
                owners[owner]["playoff_appearances"] += 1
            if team["final_standing"] and team["final_standing"] < owners[owner]["best_finish"]:
                owners[owner]["best_finish"] = team["final_standing"]

    # Sort by wins
    all_time = sorted(owners.values(), key=lambda x: x["wins"], reverse=True)

    # Round points
    for owner in all_time:
        owner["points_for"] = round(owner["points_for"], 2)
        owner["points_against"] = round(owner["points_against"], 2)
        owner["win_pct"] = round(owner["wins"] / (owner["wins"] + owner["losses"]) * 100, 1) if (owner["wins"] + owner["losses"]) > 0 else 0

    return all_time

def get_championship_history(all_seasons):
    """Extract championship history."""
    champions = []
    for season in all_seasons:
        for team in season["teams"]:
            if team["final_standing"] == 1:
                champions.append({
                    "year": season["year"],
                    "team_name": team["team_name"],
                    "owner": team["owner"],
                    "record": f"{team['wins']}-{team['losses']}",
                    "points_for": team["points_for"]
                })
                break
    return champions

def main():
    """Main function to fetch all data and save to JSON files."""
    os.makedirs(DATA_DIR, exist_ok=True)

    print("Fetching Booze Bags Fantasy League historical data...\n")

    all_seasons = []
    for year in YEARS:
        season_data = fetch_season_data(year)
        if season_data:
            all_seasons.append(season_data)

            # Save individual season file
            with open(f"{DATA_DIR}/season_{year}.json", "w") as f:
                json.dump(season_data, f, indent=2)

    print(f"\nProcessing {len(all_seasons)} seasons of data...")

    # Calculate aggregated data
    all_time_records = calculate_all_time_records(all_seasons)
    championship_history = get_championship_history(all_seasons)

    # Save aggregated data
    summary = {
        "league_name": "Booze Bags Fantasy League",
        "league_id": LEAGUE_ID,
        "years": [s["year"] for s in all_seasons],
        "total_seasons": len(all_seasons),
        "last_updated": datetime.now().isoformat(),
        "all_time_records": all_time_records,
        "championship_history": championship_history
    }

    with open(f"{DATA_DIR}/summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    with open(f"{DATA_DIR}/all_seasons.json", "w") as f:
        json.dump(all_seasons, f, indent=2)

    print(f"\n=== Data Export Complete ===")
    print(f"Seasons exported: {len(all_seasons)}")
    print(f"Files saved to: {os.path.abspath(DATA_DIR)}")
    print(f"\nChampionship History:")
    for champ in championship_history:
        print(f"  {champ['year']}: {champ['owner']} ({champ['team_name']})")

if __name__ == "__main__":
    main()
