#!/usr/bin/env python3
"""
Update picks with actual game results to enable ML training.
"""
import json
import os
from database_manager import DatabaseManager

def update_week1_results():
    """Update Week 1 picks with actual results from analysis data"""
    db = DatabaseManager()
    
    # Load Week 1 analysis data
    analysis_file = "data/analysis/2025/week1-analysis.json"
    if not os.path.exists(analysis_file):
        print(f"❌ Analysis file not found: {analysis_file}")
        return False
    
    with open(analysis_file, 'r') as f:
        analysis = json.load(f)
    
    print("🔄 Updating Week 1 picks with actual results...")
    
    # Get all Week 1 picks
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.game_id, p.pick_team_id, p.confidence_points,
                   ht.name as home_team, at.name as away_team, pt.name as pick_team
            FROM picks p
            JOIN games g ON p.game_id = g.id
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            JOIN teams pt ON p.pick_team_id = pt.id
            WHERE p.season_year = 2025 AND p.week = 1
        """)
        picks = cursor.fetchall()
    
    print(f"📊 Found {len(picks)} Week 1 picks to update")
    
    # Update each pick with result
    updated_count = 0
    for pick_id, game_id, pick_team_id, confidence_points, home_team, away_team, pick_team in picks:
        # Find the corresponding game in analysis data
        game_analysis = None
        for game in analysis.get('games_analyzed', []):
            if (game['teams']['home'] == home_team and 
                game['teams']['away'] == away_team):
                game_analysis = game
                break
        
        if game_analysis:
            # Check if pick was correct
            actual_winner = game_analysis['actual']['winner']
            is_correct = (pick_team == actual_winner)
            
            # Update the pick
            db.update_pick_result(pick_id, is_correct)
            updated_count += 1
            
            print(f"   {pick_team} vs {actual_winner} -> {'✅' if is_correct else '❌'}")
        else:
            print(f"   ⚠️  No analysis data for {away_team} @ {home_team}")
    
    print(f"✅ Updated {updated_count} picks with results")
    return updated_count > 0

def main():
    """Update picks with results"""
    success = update_week1_results()
    
    if success:
        print("\n🎉 Pick results updated successfully!")
        print("💡 Now you can train the ML model: python ml_model.py")
    else:
        print("❌ Failed to update pick results")

if __name__ == "__main__":
    main()
