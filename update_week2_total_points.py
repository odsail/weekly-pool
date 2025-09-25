#!/usr/bin/env python3
"""
Update Week 2 games with missing total points data from the original picks
"""

import sqlite3
import pandas as pd

def update_week2_total_points():
    """Update the database with total points data from Week 2 picks"""
    
    print("🔧 Updating Week 2 total points data...")
    
    # Read the original Week 2 picks data
    picks_df = pd.read_csv("data/outputs/2025/week-week2-picks.csv")
    
    # Connect to database
    conn = sqlite3.connect("data/nfl_pool_v2.db")
    cursor = conn.cursor()
    
    updated_count = 0
    
    for _, row in picks_df.iterrows():
        away_team = row['away_team']
        home_team = row['home_team']
        total_points = row['total_points']
        
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
            
            # Update the odds table with total points
            cursor.execute("""
                UPDATE odds 
                SET total_points = ? 
                WHERE game_id = ?
            """, (total_points, game_id))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"✅ Updated {away_team} @ {home_team}: {total_points} total points")
            else:
                print(f"⚠️  No odds record found for {away_team} @ {home_team}")
        else:
            print(f"❌ Game not found: {away_team} @ {home_team}")
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 Updated {updated_count} games with total points data")
    
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
    print("-" * 50)
    for home_team, away_team, home_score, away_score, total_points in results:
        actual_total = home_score + away_score if home_score is not None and away_score is not None else "N/A"
        print(f"{away_team} @ {home_team}: {home_score}-{away_score} (Total: {actual_total}, O/U: {total_points})")
    
    conn.close()

if __name__ == "__main__":
    update_week2_total_points()


