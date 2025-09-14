#!/usr/bin/env python3
"""
Enhanced ESPN API integration using comprehensive endpoints from pseudo-r/Public-ESPN-API.
This provides access to detailed game statistics, player data, and advanced metrics.
"""
import requests
import json
from typing import Dict, List, Optional, Tuple
import datetime as dt

class EnhancedESPNAPI:
    """Enhanced ESPN API client with comprehensive data access"""
    
    def __init__(self):
        self.site_base = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        self.core_base = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl"
        self.timeout = 30
    
    def get_detailed_game_stats(self, game_id: str) -> Dict:
        """
        Get comprehensive game statistics including team and player stats.
        
        Args:
            game_id: ESPN game ID
            
        Returns:
            Detailed game statistics
        """
        print(f"📊 Fetching detailed stats for game {game_id}...")
        
        # Get game summary with detailed stats
        url = f"{self.core_base}/events/{game_id}/competitions/{game_id}/statistics"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_detailed_game_stats(data)
            
        except Exception as e:
            print(f"❌ Error fetching detailed stats: {e}")
            return {}
    
    def get_team_season_stats(self, team_id: str, season: int = 2025) -> Dict:
        """
        Get comprehensive team statistics for the season.
        
        Args:
            team_id: ESPN team ID
            season: Season year
            
        Returns:
            Team season statistics
        """
        print(f"🏈 Fetching season stats for team {team_id}...")
        
        url = f"{self.core_base}/teams/{team_id}/statistics"
        params = {"season": season}
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_team_stats(data)
            
        except Exception as e:
            print(f"❌ Error fetching team stats: {e}")
            return {}
    
    def get_espn_predictions(self, game_id: str) -> Dict:
        """
        Get ESPN's internal prediction metrics for a game.
        
        Args:
            game_id: ESPN game ID
            
        Returns:
            ESPN prediction data
        """
        print(f"🔮 Fetching ESPN predictions for game {game_id}...")
        
        url = f"{self.core_base}/events/{game_id}/competitions/{game_id}/predictor"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_espn_predictions(data)
            
        except Exception as e:
            print(f"❌ Error fetching predictions: {e}")
            return {}
    
    def get_power_index(self, game_id: str, team_id: str) -> Dict:
        """
        Get ESPN's power index rating for a team in a specific game.
        
        Args:
            game_id: ESPN game ID
            team_id: ESPN team ID
            
        Returns:
            Power index data
        """
        print(f"⚡ Fetching power index for team {team_id} in game {game_id}...")
        
        url = f"{self.core_base}/events/{game_id}/competitions/{game_id}/powerindex/{team_id}"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_power_index(data)
            
        except Exception as e:
            print(f"❌ Error fetching power index: {e}")
            return {}
    
    def get_player_injuries(self, team_id: str) -> List[Dict]:
        """
        Get detailed injury information for a team.
        
        Args:
            team_id: ESPN team ID
            
        Returns:
            List of injury reports
        """
        print(f"🏥 Fetching injury data for team {team_id}...")
        
        url = f"{self.core_base}/teams/{team_id}/injuries"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_injury_data(data)
            
        except Exception as e:
            print(f"❌ Error fetching injury data: {e}")
            return []
    
    def get_week_analysis(self, year: int, week: int) -> Dict:
        """
        Get comprehensive analysis for all games in a week.
        
        Args:
            year: NFL season year
            week: Week number
            
        Returns:
            Comprehensive week analysis
        """
        print(f"📅 Analyzing Week {week} games...")
        
        # Get games for the week
        games = self._get_week_games(year, week)
        
        analysis = {
            "week": week,
            "year": year,
            "games": [],
            "summary": {}
        }
        
        for game in games:
            game_id = game.get("id")
            if not game_id:
                continue
            
            game_analysis = {
                "game_id": game_id,
                "teams": game.get("teams", {}),
                "basic_result": game,
                "detailed_stats": {},
                "espn_predictions": {},
                "power_index": {},
                "injuries": {}
            }
            
            # Get detailed statistics
            detailed_stats = self.get_detailed_game_stats(game_id)
            game_analysis["detailed_stats"] = detailed_stats
            
            # Get ESPN predictions
            predictions = self.get_espn_predictions(game_id)
            game_analysis["espn_predictions"] = predictions
            
            # Get power index for both teams
            for team_id in game_analysis["teams"].values():
                if team_id:
                    power_data = self.get_power_index(game_id, team_id)
                    game_analysis["power_index"][team_id] = power_data
            
            # Get injury data for both teams
            for team_id in game_analysis["teams"].values():
                if team_id:
                    injuries = self.get_player_injuries(team_id)
                    game_analysis["injuries"][team_id] = injuries
            
            analysis["games"].append(game_analysis)
        
        return analysis
    
    def _get_week_games(self, year: int, week: int) -> List[Dict]:
        """Get basic game information for a week"""
        # Use the existing scoreboard endpoint
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
    
    def _parse_detailed_game_stats(self, data: Dict) -> Dict:
        """Parse detailed game statistics"""
        stats = {
            "teams": {},
            "summary": {}
        }
        
        try:
            if "items" in data:
                for item in data["items"]:
                    team_id = item.get("team", {}).get("id")
                    if team_id:
                        team_stats = {}
                        
                        if "statistics" in item:
                            for stat in item["statistics"]:
                                label = stat.get("label", "Unknown")
                                value = stat.get("displayValue", "N/A")
                                team_stats[label] = value
                        
                        stats["teams"][team_id] = team_stats
            
        except Exception as e:
            print(f"❌ Error parsing detailed stats: {e}")
        
        return stats
    
    def _parse_team_stats(self, data: Dict) -> Dict:
        """Parse team season statistics"""
        stats = {}
        
        try:
            if "items" in data:
                for item in data["items"]:
                    category = item.get("label", "Unknown")
                    value = item.get("displayValue", "N/A")
                    stats[category] = value
            
        except Exception as e:
            print(f"❌ Error parsing team stats: {e}")
        
        return stats
    
    def _parse_espn_predictions(self, data: Dict) -> Dict:
        """Parse ESPN prediction data"""
        predictions = {}
        
        try:
            # ESPN predictor data structure varies
            # This is a simplified parser
            if "homeTeam" in data:
                predictions["home_team"] = data["homeTeam"]
            if "awayTeam" in data:
                predictions["away_team"] = data["awayTeam"]
            if "gameProjection" in data:
                predictions["projection"] = data["gameProjection"]
            
        except Exception as e:
            print(f"❌ Error parsing predictions: {e}")
        
        return predictions
    
    def _parse_power_index(self, data: Dict) -> Dict:
        """Parse power index data"""
        power_data = {}
        
        try:
            if "items" in data:
                for item in data["items"]:
                    category = item.get("label", "Unknown")
                    value = item.get("displayValue", "N/A")
                    power_data[category] = value
            
        except Exception as e:
            print(f"❌ Error parsing power index: {e}")
        
        return power_data
    
    def _parse_injury_data(self, data: Dict) -> List[Dict]:
        """Parse injury data"""
        injuries = []
        
        try:
            if "items" in data:
                for item in data["items"]:
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
            print(f"❌ Error parsing injury data: {e}")
        
        return injuries
    
    def _parse_basic_game(self, event: Dict) -> Optional[Dict]:
        """Parse basic game information"""
        try:
            game_id = event.get("id")
            if not game_id:
                return None
            
            teams = {}
            for competitor in event.get("competitions", [{}])[0].get("competitors", []):
                team_info = competitor.get("team", {})
                team_id = team_info.get("id")
                team_name = team_info.get("displayName")
                
                if competitor.get("homeAway") == "home":
                    teams["home"] = {"id": team_id, "name": team_name}
                elif competitor.get("homeAway") == "away":
                    teams["away"] = {"id": team_id, "name": team_name}
            
            return {
                "id": game_id,
                "teams": teams,
                "date": event.get("date"),
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

def test_enhanced_api():
    """Test the enhanced ESPN API"""
    api = EnhancedESPNAPI()
    
    print("🧪 Testing Enhanced ESPN API...")
    
    # Test getting Week 1 analysis
    analysis = api.get_week_analysis(2025, 1)
    
    if analysis["games"]:
        print(f"✅ Found {len(analysis['games'])} games")
        
        # Show sample of first game analysis
        first_game = analysis["games"][0]
        print(f"\n🎮 Sample game analysis:")
        print(f"   Game ID: {first_game['game_id']}")
        print(f"   Teams: {first_game['teams']}")
        print(f"   Detailed stats keys: {list(first_game['detailed_stats'].keys())}")
        print(f"   ESPN predictions keys: {list(first_game['espn_predictions'].keys())}")
        print(f"   Power index keys: {list(first_game['power_index'].keys())}")
        print(f"   Injuries keys: {list(first_game['injuries'].keys())}")
    else:
        print("❌ No games found")

if __name__ == "__main__":
    test_enhanced_api()
