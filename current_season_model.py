#!/usr/bin/env python3
"""
Current Season Focused ML Model
Heavy weights on: Expert picks, Point spreads, 2025 data
Light weights on: Historical data (2018-2024)
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

class CurrentSeasonNFLModel:
    """Current season focused model with expert data and point spreads"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.model = None
        self.scaler = StandardScaler()
        
        # Expert performance weights (based on Week 1 accuracy)
        self.expert_weights = {
            'Pete Prisco': 0.688,      # 11-5-0 (68.8%)
            'Dave Richard': 0.688,     # 11-5-0 (68.8%)
            'Cody Benjamin': 0.500,    # 8-8-0 (50.0%)
            'Tyler Sullivan': 0.500,   # 8-8-0 (50.0%)
            'Ryan Wilson': 0.438,      # 7-9-0 (43.8%)
            'John Breech': 0.438,      # 7-9-0 (43.8%)
            'Jared Dubin': 0.375       # 6-10-0 (37.5%)
        }
        
        # Current season weighting
        self.current_season_weight = 5.0  # 5x weight for 2025 data
        self.historical_weight = 1.0      # 1x weight for historical data
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features with current season focus"""
        
        print("🔄 Preparing current-season focused features...")
        
        features = pd.DataFrame()
        
        # Basic features
        features['home_ml'] = df['home_ml']
        features['away_ml'] = df['away_ml']
        features['odds_total'] = df['odds_total']
        features['week'] = df['week']
        features['season_year'] = df['season_year']
        
        # Add expert consensus features (HEAVY WEIGHT)
        expert_features = self._add_expert_features(df)
        features = pd.concat([features, expert_features], axis=1)
        
        # Add point spread features (HEAVY WEIGHT)
        spread_features = self._add_spread_features(df)
        features = pd.concat([features, spread_features], axis=1)
        
        # Add current season weighting
        features['current_season_weight'] = (df['season_year'] == 2025).astype(int) * self.current_season_weight + self.historical_weight
        
        # Add historical features (LIGHT WEIGHT)
        historical_features = self._add_historical_features(df)
        features = pd.concat([features, historical_features], axis=1)
        
        print(f"✅ Prepared {len(features.columns)} current-season focused features")
        return features
    
    def _add_expert_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add expert consensus features with performance weighting"""
        
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
                
                # Calculate weighted expert consensus
                weighted_consensus = self._calculate_weighted_expert_consensus(game_id)
                
                consensus_data.append({
                    'expert_consensus_percentage': consensus['consensus_percentage'],
                    'expert_total_count': consensus['total_experts'],
                    'expert_consensus_strength': consensus['consensus_percentage'] * consensus['total_experts'],
                    'expert_confidence': consensus['consensus_percentage'] * 0.8,  # Scale for realism
                    'weighted_expert_consensus': weighted_consensus['weighted_consensus'],
                    'expert_confidence_score': weighted_consensus['confidence_score']
                })
            else:
                # No expert data - use neutral values
                consensus_data.append({
                    'expert_consensus_percentage': 0.5,
                    'expert_total_count': 0,
                    'expert_consensus_strength': 0.0,
                    'expert_confidence': 0.5,
                    'weighted_expert_consensus': 0.5,
                    'expert_confidence_score': 0.5
                })
        
        expert_df = pd.DataFrame(consensus_data)
        
        # Fill any NaN values
        expert_df = expert_df.fillna({
            'expert_consensus_percentage': 0.5,
            'expert_total_count': 0,
            'expert_consensus_strength': 0.0,
            'expert_confidence': 0.5,
            'weighted_expert_consensus': 0.5,
            'expert_confidence_score': 0.5
        })
        
        return expert_df
    
    def _calculate_weighted_expert_consensus(self, game_id: int) -> dict:
        """Calculate weighted expert consensus based on individual expert performance"""
        
        expert_picks = self.db_manager.get_expert_picks_for_game(game_id)
        
        if expert_picks.empty:
            return {'weighted_consensus': 0.5, 'confidence_score': 0.5}
        
        # Calculate weighted consensus
        home_weight = 0.0
        away_weight = 0.0
        total_weight = 0.0
        
        for _, pick in expert_picks.iterrows():
            expert_name = pick['expert_name']
            pick_team = pick['pick_team']
            confidence = pick.get('confidence', 10)
            
            # Get expert weight (performance-based)
            expert_weight = self.expert_weights.get(expert_name, 0.5)
            
            # Weight by both expert performance and confidence
            weighted_confidence = expert_weight * (confidence / 10.0)
            
            if pick_team == 'home':
                home_weight += weighted_confidence
            else:
                away_weight += weighted_confidence
            
            total_weight += weighted_confidence
        
        if total_weight == 0:
            return {'weighted_consensus': 0.5, 'confidence_score': 0.5}
        
        # Calculate weighted consensus percentage
        home_consensus = home_weight / total_weight
        away_consensus = away_weight / total_weight
        
        # Return the stronger consensus
        if home_consensus >= away_consensus:
            return {
                'weighted_consensus': home_consensus,
                'confidence_score': total_weight / len(expert_picks)  # Average confidence
            }
        else:
            return {
                'weighted_consensus': away_consensus,
                'confidence_score': total_weight / len(expert_picks)
            }
    
    def _add_spread_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add point spread features from expert data"""
        
        spread_features = pd.DataFrame()
        
        # Calculate implied spread from ML odds
        spread_features['implied_spread'] = (df['away_ml'] - df['home_ml']) / 2
        
        # Add spread magnitude (absolute value)
        spread_features['spread_magnitude'] = abs(spread_features['implied_spread'])
        
        # Add spread confidence (higher magnitude = more confident)
        spread_features['spread_confidence'] = np.clip(spread_features['spread_magnitude'] / 10, 0, 1)
        
        # Add home field advantage
        spread_features['home_field_advantage'] = 3.0  # Standard NFL home field advantage
        
        # Add spread-based win probability
        spread_features['spread_win_prob'] = 0.5 + (spread_features['implied_spread'] / 20)  # Rough conversion
        spread_features['spread_win_prob'] = np.clip(spread_features['spread_win_prob'], 0.1, 0.9)
        
        return spread_features
    
    def _add_historical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add historical performance features (LIGHT WEIGHT)"""
        
        historical_features = pd.DataFrame()
        
        # Add rolling averages for team performance (devalued)
        historical_features['home_team_win_pct'] = 0.5  # Default
        historical_features['away_team_win_pct'] = 0.5  # Default
        
        # Add recent form (last 4 games) - devalued
        historical_features['home_recent_form'] = 0.5
        historical_features['away_recent_form'] = 0.5
        
        # Add head-to-head history - devalued
        historical_features['h2h_home_advantage'] = 0.0
        
        return historical_features
    
    def train_model(self, test_size: float = 0.2) -> dict:
        """Train the current-season focused model"""
        
        print("🔄 Training current-season focused ML model...")
        
        # Get all historical picks data
        df = self.db_manager.get_all_picks_for_ml()
        
        if df.empty:
            raise ValueError("No training data available. Need historical picks with results.")
        
        print(f"📊 Training on {len(df)} historical picks")
        
        # Prepare features
        X = self.prepare_features(df)
        y = df['is_correct'].astype(int)
        
        # Handle missing values
        X = X.fillna(0)
        
        # Apply current season weighting to training data
        sample_weights = X['current_season_weight'].values
        X = X.drop('current_season_weight', axis=1)  # Remove weight column from features
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)
        
        # Get corresponding sample weights
        train_weights = sample_weights[X_train.index]
        test_weights = sample_weights[X_test.index]
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train current-season focused model
        print("🤖 Training current-season focused Random Forest model...")
        self.model = RandomForestRegressor(
            n_estimators=150,  # Fewer trees for current-season focus
            max_depth=12,      # Moderate depth
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        # Fit model with sample weights
        self.model.fit(X_train_scaled, y_train, sample_weight=train_weights)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        y_pred_binary = (y_pred > 0.5).astype(int)
        
        accuracy = accuracy_score(y_test, y_pred_binary)
        mse = mean_squared_error(y_test, y_pred)
        
        print(f"✅ Current-season focused model trained successfully!")
        print(f"   Accuracy: {accuracy:.3f}")
        print(f"   MSE: {mse:.3f}")
        
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
            'feature_importance': feature_importance
        }
    
    def predict_confidence(self, games_data: list) -> list:
        """Predict confidence for a list of games using current-season focus"""
        
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
            X = X.drop('current_season_weight', axis=1)  # Remove weight column
            X = X.fillna(0)
            
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
            X_away = X_away.drop('current_season_weight', axis=1)
            X_away = X_away.fillna(0)
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
    
    def save_model(self, model_path: str = 'models/current_season_model.pkl'):
        """Save the trained model"""
        
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, model_path.replace('.pkl', '_scaler.pkl'))
        
        print(f"💾 Saved current-season model to {model_path}")
    
    def load_model(self, model_path: str = 'models/current_season_model.pkl'):
        """Load a trained model"""
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(model_path.replace('.pkl', '_scaler.pkl'))
        
        print(f"📂 Loaded current-season model from {model_path}")

def main():
    """Example usage of the current-season focused model"""
    
    print("🎯 Current Season Focused NFL Model")
    print("=" * 50)
    
    # Initialize
    db_manager = DatabaseManager(version="v2")
    ml_model = CurrentSeasonNFLModel(db_manager)
    
    # Train model
    results = ml_model.train_model()
    
    # Save model
    ml_model.save_model()
    
    print(f"\n✅ Current-season model training complete!")
    print(f"📊 Final Results:")
    print(f"   Accuracy: {results['accuracy']:.3f}")
    print(f"   MSE: {results['mse']:.3f}")

if __name__ == "__main__":
    main()


