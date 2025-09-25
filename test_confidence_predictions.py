#!/usr/bin/env python3
"""
Test confidence point predictions using the trained ML model.
"""

from database_manager import DatabaseManager
from ml_model import NFLConfidenceMLModel
import pandas as pd

def test_confidence_predictions():
    """Test the ML model's confidence predictions"""
    
    print("🧪 Testing ML model confidence predictions...")
    
    # Initialize components
    db_manager = DatabaseManager(version="v2")
    ml_model = NFLConfidenceMLModel(db_manager)
    
    # Load the trained model
    ml_model.load_model()
    
    if ml_model.model is None:
        print("❌ No trained model found. Please train the model first.")
        return
    
    print("✅ Model loaded successfully")
    
    # Get some test data
    test_df = db_manager.get_all_picks_for_ml()
    
    if test_df.empty:
        print("❌ No test data available")
        return
    
    # Take a sample for testing
    test_sample = test_df.sample(n=min(100, len(test_df)), random_state=42)
    
    print(f"📊 Testing on {len(test_sample)} sample picks")
    
    # Prepare features
    X_test = ml_model.prepare_features(test_sample)
    X_test = X_test.fillna(X_test.mean())
    
    # Make predictions
    predictions = ml_model.model.predict(ml_model.scaler.transform(X_test))
    
    # Analyze predictions
    print("\n🔍 Prediction Analysis:")
    print(f"   Prediction range: {predictions.min():.3f} to {predictions.max():.3f}")
    print(f"   Mean prediction: {predictions.mean():.3f}")
    print(f"   Std prediction: {predictions.std():.3f}")
    
    # Convert predictions to confidence points (1-16 scale)
    confidence_points = (predictions * 16).round().astype(int)
    confidence_points = confidence_points.clip(1, 16)  # Ensure within range
    
    print(f"\n📈 Confidence Point Distribution:")
    for i in range(1, 17):
        count = (confidence_points == i).sum()
        percentage = (count / len(confidence_points)) * 100
        print(f"   {i:2d} points: {count:3d} picks ({percentage:5.1f}%)")
    
    # Test accuracy by confidence level
    print(f"\n🎯 Accuracy by Confidence Level:")
    test_sample['predicted_confidence'] = confidence_points
    test_sample['predicted_correct'] = predictions > 0.5
    
    for conf_level in range(1, 17):
        level_data = test_sample[test_sample['predicted_confidence'] == conf_level]
        if len(level_data) > 0:
            accuracy = level_data['is_correct'].mean()
            count = len(level_data)
            print(f"   {conf_level:2d} points: {accuracy:.3f} accuracy ({count} picks)")
    
    # Test some specific examples
    print(f"\n📋 Sample Predictions:")
    sample_indices = test_sample.index[:5]
    for idx in sample_indices:
        row = test_sample.loc[idx]
        pred_idx = list(test_sample.index).index(idx)
        pred_conf = confidence_points[pred_idx]
        pred_prob = predictions[pred_idx]
        actual_correct = row['is_correct']
        
        print(f"   {row['home_team']} vs {row['away_team']}: "
              f"{pred_conf} points (prob: {pred_prob:.3f}, actual: {actual_correct})")
    
    print(f"\n✅ Confidence prediction testing complete!")

def test_confidence_optimization():
    """Test confidence point optimization"""
    
    print("\n🎯 Testing confidence point optimization...")
    
    db_manager = DatabaseManager(version="v2")
    ml_model = NFLConfidenceMLModel(db_manager)
    ml_model.load_model()
    
    if ml_model.model is None:
        print("❌ No trained model found")
        return
    
    # Get recent games for testing
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.id, g.season_year, g.week, t1.name as home_team, t2.name as away_team,
                   o.home_ml, o.away_ml, o.home_win_prob, o.away_win_prob
            FROM games g
            JOIN teams t1 ON g.home_team_id = t1.id
            JOIN teams t2 ON g.away_team_id = t2.id
            LEFT JOIN odds o ON g.id = o.game_id
            WHERE g.season_year = 2024 AND g.week = 1
            LIMIT 5
        """)
        
        test_games = cursor.fetchall()
    
    if not test_games:
        print("❌ No test games found")
        return
    
    print(f"📊 Testing confidence optimization on {len(test_games)} games:")
    
    for game in test_games:
        game_id, season, week, home_team, away_team, home_ml, away_ml, home_prob, away_prob = game
        
        # Create test data for this game
        test_data = pd.DataFrame([{
            'home_team': home_team,
            'away_team': away_team,
            'pick_team': home_team,  # Assume picking home team
            'home_ml': home_ml or -110,
            'away_ml': away_ml or -110,
            'week': week,
            'season_year': season
        }])
        
        # Prepare features
        X = ml_model.prepare_features(test_data)
        X = X.fillna(X.mean())
        
        # Make prediction
        prediction = ml_model.model.predict(ml_model.scaler.transform(X))[0]
        confidence_points = max(1, min(16, int(prediction * 16)))
        
        print(f"   {away_team} @ {home_team}: {confidence_points} confidence points (prob: {prediction:.3f})")

if __name__ == "__main__":
    test_confidence_predictions()
    test_confidence_optimization()


