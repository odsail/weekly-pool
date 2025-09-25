#!/usr/bin/env python3
"""
Generate Week 2 picks using the hybrid expert-ML model
"""

import pandas as pd
from database_manager import DatabaseManager
from hybrid_expert_model import HybridExpertModel

def generate_week2_picks():
    """Generate Week 2 picks using hybrid expert-ML model"""
    
    print("🎯 Generating Week 2 Picks with Hybrid Expert-ML Model")
    print("=" * 60)
    
    # Initialize
    db_manager = DatabaseManager(version="v2")
    hybrid_model = HybridExpertModel(db_manager)
    
    # Get Week 2 games from database
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.id, g.season_year, g.week, g.home_team_id, g.away_team_id,
                   t1.name as home_team, t2.name as away_team,
                   g.game_date
            FROM games g
            JOIN teams t1 ON g.home_team_id = t1.id
            JOIN teams t2 ON g.away_team_id = t2.id
            WHERE g.season_year = 2025 AND g.week = 2
            ORDER BY g.game_date
        """)
        
        columns = [description[0] for description in cursor.description]
        week2_games = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    print(f"📊 Found {len(week2_games)} Week 2 games")
    
    # Prepare games data for prediction
    games_data = []
    for game in week2_games:
        games_data.append({
            'home_team': game['home_team'],
            'away_team': game['away_team'],
            'week': game['week'],
            'season_year': game['season_year'],
            'game_date': game['game_date']
        })
    
    # Generate predictions
    print("🔄 Generating predictions...")
    predictions = hybrid_model.predict_confidence(games_data)
    
    # Sort by confidence (highest first)
    predictions.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Display results
    print(f"\n🎯 Week 2 Picks (Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print("=" * 60)
    
    total_confidence = 0
    expert_picks = 0
    ml_picks = 0
    default_picks = 0
    
    for i, pred in enumerate(predictions, 1):
        method_emoji = {
            'expert': '🎯',
            'ml': '🤖',
            'default': '⚪'
        }.get(pred['method'], '❓')
        
        print(f"{i:2d}. {method_emoji} {pred['game']}")
        print(f"    Pick: {pred['pick']} ({pred['confidence']} pts, {pred['win_probability']:.1%})")
        
        if pred['method'] == 'expert':
            expert_picks += 1
            print(f"    Method: Expert consensus ({pred.get('expert_count', 0)} experts)")
            if 'consensus_strength' in pred:
                print(f"    Consensus: {pred['consensus_strength']:.1%}")
            if 'avg_spread' in pred:
                print(f"    Avg Spread: {pred['avg_spread']:.1f}")
        elif pred['method'] == 'ml':
            ml_picks += 1
            print(f"    Method: ML model")
        else:
            default_picks += 1
            print(f"    Method: Default")
        
        print()
        total_confidence += pred['confidence']
    
    # Summary
    print("📊 Summary:")
    print(f"   Total Games: {len(predictions)}")
    print(f"   Total Confidence Points: {total_confidence}")
    print(f"   Expert-based Picks: {expert_picks}")
    print(f"   ML-based Picks: {ml_picks}")
    print(f"   Default Picks: {default_picks}")
    
    # Check if we have expert data for Week 2
    if expert_picks == 0:
        print(f"\n⚠️  No expert data found for Week 2 games")
        print(f"   Consider adding expert picks to the database")
    else:
        print(f"\n✅ Using expert consensus for {expert_picks} games")
    
    # Save to file
    output_file = "data/outputs/2025/week2-hybrid-picks.md"
    save_picks_to_file(predictions, output_file)
    
    return predictions

def save_picks_to_file(predictions, filename):
    """Save picks to markdown file"""
    
    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w') as f:
        f.write(f"# Week 2 Picks - Hybrid Expert-ML Model\n")
        f.write(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Picks\n\n")
        f.write("| Rank | Game | Pick | Confidence | Win Prob | Method |\n")
        f.write("|------|------|------|------------|----------|--------|\n")
        
        for i, pred in enumerate(predictions, 1):
            method_emoji = {
                'expert': '🎯',
                'ml': '🤖',
                'default': '⚪'
            }.get(pred['method'], '❓')
            
            f.write(f"| {i} | {pred['game']} | {pred['pick']} | {pred['confidence']} | {pred['win_probability']:.1%} | {method_emoji} {pred['method']} |\n")
        
        f.write(f"\n## Summary\n")
        f.write(f"- **Total Games**: {len(predictions)}\n")
        f.write(f"- **Total Confidence Points**: {sum(p['confidence'] for p in predictions)}\n")
        f.write(f"- **Expert-based Picks**: {sum(1 for p in predictions if p['method'] == 'expert')}\n")
        f.write(f"- **ML-based Picks**: {sum(1 for p in predictions if p['method'] == 'ml')}\n")
        f.write(f"- **Default Picks**: {sum(1 for p in predictions if p['method'] == 'default')}\n")
    
    print(f"💾 Picks saved to {filename}")

def main():
    """Main function"""
    
    predictions = generate_week2_picks()
    
    print(f"\n✅ Week 2 picks generated successfully!")
    print(f"💡 Ready for Week 2 games!")

if __name__ == "__main__":
    main()
