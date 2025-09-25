#!/usr/bin/env python3
"""
Test the improved ML model on Week 1 data
"""

import pandas as pd
from database_manager import DatabaseManager
from improved_ml_model import ImprovedNFLConfidenceMLModel

def test_improved_model_on_week1():
    """Test improved model on Week 1 data"""
    
    print("🧪 Testing Improved Model on Week 1 Data")
    print("=" * 50)
    
    # Initialize
    db_manager = DatabaseManager(version="v2")
    ml_model = ImprovedNFLConfidenceMLModel(db_manager)
    
    # Load the improved model
    ml_model.load_model()
    
    # Get Week 1 games from database
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.id, g.season_year, g.week, g.home_team_id, g.away_team_id,
                   t1.name as home_team, t2.name as away_team,
                   g.home_score, g.away_score
            FROM games g
            JOIN teams t1 ON g.home_team_id = t1.id
            JOIN teams t2 ON g.away_team_id = t2.id
            WHERE g.season_year = 2025 AND g.week = 1
            ORDER BY g.game_date
        """)
        
        columns = [description[0] for description in cursor.description]
        week1_games = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    print(f"📊 Testing on {len(week1_games)} Week 1 games")
    
    # Generate predictions
    predictions = []
    for game in week1_games:
        # Create test data
        test_data = {
            'home_team': game['home_team'],
            'away_team': game['away_team'],
            'home_ml': -110,  # Default ML odds
            'away_ml': -110,  # Default ML odds
            'odds_total': 45,  # Default total (note: odds_total not total_points)
            'week': game['week'],
            'season_year': game['season_year']
        }
        
        # Predict for home team
        home_test = test_data.copy()
        X_home = ml_model.prepare_features(pd.DataFrame([home_test]))
        X_home = X_home.fillna(0)
        X_home_scaled = ml_model.scaler.transform(X_home)
        home_prediction = ml_model.model.predict(X_home_scaled)[0]
        
        # Predict for away team
        away_test = test_data.copy()
        away_test['home_team'] = game['away_team']
        away_test['away_team'] = game['home_team']
        X_away = ml_model.prepare_features(pd.DataFrame([away_test]))
        X_away = X_away.fillna(0)
        X_away_scaled = ml_model.scaler.transform(X_away)
        away_prediction = ml_model.model.predict(X_away_scaled)[0]
        
        # Choose better prediction
        if home_prediction >= away_prediction:
            pick_team = game['home_team']
            confidence = max(1, min(16, int(home_prediction * 16)))
            win_prob = home_prediction
        else:
            pick_team = game['away_team']
            confidence = max(1, min(16, int(away_prediction * 16)))
            win_prob = away_prediction
        
        # Determine if correct (only for games with scores)
        if game['home_score'] is not None and game['away_score'] is not None:
            actual_winner = game['home_team'] if game['home_score'] > game['away_score'] else game['away_team']
            is_correct = pick_team == actual_winner
        else:
            actual_winner = "TBD"
            is_correct = None  # Can't determine without scores
        
        predictions.append({
            'game': f"{game['away_team']} @ {game['home_team']}",
            'pick': pick_team,
            'confidence': confidence,
            'win_prob': win_prob,
            'actual_winner': actual_winner,
            'is_correct': is_correct,
            'home_score': game['home_score'],
            'away_score': game['away_score']
        })
    
    # Calculate accuracy (only for games with scores)
    scored_predictions = [p for p in predictions if p['is_correct'] is not None]
    if scored_predictions:
        accuracy = sum(p['is_correct'] for p in scored_predictions) / len(scored_predictions)
    else:
        accuracy = 0.0
    
    print(f"\n📊 Improved Model Week 1 Performance:")
    print(f"   Accuracy: {accuracy:.1%}")
    print(f"   Correct Picks: {sum(p['is_correct'] for p in scored_predictions)}/{len(scored_predictions)}")
    
    # Show predictions
    print(f"\n🎯 Improved Model Predictions:")
    for pred in predictions:
        if pred['is_correct'] is not None:
            status = "✅" if pred['is_correct'] else "❌"
        else:
            status = "⏳"  # TBD
        print(f"   {status} {pred['game']}: {pred['pick']} ({pred['confidence']} pts, {pred['win_prob']:.1%})")
    
    # Compare with original results
    print(f"\n📈 Performance Comparison:")
    print(f"   Original Picks: 81.2% accuracy (13/16 correct)")
    print(f"   Original ML Model: 62.5% accuracy (10/16 correct)")
    print(f"   Improved ML Model: {accuracy:.1%} accuracy ({sum(p['is_correct'] for p in scored_predictions)}/{len(scored_predictions)} correct)")
    
    if accuracy > 0.625:
        improvement = (accuracy - 0.625) * 100
        print(f"   🎉 Improvement: +{improvement:.1f} percentage points!")
    
    if accuracy > 0.812:
        print(f"   🚀 Improved model beats original picks!")
    elif accuracy > 0.625:
        print(f"   ✅ Improved model beats original ML model!")
    else:
        print(f"   ⚠️  Still needs improvement")
    
    return predictions, accuracy

def main():
    """Main function"""
    
    predictions, accuracy = test_improved_model_on_week1()
    
    print(f"\n✅ Testing complete!")
    print(f"💡 The improved model is ready for Week 2 picks!")

if __name__ == "__main__":
    main()
