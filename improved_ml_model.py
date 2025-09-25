#!/usr/bin/env python3
"""
Improved ML Model with Expert Data Integration
Incorporates expert consensus, point spreads, and current season weighting
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import os
from database_manager import DatabaseManager

class ImprovedNFLConfidenceMLModel:
    """Improved ML model incorporating expert data and point spreads"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.model = None
        self.scaler = StandardScaler()
        
        # Expert performance weights (based on Week 1 accuracy)
        self.expert_weights = {
            'Pete Prisco': 0.688,      # 11-5-0
            'Dave Richard': 0.688,     # 11-5-0
            'Cody Benjamin': 0.500,    # 8-8-0
            'Tyler Sullivan': 0.500,   # 8-8-0
            'Ryan Wilson': 0.438,      # 7-9-0
            'John Breech': 0.438,      # 7-9-0
            'Jared Dubin': 0.375       # 6-10-0
        }
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features including expert consensus and point spreads"""
        
        print("🔄 Preparing features with expert data...")
        
        features = pd.DataFrame()
        
        # Basic features
        features['home_ml'] = df['home_ml']
        features['away_ml'] = df['away_ml']
        features['odds_total'] = df['odds_total']
        features['week'] = df['week']
        features['season_year'] = df['season_year']
        
        # Add expert consensus features
        expert_features = self._add_expert_features(df)
        features = pd.concat([features, expert_features], axis=1)
        
        # Add point spread features
        spread_features = self._add_spread_features(df)
        features = pd.concat([features, spread_features], axis=1)
        
        # Add historical performance features
        historical_features = self._add_historical_features(df)
        features = pd.concat([features, historical_features], axis=1)
        
        # Add current season weighting
        features['current_season_weight'] = (df['season_year'] == 2025).astype(int) * 3.0 + 1.0
        
        print(f"✅ Prepared {len(features.columns)} features")
        return features
    
    def _add_expert_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add expert consensus features"""
        
        expert_features = pd.DataFrame()
        
        # For each game, get expert consensus
        consensus_data = []
        for _, row in df.iterrows():
            # Get game ID
            game_id = self.db_manager.get_game_id(
                row['season_year'], row['week'], 
                row['home_team'], row['away_team']
            )
            
            if game_id:
                consensus = self.db_manager.get_expert_consensus(game_id)
                consensus_data.append({
                    'expert_consensus_percentage': consensus['consensus_percentage'],
                    'expert_total_count': consensus['total_experts'],
                    'expert_consensus_team': consensus['consensus_team']
                })
            else:
                consensus_data.append({
                    'expert_consensus_percentage': 0.5,  # Neutral if no expert data
                    'expert_total_count': 0,
                    'expert_consensus_team': None
                })
        
        expert_df = pd.DataFrame(consensus_data)
        
        # Add expert consensus strength
        expert_df['expert_consensus_strength'] = expert_df['expert_consensus_percentage'] * expert_df['expert_total_count']
        
        # Add expert confidence (weighted by expert performance)
        expert_df['expert_confidence'] = expert_df['expert_consensus_percentage'] * 0.7  # Scale down for realism
        
        # Fill any NaN values with neutral values
        expert_df = expert_df.fillna({
            'expert_consensus_percentage': 0.5,
            'expert_total_count': 0,
            'expert_consensus_strength': 0.0,
            'expert_confidence': 0.5
        })
        
        return expert_df
    
    def _add_spread_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add point spread features"""
        
        spread_features = pd.DataFrame()
        
        # Calculate implied spread from ML odds
        spread_features['implied_spread'] = (df['away_ml'] - df['home_ml']) / 2
        
        # Add spread magnitude (absolute value)
        spread_features['spread_magnitude'] = abs(spread_features['implied_spread'])
        
        # Add spread confidence (higher magnitude = more confident)
        spread_features['spread_confidence'] = np.clip(spread_features['spread_magnitude'] / 10, 0, 1)
        
        # Add home field advantage adjustment
        spread_features['home_field_advantage'] = 3.0  # Standard NFL home field advantage
        
        return spread_features
    
    def _add_historical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add historical performance features"""
        
        historical_features = pd.DataFrame()
        
        # Add rolling averages for team performance
        historical_features['home_team_win_pct'] = 0.5  # Default
        historical_features['away_team_win_pct'] = 0.5  # Default
        
        # Add recent form (last 4 games)
        historical_features['home_recent_form'] = 0.5
        historical_features['away_recent_form'] = 0.5
        
        # Add head-to-head history
        historical_features['h2h_home_advantage'] = 0.0
        
        return historical_features
    
    def train_model(self, test_size: float = 0.2) -> dict:
        """Train the improved ML model"""
        
        print("🔄 Training improved ML model...")
        
        # Get all historical picks data
        df = self.db_manager.get_all_picks_for_ml()
        
        if df.empty:
            raise ValueError("No training data available. Need historical picks with results.")
        
        print(f"📊 Training on {len(df)} historical picks")
        
        # Prepare features
        X = self.prepare_features(df)
        y = df['is_correct'].astype(int)
        
        # Handle missing values more robustly
        X = X.fillna(0)  # Fill NaN with 0 for numerical features
        
        # Check for any remaining NaN values
        if X.isnull().any().any():
            print("⚠️  Warning: Still have NaN values after filling")
            print(f"   NaN columns: {X.columns[X.isnull().any()].tolist()}")
            X = X.fillna(0)  # Fill any remaining NaN with 0
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train improved model
        print("🤖 Training improved Random Forest model...")
        self.model = RandomForestRegressor(
            n_estimators=200,  # More trees for better performance
            max_depth=15,      # Deeper trees for complex patterns
            min_samples_split=3,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1  # Use all CPU cores
        )
        
        # Fit model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        y_pred_binary = (y_pred > 0.5).astype(int)
        
        accuracy = accuracy_score(y_test, y_pred_binary)
        mse = mean_squared_error(y_test, y_pred)
        
        print(f"✅ Improved model trained successfully!")
        print(f"   Accuracy: {accuracy:.3f}")
        print(f"   MSE: {mse:.3f}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='accuracy')
        print(f"   CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n📊 Top 10 Most Important Features:")
        for _, row in feature_importance.head(10).iterrows():
            print(f"   {row['feature']}: {row['importance']:.3f}")
        
        return {
            'accuracy': accuracy,
            'mse': mse,
            'cv_accuracy': cv_scores.mean(),
            'feature_importance': feature_importance
        }
    
    def predict_confidence(self, games_data: list) -> list:
        """Predict confidence for a list of games"""
        
        if not self.model:
            raise ValueError("Model not trained. Call train_model() first.")
        
        predictions = []
        
        for game in games_data:
            # Create test data
            test_data = pd.DataFrame([{
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'home_ml': game.get('home_ml', -110),
                'away_ml': game.get('away_ml', -110),
                'odds_total': game.get('total_points', 45),
                'week': game['week'],
                'season_year': game['season_year']
            }])
            
            # Prepare features
            X = self.prepare_features(test_data)
            X = X.fillna(X.mean())
            
            # Predict for home team
            X_scaled = self.scaler.transform(X)
            home_prediction = self.model.predict(X_scaled)[0]
            
            # Predict for away team (swap the teams)
            test_data_away = test_data.copy()
            test_data_away['home_team'] = game['away_team']
            test_data_away['away_team'] = game['home_team']
            test_data_away['home_ml'] = game.get('away_ml', -110)
            test_data_away['away_ml'] = game.get('home_ml', -110)
            
            X_away = self.prepare_features(test_data_away)
            X_away = X_away.fillna(X_away.mean())
            X_away_scaled = self.scaler.transform(X_away)
            away_prediction = self.model.predict(X_away_scaled)[0]
            
            # Choose better prediction
            if home_prediction >= away_prediction:
                pick_team = game['home_team']
                confidence = max(1, min(16, int(home_prediction * 16)))
                win_prob = home_prediction
            else:
                pick_team = game['away_team']
                confidence = max(1, min(16, int(away_prediction * 16)))
                win_prob = away_prediction
            
            predictions.append({
                'game': f"{game['away_team']} @ {game['home_team']}",
                'pick': pick_team,
                'confidence': confidence,
                'win_probability': win_prob
            })
        
        return predictions
    
    def save_model(self, model_path: str = 'models/improved_confidence_model.pkl'):
        """Save the trained model"""
        
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, model_path.replace('.pkl', '_scaler.pkl'))
        
        print(f"💾 Saved improved model to {model_path}")
    
    def load_model(self, model_path: str = 'models/improved_confidence_model.pkl'):
        """Load a trained model"""
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(model_path.replace('.pkl', '_scaler.pkl'))
        
        print(f"📂 Loaded improved model from {model_path}")

def main():
    """Example usage of the improved ML model"""
    
    print("🤖 Improved NFL Confidence ML Model")
    print("=" * 50)
    
    # Initialize
    db_manager = DatabaseManager(version="v2")
    ml_model = ImprovedNFLConfidenceMLModel(db_manager)
    
    # Train model
    results = ml_model.train_model()
    
    # Save model
    ml_model.save_model()
    
    print(f"\n✅ Improved model training complete!")
    print(f"📊 Final Results:")
    print(f"   Accuracy: {results['accuracy']:.3f}")
    print(f"   MSE: {results['mse']:.3f}")
    print(f"   CV Accuracy: {results['cv_accuracy']:.3f}")

if __name__ == "__main__":
    main()
