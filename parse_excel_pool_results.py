#!/usr/bin/env python3
"""
Parse Excel pool results files and store them in the database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from database_manager import DatabaseManager
from datetime import datetime
import re

def parse_excel_pool_results():
    """Parse Excel files and store pool results in database"""
    
    print("📊 Parsing Excel Pool Results")
    print("=" * 50)
    
    db_manager = DatabaseManager(version="v2")
    
    # Process each week
    for week in [1, 2, 3]:
        excel_file = f"data/results/week{week}.xlsx"
        
        if os.path.exists(excel_file):
            print(f"\n📁 Processing Week {week}...")
            process_week_excel(db_manager, excel_file, week)
        else:
            print(f"❌ File not found: {excel_file}")
    
    print("\n✅ Excel parsing complete!")

def process_week_excel(db_manager, excel_file, week):
    """Process a single week's Excel file"""
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        
        print(f"  📋 Excel file loaded: {len(df)} rows")
        print(f"  📋 Columns: {list(df.columns)}")
        
        # Display first few rows to understand structure
        print(f"  📋 First 3 rows:")
        print(df.head(3).to_string())
        
        # Parse the data based on structure
        parse_week_data(db_manager, df, week)
        
    except Exception as e:
        print(f"  ❌ Error processing {excel_file}: {e}")

def parse_week_data(db_manager, df, week):
    """Parse the data from the DataFrame"""
    
    print(f"\n  🔍 Analyzing Week {week} data structure...")
    
    # Try to identify the structure
    if 'Participant' in df.columns or 'Player' in df.columns or 'Name' in df.columns:
        parse_participant_based_data(db_manager, df, week)
    elif 'Game' in df.columns or 'Matchup' in df.columns:
        parse_game_based_data(db_manager, df, week)
    else:
        # Try to infer structure from first few rows
        print(f"  🔍 Attempting to infer structure...")
        infer_and_parse_data(db_manager, df, week)

def parse_participant_based_data(db_manager, df, week):
    """Parse data where each row is a participant"""
    
    print(f"  👥 Parsing participant-based data for Week {week}")
    
    # Find participant column
    participant_col = None
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['participant', 'player', 'name', 'user']):
            participant_col = col
            break
    
    if not participant_col:
        print(f"  ❌ Could not find participant column")
        return
    
    print(f"  👤 Participant column: {participant_col}")
    
    # Process each participant
    for idx, row in df.iterrows():
        participant_name = row[participant_col]
        
        if pd.isna(participant_name) or participant_name == '':
            continue
            
        print(f"    👤 Processing {participant_name}...")
        
        # Extract picks from the row
        picks = extract_picks_from_row(row, week)
        
        # Store picks in database
        store_participant_picks(db_manager, participant_name, week, picks)

def parse_game_based_data(db_manager, df, week):
    """Parse data where each row is a game"""
    
    print(f"  🏈 Parsing game-based data for Week {week}")
    
    # Find game column
    game_col = None
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['game', 'matchup', 'teams']):
            game_col = col
            break
    
    if not game_col:
        print(f"  ❌ Could not find game column")
        return
    
    print(f"  🏈 Game column: {game_col}")
    
    # Process each game
    for idx, row in df.iterrows():
        game_info = row[game_col]
        
        if pd.isna(game_info) or game_info == '':
            continue
            
        print(f"    🏈 Processing game: {game_info}")
        
        # Extract picks for this game
        game_picks = extract_game_picks_from_row(row, week, game_info)
        
        # Store picks in database
        store_game_picks(db_manager, week, game_picks)

def infer_and_parse_data(db_manager, df, week):
    """Try to infer the data structure and parse accordingly"""
    
    print(f"  🔍 Inferring structure for Week {week}...")
    
    # Look for patterns in column names
    participant_cols = []
    game_cols = []
    pick_cols = []
    confidence_cols = []
    
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['participant', 'player', 'name', 'user']):
            participant_cols.append(col)
        elif any(keyword in col_lower for keyword in ['game', 'matchup', 'teams']):
            game_cols.append(col)
        elif any(keyword in col_lower for keyword in ['pick', 'choice', 'team']):
            pick_cols.append(col)
        elif any(keyword in col_lower for keyword in ['confidence', 'points', 'weight']):
            confidence_cols.append(col)
    
    print(f"  🔍 Found columns:")
    print(f"    👥 Participant: {participant_cols}")
    print(f"    🏈 Game: {game_cols}")
    print(f"    🎯 Pick: {pick_cols}")
    print(f"    📊 Confidence: {confidence_cols}")
    
    # Try different parsing strategies
    if participant_cols:
        # Try to parse as participant-based
        parse_participant_based_data(db_manager, df, week)
    elif game_cols:
        # Try to parse as game-based
        parse_game_based_data(db_manager, df, week)
    else:
        # Try to parse as matrix format
        parse_matrix_format(db_manager, df, week)

def parse_matrix_format(db_manager, df, week):
    """Parse data in matrix format (participants x games)"""
    
    print(f"  📊 Parsing matrix format for Week {week}")
    
    # First row might be games, first column might be participants
    # Or vice versa
    
    # Try to identify games from column headers
    games = []
    for col in df.columns:
        if col and not pd.isna(col):
            # Check if this looks like a game
            if '@' in str(col) or 'vs' in str(col) or 'at' in str(col):
                games.append(col)
    
    if games:
        print(f"  🏈 Found games in columns: {games}")
        parse_matrix_by_games(db_manager, df, week, games)
    else:
        print(f"  🔍 No clear game pattern found, trying alternative parsing...")
        parse_alternative_format(db_manager, df, week)

def parse_matrix_by_games(db_manager, df, week, games):
    """Parse matrix where columns are games"""
    
    print(f"  📊 Parsing matrix with games as columns")
    
    # First column should be participants
    participant_col = df.columns[0]
    
    for idx, row in df.iterrows():
        participant_name = row[participant_col]
        
        if pd.isna(participant_name) or participant_name == '':
            continue
            
        print(f"    👤 Processing {participant_name}...")
        
        # Extract picks for each game
        picks = []
        for game_col in games:
            if game_col in df.columns:
                pick_value = row[game_col]
                if not pd.isna(pick_value) and pick_value != '':
                    picks.append({
                        'game': game_col,
                        'pick': str(pick_value)
                    })
        
        # Store picks
        store_participant_picks(db_manager, participant_name, week, picks)

def parse_alternative_format(db_manager, df, week):
    """Try alternative parsing methods"""
    
    print(f"  🔍 Trying alternative parsing for Week {week}")
    
    # Look for any patterns that might indicate picks
    for idx, row in df.iterrows():
        print(f"    Row {idx}: {dict(row)}")
        
        # Try to extract any meaningful data
        for col, value in row.items():
            if not pd.isna(value) and value != '':
                print(f"      {col}: {value}")

def extract_picks_from_row(row, week):
    """Extract picks from a participant row"""
    
    picks = []
    
    # Look for pick-related columns
    for col, value in row.items():
        if pd.isna(value) or value == '':
            continue
            
        # Check if this looks like a pick
        if any(keyword in col.lower() for keyword in ['pick', 'choice', 'team']):
            picks.append({
                'column': col,
                'pick': str(value)
            })
    
    return picks

def extract_game_picks_from_row(row, week, game_info):
    """Extract picks for a specific game"""
    
    picks = []
    
    # Look for participant columns
    for col, value in row.items():
        if pd.isna(value) or value == '':
            continue
            
        # Check if this looks like a participant
        if any(keyword in col.lower() for keyword in ['participant', 'player', 'name', 'user']):
            picks.append({
                'participant': str(value),
                'game': game_info
            })
    
    return picks

def store_participant_picks(db_manager, participant_name, week, picks):
    """Store picks for a participant"""
    
    print(f"      💾 Storing {len(picks)} picks for {participant_name}")
    
    for pick in picks:
        try:
            # Try to extract game info and confidence
            game_info = pick.get('game', '')
            pick_team = pick.get('pick', '')
            
            # For now, just store the raw data
            # We'll need to map this to actual game IDs later
            print(f"        🎯 {game_info}: {pick_team}")
            
        except Exception as e:
            print(f"        ❌ Error storing pick: {e}")

def store_game_picks(db_manager, week, game_picks):
    """Store picks for a specific game"""
    
    print(f"      💾 Storing {len(game_picks)} picks for game")
    
    for pick in game_picks:
        try:
            participant = pick.get('participant', '')
            game_info = pick.get('game', '')
            
            print(f"        👤 {participant}: {game_info}")
            
        except Exception as e:
            print(f"        ❌ Error storing pick: {e}")

if __name__ == "__main__":
    parse_excel_pool_results()

