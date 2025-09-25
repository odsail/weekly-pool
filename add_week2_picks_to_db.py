#!/usr/bin/env python3
"""
Add original Week 2 picks to the database
"""

import pandas as pd
from database_manager import DatabaseManager
import re

def add_week2_picks_to_database():
    """Add original Week 2 picks to the database"""
    
    # Initialize database
    db = DatabaseManager(version="v2")
    
    print("🔄 Adding original Week 2 picks to database...")
    
    # Read the original Week 2 picks from the CSV file
    picks_file = "data/outputs/2025/week-week2-picks.csv"
    
    # Read CSV file
    df = pd.read_csv(picks_file)
    picks_data = []
    
    for _, row in df.iterrows():
        picks_data.append({
            'points': int(row['confidence_points']),
            'pick': row['pick_team'],
            'win_pct': float(row['pick_prob']) * 100,
            'home_team': row['home_team'],
            'away_team': row['away_team']
        })
    
    print(f"📊 Found {len(picks_data)} original Week 2 picks")
    
    # Get Week 2 games from database
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.id, ht.name as home_team, at.name as away_team
            FROM games g
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            WHERE g.season_year = 2025 AND g.week = 2
        """)
        games = cursor.fetchall()
    
    print(f"📊 Found {len(games)} Week 2 games in database")
    
    # Match picks to games and insert
    inserted_count = 0
    for pick_data in picks_data:
        # Find matching game
        matching_game = None
        for game in games:
            game_id, home_team, away_team = game
            if (pick_data['home_team'] == home_team and 
                pick_data['away_team'] == away_team):
                matching_game = game
                break
        
        if matching_game:
            game_id, home_team, away_team = matching_game
            
            # Insert the pick
            try:
                db.insert_pick(
                    game_id=game_id,
                    season_year=2025,
                    week=2,
                    pick_team=pick_data['pick'],
                    confidence_points=pick_data['points'],
                    win_probability=pick_data['win_pct'] / 100.0,
                    total_points_prediction=None
                )
                inserted_count += 1
                print(f"✅ Added pick: {pick_data['pick']} (Conf: {pick_data['points']}) for {away_team} @ {home_team}")
            except Exception as e:
                print(f"❌ Error adding pick for {pick_data['pick']}: {e}")
        else:
            print(f"❌ Could not find matching game for: {pick_data['away_team']} @ {pick_data['home_team']}")
    
    print(f"\n✅ Successfully added {inserted_count} original Week 2 picks to database")
    return inserted_count

if __name__ == "__main__":
    add_week2_picks_to_database()
