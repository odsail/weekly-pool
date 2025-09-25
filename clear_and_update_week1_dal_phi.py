#!/usr/bin/env python3
"""
Clear the incorrect template data and update with real picks from the screenshot.
Everyone picked Philadelphia Eagles for DAL @ PHI with different confidence points.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager

def clear_and_update_week1_dal_phi():
    """Clear template data and update with real picks from screenshot"""
    
    db_manager = DatabaseManager(version="v2")
    
    print("🧹 Clearing template data and updating with real picks...")
    print("=" * 60)
    
    # Get the DAL @ PHI game ID
    game_id = db_manager.get_game_id(2025, 1, "Philadelphia Eagles", "Dallas Cowboys")
    if not game_id:
        print("❌ Could not find DAL @ PHI game!")
        return
    
    # Get Philadelphia Eagles team ID
    eagles_team_id = db_manager.get_team_id("Philadelphia Eagles")
    if not eagles_team_id:
        print("❌ Could not find Philadelphia Eagles team!")
        return
    
    print(f"✅ Found game ID: {game_id}")
    print(f"✅ Found Eagles team ID: {eagles_team_id}")
    
    # Real picks from the screenshot (everyone picked PHI with different confidence points)
    real_picks = [
        {"participant": "Raiderjim", "confidence": 14, "total_points": 127},
        {"participant": "Spanish Flies", "confidence": 15, "total_points": 125},
        {"participant": "Big Chuck", "confidence": 15, "total_points": 123},
        {"participant": "Commish", "confidence": 16, "total_points": 121},
        {"participant": "I.P. Daly", "confidence": 16, "total_points": 118},
        {"participant": "Stevie1", "confidence": 16, "total_points": 118},
        {"participant": "Wochie", "confidence": 16, "total_points": 117},
        {"participant": "FundaySunday", "confidence": 16, "total_points": 117},
        {"participant": "Natty Ice", "confidence": 16, "total_points": 113},
        {"participant": "Amusco", "confidence": 16, "total_points": 112},
        {"participant": "LorPor", "confidence": 16, "total_points": 104},
        {"participant": "Poipu Pauly", "confidence": 16, "total_points": 103},
        {"participant": "Sean", "confidence": 16, "total_points": 100},
        {"participant": "Karat Cake", "confidence": 16, "total_points": 95},
        {"participant": "Bijan Mustard", "confidence": 15, "total_points": 89},
        {"participant": "snydermeister", "confidence": 15, "total_points": 83},
        {"participant": "Big daddy", "confidence": 16, "total_points": 77},
        {"participant": "Hails (:)", "confidence": 15, "total_points": 69}
    ]
    
    # Clear existing picks for this game
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM pool_results 
            WHERE season_year = 2025 AND week = 1 AND game_id = ?
        """, (game_id,))
        deleted_count = cursor.rowcount
        print(f"🗑️  Deleted {deleted_count} template picks for DAL @ PHI")
    
    # Insert real picks
    print("\n📝 Inserting real picks from screenshot...")
    for pick in real_picks:
        db_manager.insert_pool_result(
            season_year=2025,
            week=1,
            participant_name=pick["participant"],
            game_id=game_id,
            pick_team_id=eagles_team_id,
            confidence_points=pick["confidence"],
            is_correct=True,  # Philadelphia Eagles won
            total_weekly_score=pick["total_points"],
            weekly_rank=0  # Will be calculated separately
        )
        print(f"  ✅ {pick['participant']}: PHI ({pick['confidence']} pts)")
    
    print(f"\n✅ Updated {len(real_picks)} participants with real picks!")
    
    # Verify the update
    print("\n🔍 Verifying the update...")
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pr.participant_name, t.name as pick_team, pr.confidence_points, pr.is_correct
            FROM pool_results pr
            JOIN teams t ON pr.pick_team_id = t.id
            WHERE pr.season_year = 2025 AND pr.week = 1 AND pr.game_id = ?
            ORDER BY pr.confidence_points DESC
        """, (game_id,))
        
        results = cursor.fetchall()
        
        print(f"\nDAL @ PHI Game Results:")
        print("-" * 50)
        for participant, pick_team, confidence, is_correct in results:
            status = "✅" if is_correct else "❌"
            print(f"{participant:15} | {pick_team:20} | {confidence:2d} pts | {status}")

if __name__ == "__main__":
    clear_and_update_week1_dal_phi()

