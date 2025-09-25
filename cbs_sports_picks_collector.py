#!/usr/bin/env python3
"""
Collect NFL expert picks from CBS Sports for ML training data.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

class CBSSportsPicksCollector:
    """Collect expert picks from CBS Sports"""
    
    def __init__(self):
        self.base_url = "https://www.cbssports.com"
        self.picks_url = "https://www.cbssports.com/nfl/picks/experts/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_current_week_picks(self) -> List[Dict]:
        """Get expert picks for current week"""
        print(f"🔍 Fetching CBS Sports expert picks...")
        
        try:
            response = requests.get(self.picks_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for picks data
            picks_data = []
            
            # Try to find the picks table or data structure
            picks_table = soup.find('table', class_='picks-table') or soup.find('div', class_='picks-container')
            
            if picks_table:
                print(f"✅ Found picks table")
                # Parse the table structure
                picks_data = self._parse_picks_table(picks_table)
            else:
                print(f"⚠️  No picks table found, trying alternative parsing...")
                # Try alternative parsing methods
                picks_data = self._parse_alternative_structure(soup)
            
            print(f"📊 Found {len(picks_data)} expert picks")
            return picks_data
            
        except Exception as e:
            print(f"❌ Error fetching picks: {e}")
            return []
    
    def _parse_picks_table(self, table) -> List[Dict]:
        """Parse picks from table structure"""
        picks = []
        
        # Look for rows with game data
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:  # Minimum columns for game info
                try:
                    # Extract game information
                    game_info = self._extract_game_info(cells)
                    if game_info:
                        picks.append(game_info)
                except Exception as e:
                    print(f"⚠️  Error parsing row: {e}")
                    continue
        
        return picks
    
    def _parse_alternative_structure(self, soup) -> List[Dict]:
        """Parse picks from alternative page structure"""
        picks = []
        
        # Look for game containers or cards
        game_containers = soup.find_all(['div', 'section'], class_=re.compile(r'game|pick|matchup'))
        
        for container in game_containers:
            try:
                game_info = self._extract_game_from_container(container)
                if game_info:
                    picks.append(game_info)
            except Exception as e:
                print(f"⚠️  Error parsing container: {e}")
                continue
        
        return picks
    
    def _extract_game_info(self, cells) -> Optional[Dict]:
        """Extract game information from table cells"""
        # This is a placeholder - actual implementation depends on CBS structure
        # Look for team names, scores, analyst picks, etc.
        
        if len(cells) < 3:
            return None
        
        # Try to identify team names
        team_names = []
        for cell in cells:
            text = cell.get_text(strip=True)
            if self._is_team_name(text):
                team_names.append(text)
        
        if len(team_names) >= 2:
            return {
                'away_team': team_names[0],
                'home_team': team_names[1],
                'analysts': self._extract_analyst_picks(cells),
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def _extract_game_from_container(self, container) -> Optional[Dict]:
        """Extract game information from container element"""
        # Look for team names in the container
        team_elements = container.find_all(['span', 'div', 'h3'], class_=re.compile(r'team|name'))
        
        team_names = []
        for element in team_elements:
            text = element.get_text(strip=True)
            if self._is_team_name(text):
                team_names.append(text)
        
        if len(team_names) >= 2:
            return {
                'away_team': team_names[0],
                'home_team': team_names[1],
                'analysts': self._extract_analyst_picks_from_container(container),
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def _is_team_name(self, text: str) -> bool:
        """Check if text looks like an NFL team name"""
        # Common NFL team name patterns
        team_indicators = [
            'Chiefs', 'Ravens', 'Bills', 'Dolphins', 'Patriots', 'Jets',
            'Steelers', 'Browns', 'Bengals', 'Colts', 'Titans', 'Jaguars',
            'Texans', 'Broncos', 'Chargers', 'Raiders', 'Cowboys', 'Eagles',
            'Giants', 'Commanders', 'Packers', 'Vikings', 'Bears', 'Lions',
            'Buccaneers', 'Saints', 'Falcons', 'Panthers', '49ers', 'Rams',
            'Seahawks', 'Cardinals'
        ]
        
        return any(indicator in text for indicator in team_indicators)
    
    def _extract_analyst_picks(self, cells) -> List[Dict]:
        """Extract analyst picks from table cells"""
        # This would parse the actual analyst picks
        # For now, return placeholder data
        return [
            {'analyst': 'Expert 1', 'pick': 'Home', 'confidence': 'High'},
            {'analyst': 'Expert 2', 'pick': 'Away', 'confidence': 'Medium'}
        ]
    
    def _extract_analyst_picks_from_container(self, container) -> List[Dict]:
        """Extract analyst picks from container"""
        # Look for analyst information
        analyst_elements = container.find_all(['div', 'span'], class_=re.compile(r'analyst|expert|pick'))
        
        analysts = []
        for element in analyst_elements:
            text = element.get_text(strip=True)
            if 'Expert' in text or 'Analyst' in text:
                analysts.append({
                    'analyst': text,
                    'pick': 'Unknown',
                    'confidence': 'Unknown'
                })
        
        return analysts
    
    def save_picks_to_database(self, picks: List[Dict], week: int, season: int):
        """Save picks to database for ML training"""
        from database_manager import DatabaseManager
        
        db_manager = DatabaseManager(version="v2")
        
        print(f"💾 Saving {len(picks)} expert picks to database...")
        
        for pick_data in picks:
            try:
                # Get or create game
                game_id = db_manager.upsert_game(
                    season_year=season,
                    week=week,
                    home_team=pick_data['home_team'],
                    away_team=pick_data['away_team'],
                    game_date=datetime.now().strftime('%Y-%m-%d')
                )
                
                # Store analyst picks as synthetic training data
                for analyst in pick_data['analysts']:
                    # Convert analyst pick to confidence points
                    confidence_points = self._convert_confidence_to_points(analyst['confidence'])
                    
                    # Determine pick team
                    pick_team = pick_data['home_team'] if analyst['pick'] == 'Home' else pick_data['away_team']
                    pick_team_id = db_manager.get_team_id(pick_team)
                    
                    if pick_team_id:
                        # Store as synthetic pick for training
                        db_manager.insert_pick(
                            game_id=game_id,
                            season_year=season,
                            week=week,
                            pick_team_id=pick_team_id,
                            confidence_points=confidence_points,
                            win_probability=0.5 + (confidence_points - 8) * 0.05,  # Rough conversion
                            total_points_prediction=45.0,  # Default
                            is_correct=None  # Will be updated later
                        )
                
            except Exception as e:
                print(f"⚠️  Error saving pick: {e}")
                continue
        
        print(f"✅ Saved expert picks to database")
    
    def _convert_confidence_to_points(self, confidence: str) -> int:
        """Convert confidence level to points"""
        confidence_lower = confidence.lower()
        
        if 'high' in confidence_lower:
            return 14
        elif 'medium' in confidence_lower:
            return 8
        elif 'low' in confidence_lower:
            return 3
        else:
            return 8  # Default medium confidence

def main():
    """Test CBS Sports picks collection"""
    collector = CBSSportsPicksCollector()
    
    print("🧪 Testing CBS Sports picks collection...")
    
    # Get current week picks
    picks = collector.get_current_week_picks()
    
    if picks:
        print(f"✅ Successfully collected {len(picks)} picks")
        
        # Show sample data
        for i, pick in enumerate(picks[:3]):
            print(f"\n📋 Sample Pick {i+1}:")
            print(f"   Game: {pick['away_team']} @ {pick['home_team']}")
            print(f"   Analysts: {len(pick['analysts'])}")
            for analyst in pick['analysts']:
                print(f"     - {analyst['analyst']}: {analyst['pick']} ({analyst['confidence']})")
        
        # Save to database (commented out for testing)
        # collector.save_picks_to_database(picks, week=1, season=2024)
        
    else:
        print("❌ No picks collected")
    
    print("\n💡 Next steps:")
    print("   1. Verify the data structure matches expectations")
    print("   2. Implement proper parsing for CBS Sports format")
    print("   3. Collect historical picks data")
    print("   4. Integrate with ML training pipeline")

if __name__ == "__main__":
    main()


