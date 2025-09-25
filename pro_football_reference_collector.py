#!/usr/bin/env python3
"""
Pro-Football-Reference.com data collector for NFL games.
Downloads game data in CSV format and processes it for our database.
"""

import requests
import pandas as pd
import time
from typing import List, Dict, Optional
from database_manager import DatabaseManager
from team_name_mapper import TeamNameMapper

class ProFootballReferenceCollector:
    """Collects NFL game data from Pro-Football-Reference.com"""
    
    def __init__(self, version: str = "v2"):
        self.db_manager = DatabaseManager(version=version)
        self.team_mapper = TeamNameMapper()
        self.base_url = "https://www.pro-football-reference.com"
        
        # Headers to mimic a browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def collect_season_data(self, year: int) -> bool:
        """Collect all game data for a specific season"""
        print(f"🏈 Collecting {year} season data from Pro-Football-Reference...")
        
        try:
            # Get all games (regular season + playoffs are in the same data)
            all_games = self._get_regular_season_games(year)
            if all_games:
                # Count regular season vs playoff games
                regular_games = [g for g in all_games if g['week'] <= 18]
                playoff_games = [g for g in all_games if g['week'] >= 19]
                
                print(f"   📊 Found {len(regular_games)} regular season games")
                print(f"   🏆 Found {len(playoff_games)} playoff games")
                print(f"   📈 Total: {len(all_games)} games")
                
                self._process_games(all_games, year, "all")
            
            print(f"✅ Completed data collection for {year}")
            return True
            
        except Exception as e:
            print(f"❌ Error collecting data for {year}: {e}")
            return False
    
    def _get_regular_season_games(self, year: int) -> List[Dict]:
        """Get regular season games from Pro-Football-Reference (includes playoff games)"""
        url = f"{self.base_url}/years/{year}/games.htm"
        
        try:
            # Use pandas to read the HTML table directly
            tables = pd.read_html(url, header=0)
            
            # The games table is usually the first table
            games_df = tables[0]
            
            # Clean up the dataframe
            games_df = games_df.dropna(subset=['Week'])  # Remove rows without week numbers
            
            # Convert to list of dictionaries
            games = []
            for _, row in games_df.iterrows():
                try:
                    # Skip rows that don't have game data
                    if pd.isna(row.get('Week')) or row.get('Week') == 'Week':
                        continue
                    
                    week_str = str(row.get('Week', ''))
                    
                    # Determine week number (including playoff games)
                    if week_str.isdigit():
                        week = int(week_str)
                    elif week_str == 'WildCard':
                        week = 19
                    elif week_str == 'Division':
                        week = 20
                    elif week_str == 'ConfChamp':
                        week = 21
                    elif week_str == 'SuperBowl':
                        week = 22
                    else:
                        continue  # Skip unknown week types
                    
                    game = {
                        'week': week,
                        'date': row.get('Date', ''),
                        'away_team': row.get('Winner/tie', ''),
                        'home_team': row.get('Loser/tie', ''),
                        'away_score': int(row.get('PtsW', 0)) if pd.notna(row.get('PtsW')) else None,
                        'home_score': int(row.get('PtsL', 0)) if pd.notna(row.get('PtsL')) else None,
                        'away_points': int(row.get('PtsW', 0)) if pd.notna(row.get('PtsW')) else None,
                        'home_points': int(row.get('PtsL', 0)) if pd.notna(row.get('PtsL')) else None,
                    }
                    
                    # Handle ties (both teams have same score)
                    if row.get('PtsW') == row.get('PtsL'):
                        # For ties, we need to determine which team is home/away differently
                        # This might need adjustment based on actual data structure
                        pass
                    
                    games.append(game)
                    
                except (ValueError, TypeError) as e:
                    # Skip rows that can't be parsed
                    continue
            
            return games
            
        except Exception as e:
            print(f"❌ Error fetching regular season games: {e}")
            return []
    
    def _get_playoff_games(self, year: int) -> List[Dict]:
        """Get playoff games from Pro-Football-Reference"""
        url = f"{self.base_url}/years/{year}/playoffs.htm"
        
        try:
            tables = pd.read_html(url, header=0)
            
            if not tables:
                return []
            
            games_df = tables[0]
            games = []
            
            for _, row in games_df.iterrows():
                try:
                    # Determine playoff week based on round
                    week = self._determine_playoff_week(row.get('Round', ''))
                    
                    game = {
                        'week': week,
                        'date': row.get('Date', ''),
                        'away_team': row.get('Winner', ''),
                        'home_team': row.get('Loser', ''),
                        'away_score': int(row.get('PtsW', 0)) if pd.notna(row.get('PtsW')) else None,
                        'home_score': int(row.get('PtsL', 0)) if pd.notna(row.get('PtsL')) else None,
                        'away_points': int(row.get('PtsW', 0)) if pd.notna(row.get('PtsW')) else None,
                        'home_points': int(row.get('PtsL', 0)) if pd.notna(row.get('PtsL')) else None,
                    }
                    
                    games.append(game)
                    
                except (ValueError, TypeError) as e:
                    continue
            
            return games
            
        except Exception as e:
            print(f"❌ Error fetching playoff games: {e}")
            return []
    
    def _determine_playoff_week(self, round_name: str) -> int:
        """Determine playoff week number based on round name"""
        round_name = str(round_name).lower()
        
        if 'wild card' in round_name:
            return 19
        elif 'divisional' in round_name:
            return 20
        elif 'conference' in round_name:
            return 21
        elif 'super bowl' in round_name:
            return 22
        else:
            return 19  # Default to wild card
    
    def _process_games(self, games: List[Dict], year: int, season_type: str):
        """Process and store games in database"""
        for game in games:
            try:
                # Map team names
                home_team = self.team_mapper.map_team_name(game['home_team'])
                away_team = self.team_mapper.map_team_name(game['away_team'])
                
                # Skip invalid games
                if not home_team or not away_team:
                    continue
                
                # Parse date
                game_date = self._parse_date(game['date'], year)
                
                # Get scores
                home_score = game.get('home_score')
                away_score = game.get('away_score')
                
                # Store in database
                game_id = self.db_manager.upsert_game(
                    year, game['week'], home_team, away_team, game_date,
                    home_score, away_score
                )
                
            except Exception as e:
                print(f"⚠️  Error processing game: {e}")
                continue
    
    def _parse_date(self, date_str: str, year: int) -> str:
        """Parse date string to ISO format"""
        try:
            # Pro-Football-Reference dates are usually in format like "Sun, Sep 8"
            # We need to convert this to a full date
            if ',' in date_str:
                day_name, month_day = date_str.split(',', 1)
                month_day = month_day.strip()
                
                # Parse month and day
                month_map = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                }
                
                month_abbr = month_day.split()[0]
                day = month_day.split()[1]
                
                if month_abbr in month_map:
                    month = month_map[month_abbr]
                    # Handle year (playoff games might be in next year)
                    if month in ['01', '02'] and 'playoff' in str(year):
                        actual_year = year + 1
                    else:
                        actual_year = year
                    
                    return f"{actual_year}-{month}-{day.zfill(2)}"
            
            return f"{year}-01-01"  # Default fallback
            
        except Exception as e:
            print(f"⚠️  Error parsing date '{date_str}': {e}")
            return f"{year}-01-01"
    
    def collect_all_historical_data(self, start_year: int = 2018, end_year: int = 2024):
        """Collect historical data for multiple seasons"""
        print(f"🚀 Starting Pro-Football-Reference data collection for {start_year}-{end_year}")
        
        success_count = 0
        for year in range(start_year, end_year + 1):
            if self.collect_season_data(year):
                success_count += 1
            time.sleep(2)  # Rate limiting
        
        print(f"✅ Completed data collection: {success_count}/{end_year - start_year + 1} seasons")

def main():
    """Test the Pro-Football-Reference collector"""
    collector = ProFootballReferenceCollector()
    
    # Test with one season first
    print("🧪 Testing Pro-Football-Reference data collection...")
    success = collector.collect_season_data(2023)
    
    if success:
        print("✅ Test successful! Ready for full collection.")
    else:
        print("❌ Test failed. Check the implementation.")

if __name__ == "__main__":
    main()
