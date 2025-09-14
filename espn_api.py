#!/usr/bin/env python3
"""
ESPN API integration for fetching NFL game results and injury data.
This provides free access to game scores and player injury information.
"""
import datetime as dt
import requests
from typing import Dict, List, Optional, Tuple
import json

class ESPNAPI:
    """ESPN API client for NFL data"""
    
    def __init__(self):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        self.timeout = 30
    
    def get_week_results(self, year: int, week: int) -> List[Dict]:
        """
        Get game results for a specific NFL week.
        
        Args:
            year: NFL season year (e.g., 2025)
            week: Week number (1-18)
            
        Returns:
            List of game results with scores and team info
        """
        # ESPN uses different date ranges for each week
        # We'll fetch the scoreboard for the week
        url = f"{self.base_url}/scoreboard"
        
        # Calculate the date range for the week
        week_dates = self._get_week_date_range(year, week)
        
        params = {
            "dates": f"{week_dates['start']}-{week_dates['end']}",
            "limit": 1000
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            games = []
            for event in data.get("events", []):
                game_result = self._parse_game_result(event)
                if game_result:
                    games.append(game_result)
            
            return games
            
        except Exception as e:
            print(f"Error fetching Week {week} results: {e}")
            return []
    
    def get_team_injuries(self, team_id: Optional[str] = None) -> List[Dict]:
        """
        Get injury information for teams or specific team.
        
        Args:
            team_id: Optional specific team ID, if None gets all teams
            
        Returns:
            List of injury reports
        """
        if team_id:
            url = f"{self.base_url}/teams/{team_id}/injuries"
        else:
            # Get all teams first, then injuries for each
            url = f"{self.base_url}/teams"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if team_id:
                return self._parse_injury_data(data)
            else:
                # Get injuries for all teams
                all_injuries = []
                for team in data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", []):
                    team_info = team.get("team", {})
                    team_id = team_info.get("id")
                    if team_id:
                        team_injuries = self.get_team_injuries(team_id)
                        for injury in team_injuries:
                            injury["team_id"] = team_id
                            injury["team_name"] = team_info.get("displayName")
                        all_injuries.extend(team_injuries)
                return all_injuries
                
        except Exception as e:
            print(f"Error fetching injury data: {e}")
            return []
    
    def get_current_week(self) -> int:
        """Get the current NFL week number"""
        try:
            url = f"{self.base_url}/scoreboard"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # ESPN provides week info in the response
            week_info = data.get("week", {})
            return week_info.get("number", 1)
            
        except Exception as e:
            print(f"Error getting current week: {e}")
            return 1
    
    def _get_week_date_range(self, year: int, week: int) -> Dict[str, str]:
        """
        Calculate the date range for a specific NFL week.
        This is approximate since NFL weeks vary.
        """
        # NFL season typically starts first Thursday of September
        # Week 1: First Thursday of September
        # Each week: Thursday to Monday
        
        if week == 1:
            # First Thursday of September
            start_date = dt.date(year, 9, 1)
            while start_date.weekday() != 3:  # Thursday
                start_date += dt.timedelta(days=1)
        else:
            # Subsequent weeks start 7 days after previous week
            week1_start = self._get_week_date_range(year, 1)["start"]
            start_date = dt.datetime.strptime(week1_start, "%Y%m%d").date()
            start_date += dt.timedelta(days=(week - 1) * 7)
        
        # Week runs Thursday to Monday (5 days)
        end_date = start_date + dt.timedelta(days=4)
        
        return {
            "start": start_date.strftime("%Y%m%d"),
            "end": end_date.strftime("%Y%m%d")
        }
    
    def _parse_game_result(self, event: Dict) -> Optional[Dict]:
        """Parse a single game result from ESPN API response"""
        try:
            game_id = event.get("id")
            date = event.get("date")
            
            competitions = event.get("competitions", [])
            if not competitions:
                return None
            
            comp = competitions[0]
            competitors = comp.get("competitors", [])
            
            if len(competitors) != 2:
                return None
            
            home_team = None
            away_team = None
            
            for competitor in competitors:
                team_info = competitor.get("team", {})
                team_data = {
                    "id": team_info.get("id"),
                    "name": team_info.get("displayName"),
                    "abbreviation": team_info.get("abbreviation"),
                    "score": competitor.get("score"),
                    "home_away": competitor.get("homeAway")
                }
                
                if team_data["home_away"] == "home":
                    home_team = team_data
                elif team_data["home_away"] == "away":
                    away_team = team_data
            
            if not home_team or not away_team:
                return None
            
            # Determine winner
            home_score = int(home_team["score"]) if home_team["score"] else 0
            away_score = int(away_team["score"]) if away_team["score"] else 0
            
            winner = home_team["name"] if home_score > away_score else away_team["name"]
            
            return {
                "game_id": game_id,
                "date": date,
                "home_team": home_team["name"],
                "away_team": away_team["name"],
                "home_score": home_score,
                "away_score": away_score,
                "winner": winner,
                "total_points": home_score + away_score,
                "home_abbreviation": home_team["abbreviation"],
                "away_abbreviation": away_team["abbreviation"]
            }
            
        except Exception as e:
            print(f"Error parsing game result: {e}")
            return None
    
    def _parse_injury_data(self, data: Dict) -> List[Dict]:
        """Parse injury data from ESPN API response"""
        injuries = []
        
        try:
            # ESPN injury data structure varies
            # This is a simplified parser - may need adjustment based on actual API response
            injury_items = data.get("items", [])
            
            for item in injury_items:
                injury = {
                    "player_name": item.get("athlete", {}).get("displayName"),
                    "position": item.get("athlete", {}).get("position", {}).get("displayName"),
                    "status": item.get("status"),
                    "injury_type": item.get("injury", {}).get("type"),
                    "injury_description": item.get("injury", {}).get("description"),
                    "date_updated": item.get("dateUpdated")
                }
                injuries.append(injury)
                
        except Exception as e:
            print(f"Error parsing injury data: {e}")
        
        return injuries

def test_espn_api():
    """Test the ESPN API integration"""
    api = ESPNAPI()
    
    print("Testing ESPN API...")
    
    # Test current week
    current_week = api.get_current_week()
    print(f"Current NFL week: {current_week}")
    
    # Test getting Week 1 results (if available)
    print("Fetching Week 1 results...")
    week1_results = api.get_week_results(2025, 1)
    print(f"Found {len(week1_results)} games for Week 1")
    
    if week1_results:
        print("Sample game result:")
        print(json.dumps(week1_results[0], indent=2))
    
    # Test injury data
    print("Fetching injury data...")
    injuries = api.get_team_injuries()
    print(f"Found {len(injuries)} injury reports")

if __name__ == "__main__":
    test_espn_api()
