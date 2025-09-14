#!/usr/bin/env python3
"""
Migration script to move existing CSV/JSON data to SQLite database.
"""
import os
import json
import pandas as pd
from database_manager import DatabaseManager
import argparse

def populate_teams(db_manager: DatabaseManager):
    """Populate teams table with NFL teams"""
    print("🏈 Populating teams table...")
    
    teams_data = [
        # AFC East
        ("Buffalo Bills", "BUF", "AFC", "East"),
        ("Miami Dolphins", "MIA", "AFC", "East"),
        ("New England Patriots", "NE", "AFC", "East"),
        ("New York Jets", "NYJ", "AFC", "East"),
        
        # AFC North
        ("Baltimore Ravens", "BAL", "AFC", "North"),
        ("Cincinnati Bengals", "CIN", "AFC", "North"),
        ("Cleveland Browns", "CLE", "AFC", "North"),
        ("Pittsburgh Steelers", "PIT", "AFC", "North"),
        
        # AFC South
        ("Houston Texans", "HOU", "AFC", "South"),
        ("Indianapolis Colts", "IND", "AFC", "South"),
        ("Jacksonville Jaguars", "JAX", "AFC", "South"),
        ("Tennessee Titans", "TEN", "AFC", "South"),
        
        # AFC West
        ("Denver Broncos", "DEN", "AFC", "West"),
        ("Kansas City Chiefs", "KC", "AFC", "West"),
        ("Las Vegas Raiders", "LV", "AFC", "West"),
        ("Los Angeles Chargers", "LAC", "AFC", "West"),
        
        # NFC East
        ("Dallas Cowboys", "DAL", "NFC", "East"),
        ("New York Giants", "NYG", "NFC", "East"),
        ("Philadelphia Eagles", "PHI", "NFC", "East"),
        ("Washington Commanders", "WAS", "NFC", "East"),
        
        # NFC North
        ("Chicago Bears", "CHI", "NFC", "North"),
        ("Detroit Lions", "DET", "NFC", "North"),
        ("Green Bay Packers", "GB", "NFC", "North"),
        ("Minnesota Vikings", "MIN", "NFC", "North"),
        
        # NFC South
        ("Atlanta Falcons", "ATL", "NFC", "South"),
        ("Carolina Panthers", "CAR", "NFC", "South"),
        ("New Orleans Saints", "NO", "NFC", "South"),
        ("Tampa Bay Buccaneers", "TB", "NFC", "South"),
        
        # NFC West
        ("Arizona Cardinals", "ARI", "NFC", "West"),
        ("Los Angeles Rams", "LAR", "NFC", "West"),
        ("San Francisco 49ers", "SF", "NFC", "West"),
        ("Seattle Seahawks", "SEA", "NFC", "West"),
    ]
    
    for name, abbreviation, conference, division in teams_data:
        db_manager.upsert_team(name, abbreviation, conference, division)
    
    print(f"✅ Added {len(teams_data)} teams")

def migrate_picks_data(db_manager: DatabaseManager, year: int = 2025):
    """Migrate existing picks CSV data to database"""
    print(f"📊 Migrating picks data for {year}...")
    
    picks_dir = f"data/outputs/{year}"
    if not os.path.exists(picks_dir):
        print(f"❌ No picks directory found: {picks_dir}")
        return
    
    migrated_count = 0
    for filename in os.listdir(picks_dir):
        if filename.startswith("week-week") and filename.endswith("-picks.csv"):
            # Extract week number
            week_str = filename.split("week")[1].split("-")[0]
            try:
                week = int(week_str)
            except ValueError:
                continue
            
            csv_path = os.path.join(picks_dir, filename)
            print(f"   Migrating Week {week} picks...")
            
            try:
                db_manager.migrate_csv_data(csv_path, year, week)
                migrated_count += 1
            except Exception as e:
                print(f"   ❌ Error migrating {filename}: {e}")
    
    print(f"✅ Migrated {migrated_count} weeks of picks data")

def migrate_analysis_data(db_manager: DatabaseManager, year: int = 2025):
    """Migrate existing analysis JSON data to database"""
    print(f"📈 Migrating analysis data for {year}...")
    
    analysis_dir = f"data/analysis/{year}"
    if not os.path.exists(analysis_dir):
        print(f"❌ No analysis directory found: {analysis_dir}")
        return
    
    migrated_count = 0
    for filename in os.listdir(analysis_dir):
        if filename.startswith("week") and filename.endswith("-analysis.json"):
            # Extract week number
            week_str = filename.split("week")[1].split("-")[0]
            try:
                week = int(week_str)
            except ValueError:
                continue
            
            json_path = os.path.join(analysis_dir, filename)
            print(f"   Migrating Week {week} analysis...")
            
            try:
                db_manager.migrate_analysis_data(json_path, year, week)
                migrated_count += 1
            except Exception as e:
                print(f"   ❌ Error migrating {filename}: {e}")
    
    print(f"✅ Migrated {migrated_count} weeks of analysis data")

def migrate_odds_data(db_manager: DatabaseManager, year: int = 2025):
    """Migrate existing odds JSON data to database"""
    print(f"🎲 Migrating odds data for {year}...")
    
    raw_dir = f"data/raw/{year}"
    if not os.path.exists(raw_dir):
        print(f"❌ No raw directory found: {raw_dir}")
        return
    
    migrated_count = 0
    for filename in os.listdir(raw_dir):
        if filename.startswith("week-week") and filename.endswith("-odds.json"):
            # Extract week number
            week_str = filename.split("week")[1].split("-")[0]
            try:
                week = int(week_str)
            except ValueError:
                continue
            
            json_path = os.path.join(raw_dir, filename)
            print(f"   Migrating Week {week} odds...")
            
            try:
                with open(json_path, 'r') as f:
                    odds_data = json.load(f)
                
                # Process each event
                for event in odds_data.get('events', []):
                    # Extract team names
                    home_team = event['home_team']
                    away_team = event['away_team']
                    
                    # Create game
                    game_id = db_manager.upsert_game(
                        year, week, home_team, away_team, 
                        event.get('commence_time', '')
                    )
                    
                    # Process odds for each bookmaker
                    for bookmaker, odds in event.get('bookmakers', {}).items():
                        # H2H odds
                        h2h = odds.get('markets', [{}])[0].get('outcomes', [])
                        home_ml = None
                        away_ml = None
                        home_win_prob = None
                        away_win_prob = None
                        
                        for outcome in h2h:
                            if outcome['name'] == home_team:
                                home_ml = outcome.get('price')
                                home_win_prob = outcome.get('probability')
                            elif outcome['name'] == away_team:
                                away_ml = outcome.get('price')
                                away_win_prob = outcome.get('probability')
                        
                        # Totals
                        totals = odds.get('markets', [{}])[1].get('outcomes', []) if len(odds.get('markets', [])) > 1 else []
                        total_points = None
                        for outcome in totals:
                            if 'over' in outcome.get('name', '').lower():
                                total_points = outcome.get('point')
                                break
                        
                        # Insert odds
                        db_manager.insert_odds(
                            game_id, bookmaker, home_ml, away_ml, total_points,
                            home_win_prob, away_win_prob
                        )
                
                migrated_count += 1
            except Exception as e:
                print(f"   ❌ Error migrating {filename}: {e}")
    
    print(f"✅ Migrated {migrated_count} weeks of odds data")

def main():
    parser = argparse.ArgumentParser(description="Migrate existing data to SQLite database")
    parser.add_argument("--year", type=int, default=2025, help="Year to migrate")
    parser.add_argument("--skip-teams", action="store_true", help="Skip teams population")
    parser.add_argument("--skip-picks", action="store_true", help="Skip picks migration")
    parser.add_argument("--skip-analysis", action="store_true", help="Skip analysis migration")
    parser.add_argument("--skip-odds", action="store_true", help="Skip odds migration")
    
    args = parser.parse_args()
    
    print("🚀 Starting database migration...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Populate teams
    if not args.skip_teams:
        populate_teams(db_manager)
    
    # Migrate data
    if not args.skip_picks:
        migrate_picks_data(db_manager, args.year)
    
    if not args.skip_analysis:
        migrate_analysis_data(db_manager, args.year)
    
    if not args.skip_odds:
        migrate_odds_data(db_manager, args.year)
    
    print("\n🎉 Migration completed!")
    print("💡 Next steps:")
    print("   1. Train ML model: python ml_model.py")
    print("   2. Query database: python -c \"from database_manager import DatabaseManager; db = DatabaseManager(); print(db.get_all_picks_for_ml().head())\"")

if __name__ == "__main__":
    main()
