#!/usr/bin/env python3
"""
Parse CSV pool results with correct understanding:
- Positive numbers = Correct pick (team won)
- Negative numbers = Incorrect pick (team lost)
- Blank entries = Missed pick (loses 16 points)
"""

import pandas as pd
import re
import os
from database_manager import DatabaseManager

# Initialize DatabaseManager
db_manager = DatabaseManager('data/nfl_pool_v2.db')

# Mapping for team abbreviations to full names
TEAM_ABBR_MAP = {
    "PHI": "Philadelphia Eagles", "DAL": "Dallas Cowboys",
    "KC": "Kansas City Chiefs", "LAC": "Los Angeles Chargers",
    "TB": "Tampa Bay Buccaneers", "ATL": "Atlanta Falcons",
    "PIT": "Pittsburgh Steelers", "NYJ": "New York Jets",
    "MIA": "Miami Dolphins", "IND": "Indianapolis Colts",
    "CAR": "Carolina Panthers", "JAX": "Jacksonville Jaguars",
    "NYG": "New York Giants", "WAS": "Washington Commanders",
    "ARI": "Arizona Cardinals", "NO": "New Orleans Saints",
    "CIN": "Cincinnati Bengals", "CLE": "Cleveland Browns",
    "LV": "Las Vegas Raiders", "NE": "New England Patriots",
    "SF": "San Francisco 49ers", "SEA": "Seattle Seahawks",
    "TEN": "Tennessee Titans", "DEN": "Denver Broncos",
    "DET": "Detroit Lions", "GB": "Green Bay Packers",
    "HOU": "Houston Texans", "LAR": "Los Angeles Rams",
    "BAL": "Baltimore Ravens", "BUF": "Buffalo Bills",
    "MIN": "Minnesota Vikings", "CHI": "Chicago Bears"
}

def parse_csv_pool_results(file_path: str, week: int) -> dict:
    """
    Parse CSV file containing NFL confidence pool results.
    Format: Participant,Game1,Game2,...,TIE PTS
    Each game cell contains "Team (Confidence)" or "Team (-Confidence)" for incorrect picks
    """
    print(f"  📋 Parsing Week {week} CSV: {file_path}")
    
    # Read CSV file
    df = pd.read_csv(file_path)
    print(f"  📋 CSV loaded: {len(df)} rows, {len(df.columns)} columns")
    print(f"  📋 Columns: {df.columns.tolist()}")
    
    # First column is participant names, last column is TIE PTS
    participant_col = df.columns[0]
    game_cols = df.columns[1:-1]  # Exclude participant and TIE PTS columns
    
    print(f"  🔍 Found {len(game_cols)} games for Week {week}")
    
    results = {}
    
    for index, row in df.iterrows():
        participant_name = row[participant_col]
        if pd.isna(participant_name):
            continue
            
        participant_picks = []
        
        for game_col in game_cols:
            pick_str = str(row[game_col])
            
            if pd.isna(pick_str) or pick_str.strip() == '' or pick_str == 'nan':
                # This is a missed pick
                participant_picks.append({
                    'game': game_col,
                    'pick_team_abbr': None,
                    'confidence_points': 16,  # Highest confidence for missed pick
                    'is_correct': False  # Missed picks are incorrect
                })
                continue
            
            # Parse "Team (Confidence)" or "Team (-Confidence)" format
            # Handle cases like "KC -(9)" where there's a space before the negative
            match = re.match(r"([A-Z]{2,4})\s*\(?\s*(-?\d+)\s*\)?", pick_str)
            if match:
                pick_team_abbr = match.group(1)
                confidence = int(match.group(2))
                
                # Determine if correct based on sign
                is_correct = confidence > 0
                confidence_points = abs(confidence)  # Store absolute value
                
                participant_picks.append({
                    'game': game_col,
                    'pick_team_abbr': pick_team_abbr,
                    'confidence_points': confidence_points,
                    'is_correct': is_correct
                })
            else:
                print(f"    ⚠️ Could not parse pick for {participant_name}, game {game_col}: {pick_str}")
        
        results[participant_name] = participant_picks
    
    return results

def store_csv_pool_results(season_year: int, week: int, csv_file_path: str):
    """
    Parse CSV pool results and store them in the database with correct outcomes.
    """
    print(f"\n📁 Processing Week {week} from CSV...")
    parsed_data = parse_csv_pool_results(csv_file_path, week)
    
    if not parsed_data:
        print(f"  ❌ No data parsed for Week {week} from {csv_file_path}")
        return
    
    print(f"  📋 Processing {len(parsed_data)} participants")
    
    # Get all games for the week to match against
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.id, ht.name as home_team, at.name as away_team
            FROM games g
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            WHERE g.season_year = ? AND g.week = ?
        """, (season_year, week))
        
        games_for_week = []
        for row in cursor.fetchall():
            games_for_week.append({
                'id': row[0],
                'home_team': row[1], 
                'away_team': row[2]
            })
    
    game_lookup = {}
    for game in games_for_week:
        # Store in both 'Home @ Away' and 'Away @ Home' format for robust lookup
        game_lookup[f"{game['home_team']} @ {game['away_team']}"] = game['id']
        game_lookup[f"{game['away_team']} @ {game['home_team']}"] = game['id']
    
    # Extract game matchups from the parsed data
    excel_game_names = []
    if parsed_data:
        first_participant_picks = next(iter(parsed_data.values()))
        excel_game_names = [p['game'] for p in first_participant_picks if 'game' in p]
    
    # Map Excel game names to database game IDs
    db_game_ids_map = {}
    for excel_game_name in excel_game_names:
        # Excel game name format: "AWAY @ HOME"
        parts = excel_game_name.split(' @ ')
        if len(parts) == 2:
            away_abbr, home_abbr = parts[0], parts[1]
            away_team_name = TEAM_ABBR_MAP.get(away_abbr, away_abbr)
            home_team_name = TEAM_ABBR_MAP.get(home_abbr, home_abbr)
            
            # Try to find game in DB using both possible formats
            game_id = db_manager.get_game_id(season_year, week, home_team_name, away_team_name)
            if not game_id:
                # Try reversed order if not found
                game_id = db_manager.get_game_id(season_year, week, away_team_name, home_team_name)
            
            if game_id:
                db_game_ids_map[excel_game_name] = game_id
            else:
                print(f"  ⚠️ Could not find game ID for Excel game: {excel_game_name} (Home: {home_team_name}, Away: {away_team_name})")
    
    print(f"  🏈 Found {len(db_game_ids_map)} games")
    
    # Clear existing data for this week first
    print(f"  🗑️ Clearing existing Week {week} data...")
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pool_results WHERE season_year = ? AND week = ?", (season_year, week))
        deleted_count = cursor.rowcount
        print(f"    🗑️ Deleted {deleted_count} existing records")
    
    # Store new data
    for participant_name, picks in parsed_data.items():
        print(f"    👤 Processing {participant_name}...")
        stored_count = 0
        
        for pick_data in picks:
            excel_game_name = pick_data['game']
            pick_team_abbr = pick_data.get('pick_team_abbr')
            confidence_points = pick_data['confidence_points']
            is_correct = pick_data['is_correct']
            
            game_id = db_game_ids_map.get(excel_game_name)
            
            if not game_id:
                print(f"      ❌ Skipping pick for {participant_name} - Game ID not found for {excel_game_name}")
                continue
            
            pick_team_id = None
            if pick_team_abbr:
                pick_team_name = TEAM_ABBR_MAP.get(pick_team_abbr, pick_team_abbr)
                pick_team_id = db_manager.get_team_id(pick_team_name)
                if not pick_team_id:
                    print(f"      ⚠️ Team ID not found for pick team: {pick_team_name} (Abbr: {pick_team_abbr})")
                    continue
            else:
                # For missed picks, set pick_team_id to NULL
                pick_team_id = None
            
            # Calculate weekly score and rank (will be updated later)
            total_weekly_score = None
            weekly_rank = None
            
            # Insert the pick
            db_manager.insert_pool_result(
                season_year=season_year,
                week=week,
                participant_name=participant_name,
                game_id=game_id,
                pick_team_id=pick_team_id,  # Can be None for missed picks
                confidence_points=confidence_points,
                is_correct=is_correct,
                total_weekly_score=total_weekly_score,
                weekly_rank=weekly_rank
            )
            stored_count += 1
            
            if pick_team_abbr:
                status = "✅" if is_correct else "❌"
                print(f"      {status} Stored: {pick_team_name} ({confidence_points} pts)")
            else:
                print(f"      ❌ Stored: MISSED PICK ({confidence_points} pts)")
        
        print(f"      💾 Stored {stored_count} picks for {participant_name}")

def analyze_consensus_failures(season_year: int, week: int):
    """
    Analyze games where everyone picked a team that lost (consensus failures).
    """
    print(f"\n🔍 Analyzing Week {week} Consensus Failures...")
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get all picks for this week grouped by game
        cursor.execute("""
            SELECT 
                g.id as game_id,
                ht.name || ' @ ' || at.name as game,
                pr.pick_team_id,
                t.name as pick_team,
                pr.is_correct,
                COUNT(*) as pick_count,
                SUM(CASE WHEN pr.is_correct = 1 THEN 1 ELSE 0 END) as correct_count,
                SUM(CASE WHEN pr.is_correct = 0 THEN 1 ELSE 0 END) as incorrect_count
            FROM pool_results pr
            JOIN games g ON pr.game_id = g.id
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            JOIN teams t ON pr.pick_team_id = t.id
            WHERE pr.season_year = ? AND pr.week = ?
            GROUP BY g.id, pr.pick_team_id
            ORDER BY g.id, pick_count DESC
        """, (season_year, week))
        
        results = cursor.fetchall()
        
        # Group by game
        games = {}
        for result in results:
            game_id, game, pick_team_id, pick_team, is_correct, pick_count, correct_count, incorrect_count = result
            
            if game_id not in games:
                games[game_id] = {
                    'game': game,
                    'picks': []
                }
            
            games[game_id]['picks'].append({
                'pick_team': pick_team,
                'is_correct': is_correct,
                'pick_count': pick_count,
                'correct_count': correct_count,
                'incorrect_count': incorrect_count
            })
        
        # Find consensus failures
        consensus_failures = []
        for game_id, game_data in games.items():
            picks = game_data['picks']
            
            # Sort by pick count to find the most popular pick
            picks.sort(key=lambda x: x['pick_count'], reverse=True)
            
            if picks and picks[0]['pick_count'] > 10:  # If more than 10 people picked the same team
                most_popular = picks[0]
                if most_popular['is_correct'] == 0:  # If the most popular pick was wrong
                    consensus_failures.append({
                        'game': game_data['game'],
                        'popular_pick': most_popular['pick_team'],
                        'pick_count': most_popular['pick_count'],
                        'incorrect_count': most_popular['incorrect_count']
                    })
        
        if consensus_failures:
            print(f"  🚨 Found {len(consensus_failures)} consensus failures in Week {week}:")
            for failure in consensus_failures:
                print(f"    ❌ {failure['game']}: {failure['popular_pick']} ({failure['pick_count']} picks, all wrong)")
        else:
            print(f"  ✅ No major consensus failures found in Week {week}")
        
        return consensus_failures

def main():
    print("🎯 Parsing CSV Pool Results with Correct Logic")
    print("=" * 60)
    
    season_year = 2025
    
    # Process each week
    for week in [1, 2, 3]:
        csv_file = f'data/results/week{week}.csv'
        if os.path.exists(csv_file):
            store_csv_pool_results(season_year, week, csv_file)
            analyze_consensus_failures(season_year, week)
        else:
            print(f"  ❌ CSV file not found: {csv_file}")
    
    print("\n✅ CSV data processing complete!")
    
    # Generate updated performance analysis
    print("\n📊 Generating Updated Performance Analysis...")
    from validate_pool_results import analyze_fundaysunday_performance
    analyze_fundaysunday_performance(db_manager)

if __name__ == "__main__":
    main()
