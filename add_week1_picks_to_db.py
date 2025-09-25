#!/usr/bin/env python3
"""
Add Week 1 picks to database for retraining
"""

import pandas as pd
from database_manager import DatabaseManager

def add_week1_picks_to_database():
    """Add Week 1 picks from the comparison CSV to database"""
    
    print("📊 Adding Week 1 picks to database...")
    
    db_manager = DatabaseManager(version="v2")
    
    # Load Week 1 comparison data
    df = pd.read_csv('data/outputs/2025/week1-live-ml-comparison.csv')
    
    picks_added = 0
    
    for _, row in df.iterrows():
        try:
            # Parse game string (format: "Away Team @ Home Team")
            game_str = row['game']
            if ' @ ' in game_str:
                away_team, home_team = game_str.split(' @ ')
            else:
                print(f"⚠️  Invalid game format: {game_str}")
                continue
            
            # Get game ID
            game_id = db_manager.get_game_id(2025, 1, home_team, away_team)
            
            if not game_id:
                print(f"⚠️  Game not found: {home_team} vs {away_team}")
                continue
            
            # Insert original pick
            db_manager.insert_pick(
                game_id=game_id,
                season_year=2025,
                week=1,
                pick_team=row['original_pick'],
                confidence_points=row['original_confidence'],
                win_probability=0.5 + (row['original_confidence'] - 8) * 0.05,  # Rough conversion
                total_points_prediction=row.get('total_points', None)
            )
            
            picks_added += 1
            
        except Exception as e:
            print(f"❌ Error adding pick for {game_str}: {e}")
            continue
    
    print(f"✅ Added {picks_added} Week 1 picks to database")
    return picks_added

def main():
    """Main function"""
    
    print("🔄 Adding Week 1 picks to database for retraining...")
    
    picks_added = add_week1_picks_to_database()
    
    if picks_added > 0:
        print(f"\n✅ Successfully added {picks_added} Week 1 picks!")
        print("💡 Now you can retrain the model with current season data")
    else:
        print("\n❌ No picks were added. Check the data format.")

if __name__ == "__main__":
    main()
