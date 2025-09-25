#!/usr/bin/env python3
"""
Retrain ML Model with Expert Pick Data and Current Season Weighting
Incorporates CBS Sports expert picks and properly weights current season data
"""

import pandas as pd
import numpy as np
from database_manager import DatabaseManager
from ml_model import NFLConfidenceMLModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class ExpertDataRetrainer:
    """Retrain ML model with expert pick data and current season weighting"""
    
    def __init__(self):
        self.db_manager = DatabaseManager(version="v2")
        self.ml_model = NFLConfidenceMLModel(self.db_manager)
        self.espn_base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        
    def add_expert_picks_to_database(self):
        """Add expert picks data to database for training"""
        
        print("📊 Adding expert picks data to database...")
        
        # Week 1 expert picks data (from the image you provided)
        week1_expert_picks = [
            # Game: DAL 20 vs PHI 24
            {"game_id": self._get_game_id("Dallas Cowboys", "Philadelphia Eagles", 1),
             "expert": "Pete Prisco", "pick": "Dallas Cowboys", "spread": 7, "result": "WIN"},
            {"game_id": self._get_game_id("Dallas Cowboys", "Philadelphia Eagles", 1),
             "expert": "Cody Benjamin", "pick": "Dallas Cowboys", "spread": 7, "result": "WIN"},
            {"game_id": self._get_game_id("Dallas Cowboys", "Philadelphia Eagles", 1),
             "expert": "Jared Dubin", "pick": "Philadelphia Eagles", "spread": -7, "result": "LOSS"},
            {"game_id": self._get_game_id("Dallas Cowboys", "Philadelphia Eagles", 1),
             "expert": "Ryan Wilson", "pick": "Philadelphia Eagles", "spread": -7, "result": "LOSS"},
            {"game_id": self._get_game_id("Dallas Cowboys", "Philadelphia Eagles", 1),
             "expert": "John Breech", "pick": "Philadelphia Eagles", "spread": -7, "result": "LOSS"},
            {"game_id": self._get_game_id("Dallas Cowboys", "Philadelphia Eagles", 1),
             "expert": "Tyler Sullivan", "pick": "Philadelphia Eagles", "spread": -7, "result": "LOSS"},
            {"game_id": self._get_game_id("Dallas Cowboys", "Philadelphia Eagles", 1),
             "expert": "Dave Richard", "pick": "Philadelphia Eagles", "spread": -7, "result": "LOSS"},
            
            # Game: KC 21 vs LAC 27
            {"game_id": self._get_game_id("Kansas City Chiefs", "Los Angeles Chargers", 1),
             "expert": "Pete Prisco", "pick": "Kansas City Chiefs", "spread": -3, "result": "LOSS"},
            {"game_id": self._get_game_id("Kansas City Chiefs", "Los Angeles Chargers", 1),
             "expert": "Cody Benjamin", "pick": "Kansas City Chiefs", "spread": -3, "result": "LOSS"},
            {"game_id": self._get_game_id("Kansas City Chiefs", "Los Angeles Chargers", 1),
             "expert": "Jared Dubin", "pick": "Kansas City Chiefs", "spread": -3, "result": "LOSS"},
            {"game_id": self._get_game_id("Kansas City Chiefs", "Los Angeles Chargers", 1),
             "expert": "Ryan Wilson", "pick": "Los Angeles Chargers", "spread": 3, "result": "WIN"},
            {"game_id": self._get_game_id("Kansas City Chiefs", "Los Angeles Chargers", 1),
             "expert": "John Breech", "pick": "Kansas City Chiefs", "spread": -3, "result": "LOSS"},
            {"game_id": self._get_game_id("Kansas City Chiefs", "Los Angeles Chargers", 1),
             "expert": "Tyler Sullivan", "pick": "Kansas City Chiefs", "spread": -3, "result": "LOSS"},
            {"game_id": self._get_game_id("Kansas City Chiefs", "Los Angeles Chargers", 1),
             "expert": "Dave Richard", "pick": "Los Angeles Chargers", "spread": 3, "result": "WIN"},
            
            # Add more games as needed...
        ]
        
        # Store expert picks in database
        for pick in week1_expert_picks:
            if pick["game_id"]:
                self._store_expert_pick(pick)
        
        print(f"✅ Added {len(week1_expert_picks)} expert picks to database")
    
    def _get_game_id(self, home_team, away_team, week):
        """Get game ID from database"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.id FROM games g
                JOIN teams ht ON g.home_team_id = ht.id
                JOIN teams at ON g.away_team_id = at.id
                WHERE ht.name = ? AND at.name = ? AND g.week = ? AND g.season_year = 2025
            """, (home_team, away_team, week))
            
            result = cursor.fetchone()
            return result[0] if result else None
    
    def _store_expert_pick(self, pick_data):
        """Store expert pick in database"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO expert_picks 
                (game_id, expert_name, pick_team, spread, result, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                pick_data["game_id"],
                pick_data["expert"],
                pick_data["pick"],
                pick_data["spread"],
                pick_data["result"],
                10  # Default confidence for expert picks
            ))
            conn.commit()
    
    def create_weighted_training_data(self):
        """Create training data with proper current season weighting"""
        
        print("🔄 Creating weighted training data...")
        
        # Get all historical picks
        historical_picks = self.db_manager.get_all_picks_for_ml()
        
        # Get current season picks (2025)
        current_season_picks = historical_picks[historical_picks['season_year'] == 2025]
        historical_picks = historical_picks[historical_picks['season_year'] < 2025]
        
        print(f"📊 Historical picks: {len(historical_picks)}")
        print(f"📊 Current season picks: {len(current_season_picks)}")
        
        # Weight current season data more heavily
        # Current season gets 3x weight, historical gets 1x weight
        current_season_weighted = current_season_picks.copy()
        current_season_weighted['weight'] = 3.0
        
        historical_weighted = historical_picks.copy()
        historical_weighted['weight'] = 1.0
        
        # Combine weighted data
        weighted_training_data = pd.concat([current_season_weighted, historical_weighted], ignore_index=True)
        
        print(f"✅ Created weighted training data: {len(weighted_training_data)} picks")
        print(f"   Current season weight: 3.0x")
        print(f"   Historical weight: 1.0x")
        
        return weighted_training_data
    
    def retrain_model_with_expert_data(self):
        """Retrain model with expert data and current season weighting"""
        
        print("🤖 Retraining ML model with expert data and current season weighting...")
        
        # Step 1: Add expert picks to database
        self.add_expert_picks_to_database()
        
        # Step 2: Create weighted training data
        weighted_data = self.create_weighted_training_data()
        
        # Step 3: Prepare features with weights
        X = self.ml_model.prepare_features(weighted_data)
        y = weighted_data['is_correct'].astype(int)
        weights = weighted_data['weight']
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Step 4: Train model with sample weights
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.metrics import accuracy_score, mean_squared_error
        
        X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
            X, y, weights, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.ml_model.scaler.fit_transform(X_train)
        X_test_scaled = self.ml_model.scaler.transform(X_test)
        
        # Train model with sample weights
        print("🔄 Training weighted Random Forest model...")
        self.ml_model.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        # Fit with sample weights
        self.ml_model.model.fit(X_train_scaled, y_train, sample_weight=w_train)
        
        # Evaluate model
        y_pred = self.ml_model.model.predict(X_test_scaled)
        y_pred_binary = (y_pred > 0.5).astype(int)
        
        accuracy = accuracy_score(y_test, y_pred_binary)
        mse = mean_squared_error(y_test, y_pred)
        
        print(f"✅ Retrained model successfully!")
        print(f"   Accuracy: {accuracy:.3f}")
        print(f"   MSE: {mse:.3f}")
        
        # Step 5: Save retrained model
        import joblib
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.ml_model.model, 'models/retrained_confidence_model.pkl')
        joblib.dump(self.ml_model.scaler, 'models/retrained_scaler.pkl')
        
        print("💾 Saved retrained model to models/retrained_confidence_model.pkl")
        
        return accuracy, mse
    
    def test_retrained_model_on_week1(self):
        """Test retrained model on Week 1 data"""
        
        print("🧪 Testing retrained model on Week 1 data...")
        
        # Load retrained model
        import joblib
        self.ml_model.model = joblib.load('models/retrained_confidence_model.pkl')
        self.ml_model.scaler = joblib.load('models/retrained_scaler.pkl')
        
        # Get Week 1 games
        with self.db_manager.get_connection() as conn:
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
        
        # Generate predictions
        predictions = []
        for game in week1_games:
            # Create test data
            test_data = pd.DataFrame([{
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'pick_team': game['home_team'],
                'home_ml': -110,
                'away_ml': -110,
                'week': game['week'],
                'season_year': game['season_year']
            }])
            
            # Predict for home team
            X_home = self.ml_model.prepare_features(test_data)
            X_home = X_home.fillna(X_home.mean())
            home_prediction = self.ml_model.model.predict(self.ml_model.scaler.transform(X_home))[0]
            
            # Predict for away team
            test_data_away = test_data.copy()
            test_data_away['pick_team'] = game['away_team']
            X_away = self.ml_model.prepare_features(test_data_away)
            X_away = X_away.fillna(X_away.mean())
            away_prediction = self.ml_model.model.predict(self.ml_model.scaler.transform(X_away))[0]
            
            # Choose better prediction
            if home_prediction >= away_prediction:
                pick_team = game['home_team']
                confidence = max(1, min(16, int(home_prediction * 16)))
                win_prob = home_prediction
            else:
                pick_team = game['away_team']
                confidence = max(1, min(16, int(away_prediction * 16)))
                win_prob = away_prediction
            
            # Determine if correct
            actual_winner = game['home_team'] if game['home_score'] > game['away_score'] else game['away_team']
            is_correct = pick_team == actual_winner
            
            predictions.append({
                'game': f"{game['away_team']} @ {game['home_team']}",
                'pick': pick_team,
                'confidence': confidence,
                'win_prob': win_prob,
                'actual_winner': actual_winner,
                'is_correct': is_correct
            })
        
        # Calculate accuracy
        accuracy = sum(p['is_correct'] for p in predictions) / len(predictions)
        
        print(f"📊 Retrained Model Week 1 Performance:")
        print(f"   Accuracy: {accuracy:.1%}")
        print(f"   Correct Picks: {sum(p['is_correct'] for p in predictions)}/{len(predictions)}")
        
        # Show predictions
        print(f"\n🎯 Retrained Model Predictions:")
        for pred in predictions:
            status = "✅" if pred['is_correct'] else "❌"
            print(f"   {status} {pred['game']}: {pred['pick']} ({pred['confidence']} pts, {pred['win_prob']:.1%})")
        
        return predictions, accuracy

def main():
    """Main function to retrain model with expert data"""
    
    print("🔄 Retraining ML Model with Expert Data and Current Season Weighting")
    print("=" * 70)
    
    retrainer = ExpertDataRetrainer()
    
    # Step 1: Retrain model
    accuracy, mse = retrainer.retrain_model_with_expert_data()
    
    # Step 2: Test on Week 1
    predictions, test_accuracy = retrainer.test_retrained_model_on_week1()
    
    print(f"\n✅ Retraining complete!")
    print(f"📊 Results:")
    print(f"   Training Accuracy: {accuracy:.3f}")
    print(f"   Week 1 Test Accuracy: {test_accuracy:.1%}")
    print(f"   Model saved to: models/retrained_confidence_model.pkl")
    
    if test_accuracy > 0.625:  # Better than original ML model
        print(f"🎉 Retrained model performs better than original ML model!")
    else:
        print(f"⚠️  Retrained model needs further improvement")

if __name__ == "__main__":
    main()


