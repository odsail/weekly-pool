#!/usr/bin/env python3
"""
Create odds records for Week 2 games with total points data
"""

import sqlite3
import pandas as pd
from datetime import datetime

def create_week2_odds_records():
    """Create odds records for Week 2 games with total points data"""
    
    print("🔧 Creating Week 2 odds records with total points...")
    
    # Read the original Week 2 picks data
    picks_df = pd.read_csv("data/outputs/2025/week-week2-picks.csv")
    
    # Connect to database
    conn = sqlite3.connect("data/nfl_pool_v2.db")
    cursor = conn.cursor()
    
    created_count = 0
    
    for _, row in picks_df.iterrows():
        away_team = row['away_team']
        home_team = row['home_team']
        away_ml = row['away_ml']
        home_ml = row['home_ml']
        total_points = row['total_points']
        bookmaker = row['bookmaker']
        
        # Find the game in the database
        cursor.execute("""
            SELECT g.id 
            FROM games g 
            JOIN teams ht ON g.home_team_id = ht.id 
            JOIN teams at ON g.away_team_id = at.id 
            WHERE g.season_year = 2025 
            AND g.week = 2 
            AND ht.name = ? 
            AND at.name = ?
        """, (home_team, away_team))
        
        game_result = cursor.fetchone()
        if game_result:
            game_id = game_result[0]
            
            # Create odds record
            cursor.execute("""
                INSERT INTO odds (game_id, bookmaker, home_ml, away_ml, total_points, home_win_prob, away_win_prob, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (game_id, bookmaker, home_ml, away_ml, total_points, 
                  row['home_prob'], row['away_prob'], datetime.now().isoformat()))
            
            created_count += 1
            print(f"✅ Created odds for {away_team} @ {home_team}: O/U {total_points}")
        else:
            print(f"❌ Game not found: {away_team} @ {home_team}")
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 Created {created_count} odds records with total points data")
    
    # Verify the updates
    print("\n🔍 Verifying updates...")
    conn = sqlite3.connect("data/nfl_pool_v2.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ht.name as home_team, at.name as away_team, g.home_score, g.away_score, o.total_points
        FROM games g 
        JOIN teams ht ON g.home_team_id = ht.id 
        JOIN teams at ON g.away_team_id = at.id 
        LEFT JOIN odds o ON g.id = o.game_id 
        WHERE g.season_year = 2025 AND g.week = 2 
        ORDER BY g.game_date
    """)
    
    results = cursor.fetchall()
    
    print("\n📋 Week 2 Games with Total Points:")
    print("-" * 60)
    for home_team, away_team, home_score, away_score, total_points in results:
        actual_total = home_score + away_score if home_score is not None and away_score is not None else "N/A"
        over_under_result = ""
        if total_points and actual_total != "N/A":
            if actual_total > total_points:
                over_under_result = " (OVER ✅)"
            elif actual_total < total_points:
                over_under_result = " (UNDER ❌)"
            else:
                over_under_result = " (PUSH)"
        print(f"{away_team} @ {home_team}: {home_score}-{away_score} (Total: {actual_total}, O/U: {total_points}){over_under_result}")
    
    conn.close()

if __name__ == "__main__":
    create_week2_odds_records()


