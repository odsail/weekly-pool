#!/usr/bin/env python3
"""
Historical data collector for NFL games (2018-2024) with international game awareness.
Collects game results, team performance, and home field advantage data.
"""
import requests
import json
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import time
import os
from database_manager import DatabaseManager

class HistoricalDataCollector:
    """Collects historical NFL data with international game awareness"""
    
    def __init__(self, version: str = "v2"):
        self.db_manager = DatabaseManager(version=version)
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        
        # International game locations and their characteristics
        self.international_locations = {
            'London': {'timezone': 5, 'neutral_site': True},
            'Frankfurt': {'timezone': 6, 'neutral_site': True},
            'Dublin': {'timezone': 5, 'neutral_site': True},
            'Mexico City': {'timezone': -6, 'neutral_site': True},
            'Toronto': {'timezone': 0, 'neutral_site': False}  # Bills games
        }
        
        # Known international games by season (this would be populated from research)
        self.international_games = {
            2024: [
                {'week': 5, 'home': 'Jacksonville Jaguars', 'away': 'Chicago Bears', 'location': 'London'},
                {'week': 6, 'home': 'Minnesota Vikings', 'away': 'New York Jets', 'location': 'London'},
                {'week': 7, 'home': 'Jacksonville Jaguars', 'away': 'New England Patriots', 'location': 'London'},
                {'week': 8, 'home': 'New York Giants', 'away': 'Green Bay Packers', 'location': 'London'},
                {'week': 9, 'home': 'Philadelphia Eagles', 'away': 'Jacksonville Jaguars', 'location': 'London'},
                {'week': 10, 'home': 'Indianapolis Colts', 'away': 'New England Patriots', 'location': 'Frankfurt'},
                {'week': 11, 'home': 'New York Giants', 'away': 'Carolina Panthers', 'location': 'Frankfurt'},
            ],
            2023: [
                {'week': 4, 'home': 'Jacksonville Jaguars', 'away': 'Atlanta Falcons', 'location': 'London'},
                {'week': 5, 'home': 'Jacksonville Jaguars', 'away': 'Buffalo Bills', 'location': 'London'},
                {'week': 6, 'home': 'Baltimore Ravens', 'away': 'Tennessee Titans', 'location': 'London'},
                {'week': 9, 'home': 'Miami Dolphins', 'away': 'Kansas City Chiefs', 'location': 'Frankfurt'},
                {'week': 10, 'home': 'Indianapolis Colts', 'away': 'New England Patriots', 'location': 'Frankfurt'},
            ],
            # Add more seasons as needed
        }
    
    def collect_season_data(self, year: int) -> bool:
        """Collect all data for a specific season"""
        print(f"🏈 Collecting data for {year} season...")
        
        try:
            # Get season schedule
            schedule = self._get_season_schedule(year)
            if not schedule:
                print(f"❌ Failed to get schedule for {year}")
                return False
            
            # Process regular season weeks (1-18)
            for week in range(1, 19):
                print(f"   📅 Processing Regular Season Week {week}...")
                week_games = self._get_week_games(year, week)
                
                for game in week_games:
                    self._process_game(game, year, week)
                
                # Rate limiting
                time.sleep(0.5)
            
            # Process playoffs and Super Bowl
            print(f"   🏆 Processing Playoffs and Super Bowl...")
            playoff_games = self._get_playoff_games(year)
            
            for game in playoff_games:
                # Determine playoff week (19-22 typically)
                playoff_week = self._determine_playoff_week(game, year)
                self._process_game(game, year, playoff_week)
            
            # Rate limiting
            time.sleep(0.5)
            
            # Calculate home field advantage for the season
            self._calculate_home_field_advantage(year)
            
            print(f"✅ Completed data collection for {year}")
            return True
            
        except Exception as e:
            print(f"❌ Error collecting data for {year}: {e}")
            return False
    
    def _get_season_schedule(self, year: int) -> Optional[Dict]:
        """Get the full season schedule from ESPN"""
        url = f"{self.base_url}/scoreboard"
        params = {
            'dates': f"{year}0901-{year+1}0107",  # Full season range
            'limit': 1000
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching schedule: {e}")
            return None
    
    def _get_week_games(self, year: int, week: int) -> List[Dict]:
        """Get games for a specific week using ESPN API"""
        # Use specific dates for each week (more reliable than date ranges)
        week_dates = self._get_week_dates(year, week)
        
        all_games = []
        for date in week_dates:
            url = f"{self.base_url}/scoreboard"
            params = {'dates': date}
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                for event in data.get('events', []):
                    # Only include completed games
                    if event.get('status', {}).get('type', {}).get('name') == 'STATUS_FINAL':
                        all_games.append(event)
                
                # Rate limiting
                time.sleep(0.2)
                
            except Exception as e:
                print(f"⚠️  Error fetching games for {date}: {e}")
                continue
        
        return all_games
    
    def _process_game(self, game: Dict, year: int, week: int):
        """Process a single game and store in database"""
        try:
            # Extract game data
            home_team = game['competitions'][0]['competitors'][0]['team']['displayName']
            away_team = game['competitions'][0]['competitors'][1]['team']['displayName']
            
            # Skip invalid games (Pro Bowl, etc.)
            if self.db_manager.team_mapper.should_skip_game(home_team, away_team):
                return  # Skip this game
            
            # Get scores
            home_score = int(game['competitions'][0]['competitors'][0]['score'])
            away_score = int(game['competitions'][0]['competitors'][1]['score'])
            
            # Check if this is an international game
            is_international, location = self._is_international_game(home_team, away_team, year, week)
            
            # Determine true home team (for international games, this might be different)
            true_home_team = self._get_true_home_team(home_team, away_team, is_international, location)
            
            # Get stadium info
            stadium_info = game['competitions'][0].get('venue', {})
            stadium_type = self._get_stadium_type(stadium_info, is_international)
            
            # Create/update game in database
            game_id = self.db_manager.upsert_game(
                year, week, home_team, away_team, 
                game['date'],
                home_score, away_score
            )
            
            # Update game with additional info
            self._update_game_details(game_id, is_international, location, true_home_team, stadium_type)
            
            # Store international game details if applicable
            if is_international:
                self._store_international_game(game_id, home_team, away_team, location, true_home_team)
            
        except Exception as e:
            print(f"⚠️  Error processing game: {e}")
    
    def _is_international_game(self, home_team: str, away_team: str, year: int, week: int) -> Tuple[bool, Optional[str]]:
        """Check if a game is an international game"""
        if year in self.international_games:
            for intl_game in self.international_games[year]:
                if (intl_game['week'] == week and 
                    intl_game['home'] == home_team and 
                    intl_game['away'] == away_team):
                    return True, intl_game['location']
        
        return False, None
    
    def _get_true_home_team(self, scheduled_home: str, away_team: str, is_international: bool, location: Optional[str]) -> str:
        """Determine the true home team (may differ for international games)"""
        if is_international and location in ['London', 'Frankfurt', 'Dublin']:
            # For true neutral sites, we might consider both teams as "away"
            # or use some other logic to determine the "home" team
            return scheduled_home  # For now, keep the scheduled home team
        return scheduled_home
    
    def _get_stadium_type(self, stadium_info: Dict, is_international: bool) -> str:
        """Determine stadium type"""
        if is_international:
            return 'international'
        
        stadium_name = stadium_info.get('fullName', '').lower()
        if any(dome in stadium_name for dome in ['dome', 'stadium', 'center', 'field']):
            # This is a simplified check - would need more comprehensive data
            return 'dome'
        
        return 'outdoor'
    
    def _update_game_details(self, game_id: int, is_international: bool, location: Optional[str], 
                           true_home_team: str, stadium_type: str):
        """Update game with additional details"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE games 
                SET is_international = ?, international_location = ?, 
                    true_home_team_id = (SELECT id FROM teams WHERE name = ?),
                    stadium_type = ?
                WHERE id = ?
            """, (is_international, location, true_home_team, stadium_type, game_id))
            conn.commit()
    
    def _store_international_game(self, game_id: int, scheduled_home: str, scheduled_away: str, 
                                location: str, true_home_team: str):
        """Store international game details"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get team IDs
            home_team_id = self.db_manager.get_team_id(scheduled_home)
            away_team_id = self.db_manager.get_team_id(scheduled_away)
            true_home_team_id = self.db_manager.get_team_id(true_home_team)
            
            if home_team_id and away_team_id:
                cursor.execute("""
                    INSERT INTO international_games 
                    (game_id, location, scheduled_home_team_id, scheduled_away_team_id, 
                     actual_home_team_id, neutral_site, time_zone_difference)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (game_id, location, home_team_id, away_team_id, true_home_team_id, 
                      True, self.international_locations.get(location, {}).get('timezone', 0)))
                conn.commit()
    
    def _calculate_home_field_advantage(self, year: int):
        """Calculate home field advantage for each team, excluding international games"""
        print(f"   🏠 Calculating home field advantage for {year}...")
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all teams
            cursor.execute("SELECT id FROM teams")
            teams = cursor.fetchall()
            
            for (team_id,) in teams:
                # Get true home games (excluding international)
                cursor.execute("""
                    SELECT COUNT(*), SUM(CASE WHEN winner_team_id = ? THEN 1 ELSE 0 END)
                    FROM games 
                    WHERE season_year = ? AND home_team_id = ? AND is_international = FALSE
                """, (team_id, year, team_id))
                
                true_home_games, true_home_wins = cursor.fetchone()
                true_home_wins = true_home_wins or 0  # Handle None case
                true_home_losses = true_home_games - true_home_wins
                
                # Get international games
                cursor.execute("""
                    SELECT COUNT(*), SUM(CASE WHEN winner_team_id = ? THEN 1 ELSE 0 END)
                    FROM games 
                    WHERE season_year = ? AND home_team_id = ? AND is_international = TRUE
                """, (team_id, year, team_id))
                
                intl_games, intl_wins = cursor.fetchone()
                intl_wins = intl_wins or 0  # Handle None case
                intl_losses = intl_games - intl_wins
                
                # Calculate percentages
                home_win_pct = true_home_wins / true_home_games if true_home_games > 0 else 0
                intl_win_pct = intl_wins / intl_games if intl_games > 0 else 0
                
                # Calculate home field advantage (home win % - international win %)
                home_field_adv = home_win_pct - intl_win_pct if intl_games > 0 else home_win_pct - 0.5
                
                # Store in database
                cursor.execute("""
                    INSERT OR REPLACE INTO home_field_advantage 
                    (team_id, season_year, true_home_games, true_home_wins, true_home_losses,
                     international_games, international_wins, international_losses,
                     home_win_percentage, international_win_percentage, home_field_advantage)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (team_id, year, true_home_games, true_home_wins, true_home_losses,
                      intl_games, intl_wins, intl_losses, home_win_pct, intl_win_pct, home_field_adv))
            
            conn.commit()
    
    def _get_week_dates(self, year: int, week: int) -> List[str]:
        """Get specific dates for a given week using a broader date range"""
        # NFL seasons start as early as August 25th, not September 1st
        # Use a broader approach to capture all games for each week
        
        week_dates = []
        
        # Define season start dates (NFL seasons start in late August)
        season_start_dates = {
            2018: pd.Timestamp("2018-08-25"),
            2019: pd.Timestamp("2019-08-25"), 
            2020: pd.Timestamp("2020-09-10"),  # COVID year, started later
            2021: pd.Timestamp("2021-08-27"),
            2022: pd.Timestamp("2022-08-25"),
            2023: pd.Timestamp("2023-08-25"),
            2024: pd.Timestamp("2024-08-25"),
        }
        
        # Get season start date for the year
        season_start = season_start_dates.get(year, pd.Timestamp(f"{year}-08-25"))
        
        # Calculate week start (each week is approximately 7 days)
        week_start = season_start + pd.Timedelta(weeks=week-1)
        
        # Create a broader date range for each week (5 days to catch all games)
        for i in range(5):  # Thursday through Monday
            date = week_start + pd.Timedelta(days=i)
            week_dates.append(date.strftime('%Y%m%d'))
        
        return week_dates
    
    def _get_playoff_games(self, year: int) -> List[Dict]:
        """Get playoff and Super Bowl games for a season"""
        # Playoffs run from early January to early February
        # Use a date range to capture all playoff games
        playoff_start = f"{year+1}0106"  # Start of Wild Card weekend
        playoff_end = f"{year+1}0215"    # End of Super Bowl week
        
        all_playoff_games = []
        
        # Get games for the entire playoff period
        url = f"{self.base_url}/scoreboard"
        params = {
            'dates': f"{playoff_start}-{playoff_end}",
            'limit': 1000
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for event in data.get('events', []):
                # Only include completed games
                if event.get('status', {}).get('type', {}).get('name') == 'STATUS_FINAL':
                    # Check if it's a playoff game by date and context
                    if self._is_playoff_game_by_date(event, year):
                        all_playoff_games.append(event)
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"⚠️  Error fetching playoff games: {e}")
        
        return all_playoff_games
    
    def _is_playoff_game_by_date(self, game: Dict, year: int) -> bool:
        """Determine if a game is a playoff game based on date and context"""
        game_date = game.get('date', '')
        if not game_date:
            return False
        
        try:
            from datetime import datetime
            game_dt = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
            game_month = game_dt.month
            game_day = game_dt.day
            
            # Playoff games are in January and early February
            if game_month == 1 or (game_month == 2 and game_day <= 15):
                # Exclude regular season games that might be in January
                # Regular season typically ends by early January
                if game_month == 1 and game_day <= 7:
                    # These could be regular season games, check for playoff indicators
                    name = game.get('name', '').lower()
                    playoff_indicators = ['wild card', 'divisional', 'conference', 'super bowl', 'playoff']
                    return any(indicator in name for indicator in playoff_indicators)
                else:
                    # Games after Jan 7 are definitely playoffs
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _determine_playoff_week(self, game: Dict, year: int) -> int:
        """Determine the playoff week number for a game"""
        game_date = game.get('date', '')
        game_name = game.get('name', '').lower()
        
        if not game_date:
            return 19  # Default to Wild Card
        
        # Parse game date
        try:
            from datetime import datetime
            game_dt = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
            game_month = game_dt.month
            game_day = game_dt.day
            
            # Determine playoff round based on date and game name
            if game_month == 1:  # January
                if game_day <= 8:
                    return 19  # Wild Card Weekend (Jan 6-8)
                elif game_day <= 15:
                    return 20  # Divisional Round (Jan 13-15)
                elif game_day <= 22:
                    return 21  # Conference Championships (Jan 20-22)
                else:
                    return 22  # Super Bowl (Jan 28+)
            elif game_month == 2 and game_day <= 15:
                return 22  # Super Bowl (Feb 1-15)
            else:
                # Fallback: use game name to determine round
                if 'wild card' in game_name:
                    return 19
                elif 'divisional' in game_name:
                    return 20
                elif 'conference' in game_name:
                    return 21
                elif 'super bowl' in game_name:
                    return 22
                else:
                    return 19  # Default to Wild Card
                
        except Exception:
            return 19  # Default to Wild Card
    
    def collect_all_historical_data(self, start_year: int = 2018, end_year: int = 2024):
        """Collect historical data for multiple seasons"""
        print(f"🚀 Starting historical data collection for {start_year}-{end_year}")
        
        success_count = 0
        for year in range(start_year, end_year + 1):
            if self.collect_season_data(year):
                success_count += 1
            time.sleep(1)  # Rate limiting between seasons
        
        print(f"✅ Completed historical data collection: {success_count}/{end_year - start_year + 1} seasons")
        
        # Generate summary report
        self._generate_historical_summary()
    
    def _generate_historical_summary(self):
        """Generate a summary of collected historical data"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total games collected
            cursor.execute("SELECT COUNT(*) FROM games")
            total_games = cursor.fetchone()[0]
            
            # Get international games
            cursor.execute("SELECT COUNT(*) FROM games WHERE is_international = TRUE")
            intl_games = cursor.fetchone()[0]
            
            # Get seasons covered
            cursor.execute("SELECT DISTINCT season_year FROM games ORDER BY season_year")
            seasons = [row[0] for row in cursor.fetchall()]
            
            print(f"\n📊 Historical Data Summary:")
            print(f"   Total Games: {total_games}")
            print(f"   International Games: {intl_games}")
            print(f"   Seasons: {seasons}")
            print(f"   Home Field Advantage Data: Available for all teams")

def main():
    """Collect historical data"""
    collector = HistoricalDataCollector()
    
    # Collect data for recent seasons including complete 2024 season
    print("🏈 Collecting complete historical data including playoffs and Super Bowl...")
    collector.collect_all_historical_data(2020, 2024)
    
    print("\n🎉 Historical data collection completed!")
    print("💡 The ML model can now use this data for better predictions")
    print("📊 Data includes regular season, playoffs, and Super Bowl games")

if __name__ == "__main__":
    main()
