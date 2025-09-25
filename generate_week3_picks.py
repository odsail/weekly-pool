#!/usr/bin/env python3
"""
Generate Week 3 picks using the existing infrastructure
"""

import pandas as pd
from database_manager import DatabaseManager
from hybrid_expert_model import HybridExpertModel
import os
from datetime import datetime

def generate_week3_picks():
    """Generate Week 3 picks using hybrid model"""
    
    print("🎯 Generating Week 3 Picks")
    print("=" * 40)
    
    # Initialize database and model
    db = DatabaseManager(version="v2")
    hybrid_model = HybridExpertModel(db)
    
    # Get Week 3 games
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.id, ht.name as home_team, at.name as away_team, g.game_date
            FROM games g
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            WHERE g.season_year = 2025 AND g.week = 3
            ORDER BY g.game_date
        """)
        games = cursor.fetchall()
    
    print(f"📊 Found {len(games)} Week 3 games")
    
    if not games:
        print("❌ No Week 3 games found in database")
        return False
    
    # Prepare games data for hybrid model
    games_data = []
    for game_id, home_team, away_team, game_date in games:
        games_data.append({
            'game_id': game_id,
            'season_year': 2025,
            'week': 3,
            'home_team': home_team,
            'away_team': away_team,
            'game_date': game_date
        })
    
    # Get predictions from hybrid model
    try:
        predictions = hybrid_model.predict_confidence(games_data)
        print(f"✅ Generated {len(predictions)} predictions")
    except Exception as e:
        print(f"❌ Error generating predictions: {e}")
        return False
    
    # Convert predictions to picks format
    picks = []
    for i, prediction in enumerate(predictions):
        game = games_data[i]
        picks.append({
            'game_id': game['game_id'],
            'home_team': game['home_team'],
            'away_team': game['away_team'],
            'pick_team': prediction['pick'],
            'confidence': prediction['confidence'],
            'win_probability': prediction.get('win_probability', 0.5),
            'game_date': game['game_date']
        })
        
        print(f"✅ {game['away_team']} @ {game['home_team']}: {prediction['pick']} (Conf: {prediction['confidence']:.3f})")
    
    if not picks:
        print("❌ No picks generated")
        return False
    
    # Apply stack ranking (16 to 1)
    picks.sort(key=lambda x: x['win_probability'], reverse=True)
    for i, pick in enumerate(picks):
        pick['confidence_points'] = 16 - i
    
    # Store picks in database
    print(f"\n💾 Storing {len(picks)} picks in database...")
    stored_count = 0
    
    for pick in picks:
        try:
            db.insert_pick(
                game_id=pick['game_id'],
                season_year=2025,
                week=3,
                pick_team=pick['pick_team'],
                confidence_points=pick['confidence_points'],
                win_probability=pick['win_probability'],
                total_points_prediction=None
            )
            stored_count += 1
        except Exception as e:
            print(f"❌ Error storing pick for {pick['pick_team']}: {e}")
    
    print(f"✅ Stored {stored_count} picks in database")
    
    # Export picks to files
    output_dir = "data/outputs/2025"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create CSV file
    csv_file = f"{output_dir}/week-week3-picks.csv"
    picks_df = pd.DataFrame(picks)
    picks_df.to_csv(csv_file, index=False)
    print(f"💾 Saved CSV: {csv_file}")
    
    # Create markdown file
    md_file = f"{output_dir}/week-week3-picks.md"
    with open(md_file, 'w') as f:
        f.write("# Week 3 Picks - Hybrid Expert-ML Model\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Picks\n\n")
        f.write("| Points | Pick | Win% | Home | Away | Game Date |\n")
        f.write("|--------|------|------|------|------|----------|\n")
        
        for pick in picks:
            f.write(f"| {pick['confidence_points']:2d} | {pick['pick_team']} | {pick['win_probability']*100:5.1f}% | {pick['home_team']} | {pick['away_team']} | {pick['game_date']} |\n")
        
        f.write(f"\n## Summary\n")
        f.write(f"- **Total Games**: {len(picks)}\n")
        f.write(f"- **Total Confidence Points**: {sum(p['confidence_points'] for p in picks)}\n")
        f.write(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"💾 Saved Markdown: {md_file}")
    
    # Display summary
    print(f"\n🎉 Week 3 Picks Generated Successfully!")
    print(f"📊 Games: {len(picks)}")
    print(f"🎯 Total Confidence Points: {sum(p['confidence_points'] for p in picks)}")
    print(f"📁 Files: {csv_file}, {md_file}")
    
    return True

if __name__ == "__main__":
    generate_week3_picks()
