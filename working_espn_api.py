#!/usr/bin/env python3
"""
Working ESPN API integration based on actual endpoint testing.
This focuses on the endpoints that actually work and provide useful data.
"""
import requests
import json
from typing import Dict, List, Optional, Tuple
import datetime as dt

class WorkingESPNAPI:
    """ESPN API client using verified working endpoints"""
    
    def __init__(self):
        self.site_base = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        self.core_base = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl"
        self.timeout = 30
    
    def get_week_games_with_details(self, year: int, week: int) -> List[Dict]:
        """
        Get all games for a week with detailed information.
        
        Args:
            year: NFL season year
            week: Week number
            
        Returns:
            List of games with detailed information
        """
        print(f"📅 Getting Week {week} games with details...")
        
        # Get games from scoreboard
        games = self._get_week_games_from_scoreboard(year, week)
        
        detailed_games = []
        for game in games:
            game_id = game.get("id")
            if game_id:
                # Get detailed game information
                detailed_game = self.get_game_details(game_id)
                if detailed_game:
                    detailed_games.append(detailed_game)
        
        return detailed_games
    
    def get_game_details(self, game_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific game.
        
        Args:
            game_id: ESPN game ID
            
        Returns:
            Detailed game information
        """
        print(f"🎮 Getting details for game {game_id}...")
        
        # Get basic game info
        url = f"{self.core_base}/events/{game_id}"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            game_details = self._parse_game_details(data)
            
            # Get ESPN predictions if available
            predictions = self.get_espn_predictions(game_id)
            if predictions:
                game_details["espn_predictions"] = predictions
            
            # Get team injury data
            injuries = self.get_game_injuries(game_details.get("teams", {}))
            if injuries:
                game_details["injuries"] = injuries
            
            return game_details
            
        except Exception as e:
            print(f"❌ Error getting game details: {e}")
            return None
    
    def get_espn_predictions(self, game_id: str) -> Optional[Dict]:
        """Get ESPN's predictions for a game"""
        url = f"{self.core_base}/events/{game_id}/competitions/{game_id}/predictor"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_predictions(data)
            
        except Exception as e:
            print(f"❌ Error getting predictions: {e}")
            return None
    
    def get_game_injuries(self, teams: Dict) -> Dict:
        """Get injury data for teams in a game"""
        injuries = {}
        
        for team_type, team_info in teams.items():
            if isinstance(team_info, dict) and "id" in team_info:
                team_id = team_info["id"]
                team_injuries = self.get_team_injuries(team_id)
                if team_injuries:
                    injuries[team_type] = team_injuries
        
        return injuries
    
    def get_team_injuries(self, team_id: str) -> List[Dict]:
        """Get injury data for a specific team"""
        url = f"{self.core_base}/teams/{team_id}/injuries"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_injury_data(data)
            
        except Exception as e:
            print(f"❌ Error getting team injuries: {e}")
            return []
    
    def get_team_info(self, team_id: str) -> Optional[Dict]:
        """Get detailed team information"""
        url = f"{self.core_base}/teams/{team_id}"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_team_info(data)
            
        except Exception as e:
            print(f"❌ Error getting team info: {e}")
            return None
    
    def _get_week_games_from_scoreboard(self, year: int, week: int) -> List[Dict]:
        """Get basic game information from scoreboard"""
        url = f"{self.site_base}/scoreboard"
        
        # Calculate date range for the week
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
                game_data = self._parse_basic_game(event)
                if game_data:
                    games.append(game_data)
            
            return games
            
        except Exception as e:
            print(f"❌ Error getting week games: {e}")
            return []
    
    def _parse_game_details(self, data: Dict) -> Dict:
        """Parse detailed game information"""
        game_details = {
            "id": data.get("id"),
            "name": data.get("name"),
            "short_name": data.get("shortName"),
            "date": data.get("date"),
            "week": data.get("week", {}).get("number"),
            "season": data.get("season", {}).get("year"),
            "status": data.get("status", {}),
            "teams": {},
            "venue": {},
            "weather": {}
        }
        
        # Parse competitions
        competitions = data.get("competitions", [])
        if competitions:
            comp = competitions[0]
            
            # Parse venue
            if "venue" in comp:
                venue = comp["venue"]
                game_details["venue"] = {
                    "name": venue.get("fullName"),
                    "city": venue.get("address", {}).get("city"),
                    "state": venue.get("address", {}).get("state")
                }
            
            # Parse weather
            if "weather" in comp:
                weather = comp["weather"]
                game_details["weather"] = {
                    "temperature": weather.get("temperature"),
                    "condition": weather.get("displayValue"),
                    "humidity": weather.get("humidity"),
                    "wind": weather.get("windSpeed")
                }
            
            # Parse competitors (teams)
            competitors = comp.get("competitors", [])
            for competitor in competitors:
                team_info = competitor.get("team", {})
                team_data = {
                    "id": team_info.get("id"),
                    "name": team_info.get("displayName"),
                    "abbreviation": team_info.get("abbreviation"),
                    "score": competitor.get("score"),
                    "home_away": competitor.get("homeAway"),
                    "record": team_info.get("record", {}).get("items", [])
                }
                
                if team_data["home_away"] == "home":
                    game_details["teams"]["home"] = team_data
                elif team_data["home_away"] == "away":
                    game_details["teams"]["away"] = team_data
        
        return game_details
    
    def _parse_predictions(self, data: Dict) -> Dict:
        """Parse ESPN prediction data"""
        predictions = {
            "last_modified": data.get("lastModified"),
            "home_team": {},
            "away_team": {}
        }
        
        # Parse home team predictions
        if "homeTeam" in data:
            home_data = data["homeTeam"]
            predictions["home_team"] = {
                "team": home_data.get("team", {}).get("displayName"),
                "win_probability": home_data.get("winProbability"),
                "spread": home_data.get("spread"),
                "total": home_data.get("total")
            }
        
        # Parse away team predictions
        if "awayTeam" in data:
            away_data = data["awayTeam"]
            predictions["away_team"] = {
                "team": away_data.get("team", {}).get("displayName"),
                "win_probability": away_data.get("winProbability"),
                "spread": away_data.get("spread"),
                "total": away_data.get("total")
            }
        
        return predictions
    
    def _parse_injury_data(self, data: Dict) -> List[Dict]:
        """Parse injury data"""
        injuries = []
        
        try:
            items = data.get("items", [])
            for item in items:
                # Get detailed injury info from the reference
                injury_ref = item.get("$ref")
                if injury_ref:
                    injury_details = self._fetch_injury_details(injury_ref)
                    if injury_details:
                        injuries.append(injury_details)
            
        except Exception as e:
            print(f"❌ Error parsing injury data: {e}")
        
        return injuries
    
    def _fetch_injury_details(self, injury_ref: str) -> Optional[Dict]:
        """Fetch detailed injury information from reference"""
        try:
            response = requests.get(injury_ref, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return {
                "player_name": data.get("athlete", {}).get("displayName"),
                "position": data.get("athlete", {}).get("position", {}).get("displayName"),
                "status": data.get("status"),
                "injury_type": data.get("injury", {}).get("type"),
                "injury_description": data.get("injury", {}).get("description"),
                "date_updated": data.get("dateUpdated")
            }
            
        except Exception as e:
            print(f"❌ Error fetching injury details: {e}")
            return None
    
    def _parse_team_info(self, data: Dict) -> Dict:
        """Parse team information"""
        return {
            "id": data.get("id"),
            "name": data.get("displayName"),
            "abbreviation": data.get("abbreviation"),
            "location": data.get("location"),
            "nickname": data.get("nickname"),
            "record": data.get("record", {}),
            "venue": data.get("venue", {}),
            "colors": {
                "primary": data.get("color"),
                "secondary": data.get("alternateColor")
            }
        }
    
    def _parse_basic_game(self, event: Dict) -> Optional[Dict]:
        """Parse basic game information"""
        try:
            game_id = event.get("id")
            if not game_id:
                return None
            
            teams = {}
            for competitor in event.get("competitions", [{}])[0].get("competitors", []):
                team_info = competitor.get("team", {})
                team_data = {
                    "id": team_info.get("id"),
                    "name": team_info.get("displayName"),
                    "abbreviation": team_info.get("abbreviation"),
                    "score": competitor.get("score"),
                    "home_away": competitor.get("homeAway")
                }
                
                if team_data["home_away"] == "home":
                    teams["home"] = team_data
                elif team_data["home_away"] == "away":
                    teams["away"] = team_data
            
            return {
                "id": game_id,
                "name": event.get("name"),
                "date": event.get("date"),
                "teams": teams,
                "status": event.get("status", {})
            }
            
        except Exception as e:
            print(f"❌ Error parsing basic game: {e}")
            return None
    
    def _get_week_date_range(self, year: int, week: int) -> Dict[str, str]:
        """Calculate date range for NFL week"""
        if week == 1:
            start_date = dt.date(year, 9, 1)
            while start_date.weekday() != 3:  # Thursday
                start_date += dt.timedelta(days=1)
        else:
            week1_start = self._get_week_date_range(year, 1)["start"]
            start_date = dt.datetime.strptime(week1_start, "%Y%m%d").date()
            start_date += dt.timedelta(days=(week - 1) * 7)
        
        end_date = start_date + dt.timedelta(days=4)
        
        return {
            "start": start_date.strftime("%Y%m%d"),
            "end": end_date.strftime("%Y%m%d")
        }

def test_working_api():
    """Test the working ESPN API"""
    api = WorkingESPNAPI()
    
    print("🧪 Testing Working ESPN API...")
    
    # Test getting Week 1 games with details
    games = api.get_week_games_with_details(2025, 1)
    
    print(f"✅ Found {len(games)} detailed games")
    
    if games:
        # Show sample of first game
        first_game = games[0]
        print(f"\n🎮 Sample game details:")
        print(f"   Game: {first_game.get('name')}")
        print(f"   Date: {first_game.get('date')}")
        print(f"   Teams: {first_game.get('teams', {}).keys()}")
        
        if "espn_predictions" in first_game:
            pred = first_game["espn_predictions"]
            print(f"   ESPN Predictions:")
            if "home_team" in pred:
                print(f"     Home: {pred['home_team'].get('team')} - {pred['home_team'].get('win_probability')}%")
            if "away_team" in pred:
                print(f"     Away: {pred['away_team'].get('team')} - {pred['away_team'].get('win_probability')}%")
        
        if "injuries" in first_game:
            total_injuries = sum(len(team_injuries) for team_injuries in first_game["injuries"].values())
            print(f"   Injuries: {total_injuries} total across both teams")

if __name__ == "__main__":
    test_working_api()
