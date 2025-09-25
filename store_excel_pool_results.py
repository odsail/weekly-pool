#!/usr/bin/env python3
"""
Store parsed Excel pool results in the database with proper team mapping.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from database_manager import DatabaseManager
from datetime import datetime
import re

def store_excel_pool_results():
    """Store parsed Excel pool results in database"""
    
    print("💾 Storing Excel Pool Results in Database")
    print("=" * 50)
    
    db_manager = DatabaseManager(version="v2")
    
    # Team abbreviation mapping
    team_mapping = {
        'PHI': 'Philadelphia Eagles', 'DAL': 'Dallas Cowboys', 'KC': 'Kansas City Chiefs',
        'LAC': 'Los Angeles Chargers', 'TB': 'Tampa Bay Buccaneers', 'ATL': 'Atlanta Falcons',
        'PIT': 'Pittsburgh Steelers', 'NYJ': 'New York Jets', 'MIA': 'Miami Dolphins',
        'IND': 'Indianapolis Colts', 'CAR': 'Carolina Panthers', 'JAX': 'Jacksonville Jaguars',
        'NYG': 'New York Giants', 'WAS': 'Washington Commanders', 'ARI': 'Arizona Cardinals',
        'NO': 'New Orleans Saints', 'CIN': 'Cincinnati Bengals', 'CLE': 'Cleveland Browns',
        'LV': 'Las Vegas Raiders', 'NE': 'New England Patriots', 'SF': 'San Francisco 49ers',
        'SEA': 'Seattle Seahawks', 'TEN': 'Tennessee Titans', 'DEN': 'Denver Broncos',
        'DET': 'Detroit Lions', 'GB': 'Green Bay Packers', 'HOU': 'Houston Texans',
        'LAR': 'Los Angeles Rams', 'BAL': 'Baltimore Ravens', 'BUF': 'Buffalo Bills',
        'MIN': 'Minnesota Vikings', 'CHI': 'Chicago Bears'
    }
    
    # Process each week
    for week in [1, 2, 3]:
        excel_file = f"data/results/week{week}.xlsx"
        
        if os.path.exists(excel_file):
            print(f"\n📁 Processing Week {week}...")
            store_week_data(db_manager, excel_file, week, team_mapping)
        else:
            print(f"❌ File not found: {excel_file}")
    
    print("\n✅ Excel data storage complete!")

def store_week_data(db_manager, excel_file, week, team_mapping):
    """Store data for a single week"""
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        
        print(f"  📋 Processing {len(df)} participants")
        
        # Get game columns (exclude first column which is participant names)
        game_columns = [col for col in df.columns if col != 'Week 4' and col != 'TIE PTS']
        
        print(f"  🏈 Found {len(game_columns)} games")
        
        # Process each participant
        for idx, row in df.iterrows():
            participant_name = row['Week 4']
            
            if pd.isna(participant_name) or participant_name == '':
                continue
                
            print(f"    👤 Processing {participant_name}...")
            
            # Process each game
            for game_col in game_columns:
                pick_value = row[game_col]
                
                if pd.isna(pick_value) or pick_value == '':
                    continue
                
                # Parse pick and confidence
                pick_info = parse_pick_value(pick_value, team_mapping)
                
                if pick_info:
                    # Get game info
                    game_info = parse_game_info(game_col, team_mapping)
                    
                    if game_info:
                        # Store in database
                        store_pick_in_database(db_manager, participant_name, week, 
                                             game_info, pick_info)
        
    except Exception as e:
        print(f"  ❌ Error processing {excel_file}: {e}")

def parse_pick_value(pick_value, team_mapping):
    """Parse pick value like 'PHI (16)' into team and confidence"""
    
    try:
        # Extract team abbreviation and confidence
        match = re.match(r'([A-Z]{2,4})\s*\((\d+)\)', str(pick_value))
        
        if match:
            team_abbr = match.group(1)
            confidence = int(match.group(2))
            
            # Map abbreviation to full team name
            team_name = team_mapping.get(team_abbr)
            
            if team_name:
                return {
                    'team_abbr': team_abbr,
                    'team_name': team_name,
                    'confidence': confidence
                }
        
        return None
        
    except Exception as e:
        print(f"      ❌ Error parsing pick value '{pick_value}': {e}")
        return None

def parse_game_info(game_col, team_mapping):
    """Parse game column like 'DAL @ PHI' into home and away teams"""
    
    try:
        # Split by @ or vs
        if '@' in game_col:
            parts = game_col.split('@')
        elif 'vs' in game_col:
            parts = game_col.split('vs')
        else:
            return None
        
        if len(parts) != 2:
            return None
        
        away_abbr = parts[0].strip()
        home_abbr = parts[1].strip()
        
        away_team = team_mapping.get(away_abbr)
        home_team = team_mapping.get(home_abbr)
        
        if away_team and home_team:
            return {
                'away_team': away_team,
                'home_team': home_team,
                'away_abbr': away_abbr,
                'home_abbr': home_abbr
            }
        
        return None
        
    except Exception as e:
        print(f"      ❌ Error parsing game info '{game_col}': {e}")
        return None

def store_pick_in_database(db_manager, participant_name, week, game_info, pick_info):
    """Store a single pick in the database"""
    
    try:
        # Get game ID
        game_id = db_manager.get_game_id(2025, week, game_info['home_team'], game_info['away_team'])
        
        if not game_id:
            print(f"      ❌ Game not found: {game_info['away_team']} @ {game_info['home_team']}")
            return
        
        # Get team ID for the picked team
        pick_team_id = db_manager.get_team_id(pick_info['team_name'])
        
        if not pick_team_id:
            print(f"      ❌ Team not found: {pick_info['team_name']}")
            return
        
        # Store in pool_results table
        db_manager.insert_pool_result(
            season_year=2025,
            week=week,
            participant_name=participant_name,
            game_id=game_id,
            pick_team_id=pick_team_id,
            confidence_points=pick_info['confidence'],
            is_correct=None,  # Will be updated after games are played
            total_weekly_score=None,
            weekly_rank=None
        )
        
        print(f"      ✅ Stored: {pick_info['team_name']} ({pick_info['confidence']} pts)")
        
    except Exception as e:
        print(f"      ❌ Error storing pick: {e}")

if __name__ == "__main__":
    store_excel_pool_results()

