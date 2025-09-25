#!/usr/bin/env python3
"""
Fetch current DraftKings odds for Week 3 games
"""

import requests
import json
from database_manager import DatabaseManager
from datetime import datetime

def fetch_current_odds():
    """Fetch current odds from The Odds API for Week 3"""
    
    print("📡 Fetching current DraftKings odds for Week 3...")
    
    # The Odds API endpoint
    url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/"
    
    # API parameters
    params = {
        'apiKey': 'your_api_key_here',  # You'll need to add your actual API key
        'regions': 'us',
        'markets': 'h2h,spreads,totals',
        'oddsFormat': 'american',
        'dateFormat': 'iso'
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Fetched {len(data)} games from The Odds API")
            
            # Process and store odds
            db = DatabaseManager(version="v2")
            stored_count = 0
            
            for game in data:
                # Extract game info
                home_team = game['home_team']
                away_team = game['away_team']
                commence_time = game['commence_time']
                
                # Find matching game in database
                game_id = db.get_game_id(2025, 3, home_team, away_team)
                
                if game_id:
                    # Extract DraftKings odds
                    dk_odds = None
                    for bookmaker in game.get('bookmakers', []):
                        if bookmaker['title'] == 'DraftKings':
                            dk_odds = bookmaker
                            break
                    
                    if dk_odds:
                        # Extract H2H odds
                        h2h_odds = None
                        for market in dk_odds.get('markets', []):
                            if market['key'] == 'h2h':
                                h2h_odds = market
                                break
                        
                        if h2h_odds:
                            home_ml = None
                            away_ml = None
                            
                            for outcome in h2h_odds.get('outcomes', []):
                                if outcome['name'] == home_team:
                                    home_ml = outcome['price']
                                elif outcome['name'] == away_team:
                                    away_ml = outcome['price']
                            
                            if home_ml and away_ml:
                                # Store odds in database
                                try:
                                    db.insert_odds(
                                        game_id=game_id,
                                        bookmaker='DraftKings',
                                        home_ml=home_ml,
                                        away_ml=away_ml,
                                        total_points=None,  # Could extract from totals market
                                        timestamp=datetime.now().isoformat()
                                    )
                                    stored_count += 1
                                    print(f"✅ Stored odds: {away_team} @ {home_team} (Home: {home_ml}, Away: {away_ml})")
                                except Exception as e:
                                    print(f"❌ Error storing odds for {away_team} @ {home_team}: {e}")
                        else:
                            print(f"⚠️  No H2H odds found for {away_team} @ {home_team}")
                    else:
                        print(f"⚠️  No DraftKings odds found for {away_team} @ {home_team}")
                else:
                    print(f"⚠️  Game not found in database: {away_team} @ {home_team}")
            
            print(f"\n✅ Successfully stored {stored_count} sets of odds")
            return stored_count > 0
            
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching odds: {e}")
        return False

def manual_odds_check():
    """Manual check of what odds should be for key games"""
    
    print("\n🔍 Manual Odds Check (What they should be):")
    print("=" * 50)
    
    # Key games that should have clear favorites
    key_games = [
        ("Miami Dolphins", "Buffalo Bills", "Bills should be heavy favorites"),
        ("Detroit Lions", "Baltimore Ravens", "Ravens should be favorites"),
        ("Kansas City Chiefs", "New York Giants", "Chiefs should be heavy favorites"),
        ("San Francisco 49ers", "Arizona Cardinals", "49ers should be favorites")
    ]
    
    for away, home, expected in key_games:
        print(f"{away} @ {home}: {expected}")

if __name__ == "__main__":
    print("🎯 Current Odds Fetcher for Week 3")
    print("=" * 40)
    
    # Show what odds should look like
    manual_odds_check()
    
    # Note about API key
    print(f"\n⚠️  Note: You need to add your The Odds API key to fetch real odds")
    print(f"Without real odds, the model uses default -110 for all teams")
    print(f"This explains why Miami Dolphins got 16 confidence points over Buffalo Bills!")
    
    # Uncomment to actually fetch odds (requires API key)
    # fetch_current_odds()


