#!/usr/bin/env python3
"""
Hybrid Expert-ML Model
Primary: Expert consensus with point spreads
Secondary: ML model for games without expert data
"""

import pandas as pd
import numpy as np
from database_manager import DatabaseManager
from current_season_model import CurrentSeasonNFLModel

class HybridExpertModel:
    """Hybrid model combining expert picks with ML predictions"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.ml_model = CurrentSeasonNFLModel(db_manager)
        
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
        
        # Load ML model
        try:
            self.ml_model.load_model()
            self.ml_available = True
        except:
            self.ml_available = False
            print("⚠️  ML model not available, using expert-only predictions")
    
    def predict_confidence(self, games_data: list) -> list:
        """Predict confidence using hybrid expert-ML approach with proper stack ranking"""
        
        predictions = []
        
        for game in games_data:
            # Get game ID
            game_id = self.db_manager.get_game_id(
                game['season_year'], game['week'], 
                game['home_team'], game['away_team']
            )
            
            if game_id:
                # Try expert consensus first
                expert_prediction = self._get_expert_prediction(game_id, game)
                
                if expert_prediction:
                    predictions.append(expert_prediction)
                    continue
            
            # Fall back to ML model if no expert data
            if self.ml_available:
                ml_prediction = self._get_ml_prediction(game)
                predictions.append(ml_prediction)
            else:
                # Default prediction if no data available
                predictions.append({
                    'game': f"{game['away_team']} @ {game['home_team']}",
                    'pick': game['home_team'],  # Default to home team
                    'confidence': 8,  # Default confidence
                    'win_probability': 0.5,
                    'method': 'default'
                })
        
        # Apply proper stack ranking (16, 15, 14, ..., 1)
        predictions = self._apply_stack_ranking(predictions)
        
        return predictions
    
    def _apply_stack_ranking(self, predictions: list) -> list:
        """Apply proper stack ranking from 16 to 1 based on win probability"""
        
        # Sort by win probability (highest first)
        predictions.sort(key=lambda x: x['win_probability'], reverse=True)
        
        # Assign confidence points 16, 15, 14, ..., 1
        for i, pred in enumerate(predictions):
            pred['confidence'] = len(predictions) - i
            pred['rank'] = i + 1
        
        return predictions
    
    def _get_expert_prediction(self, game_id: int, game: dict) -> dict:
        """Get expert-based prediction with point spread adjustment"""
        
        expert_picks = self.db_manager.get_expert_picks_for_game(game_id)
        
        if expert_picks.empty:
            return None
        
        # Calculate weighted expert consensus
        home_weight = 0.0
        away_weight = 0.0
        total_weight = 0.0
        spreads = []
        
        for _, pick in expert_picks.iterrows():
            expert_name = pick['expert_name']
            pick_team = pick['pick_team']
            spread = pick.get('spread', 0)
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
            spreads.append(spread)
        
        if total_weight == 0:
            return None
        
        # Calculate weighted consensus percentage
        home_consensus = home_weight / total_weight
        away_consensus = away_weight / total_weight
        
        # Determine pick and confidence
        if home_consensus >= away_consensus:
            pick_team = game['home_team']
            consensus_strength = home_consensus
        else:
            pick_team = game['away_team']
            consensus_strength = away_consensus
        
        # Calculate confidence based on consensus strength and point spread
        avg_spread = np.mean(spreads) if spreads else 0
        spread_confidence = min(abs(avg_spread) / 7, 1.0)  # Max confidence at 7+ point spread
        
        # Combine consensus strength and spread confidence for win probability
        win_probability = consensus_strength * 0.7 + spread_confidence * 0.3
        
        return {
            'game': f"{game['away_team']} @ {game['home_team']}",
            'pick': pick_team,
            'confidence': 0,  # Will be set by stack ranking
            'win_probability': win_probability,
            'method': 'expert',
            'consensus_strength': consensus_strength,
            'avg_spread': avg_spread,
            'expert_count': len(expert_picks)
        }
    
    def _get_ml_prediction(self, game: dict) -> dict:
        """Get ML-based prediction as fallback"""
        
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
        
        # Predict for home team
        X_home = self.ml_model.prepare_features(test_data)
        X_home = X_home.drop('current_season_weight', axis=1)
        X_home = X_home.fillna(0)
        X_home_scaled = self.ml_model.scaler.transform(X_home)
        home_prediction = self.ml_model.model.predict(X_home_scaled)[0]
        
        # Predict for away team
        test_data_away = test_data.copy()
        test_data_away['home_team'] = game['away_team']
        test_data_away['away_team'] = game['home_team']
        test_data_away['home_ml'] = game.get('away_ml', -110)
        test_data_away['away_ml'] = game.get('home_ml', -110)
        
        X_away = self.ml_model.prepare_features(test_data_away)
        X_away = X_away.drop('current_season_weight', axis=1)
        X_away = X_away.fillna(0)
        X_away_scaled = self.ml_model.scaler.transform(X_away)
        away_prediction = self.ml_model.model.predict(X_away_scaled)[0]
        
        # Choose better prediction
        if home_prediction >= away_prediction:
            pick_team = game['home_team']
            win_prob = home_prediction
        else:
            pick_team = game['away_team']
            win_prob = away_prediction
        
        return {
            'game': f"{game['away_team']} @ {game['home_team']}",
            'pick': pick_team,
            'confidence': 0,  # Will be set by stack ranking
            'win_probability': win_prob,
            'method': 'ml'
        }

def main():
    """Example usage of the hybrid expert model"""
    
    print("🎯 Hybrid Expert-ML Model")
    print("=" * 50)
    
    # Initialize
    db_manager = DatabaseManager(version="v2")
    hybrid_model = HybridExpertModel(db_manager)
    
    print("✅ Hybrid model initialized successfully!")
    print("💡 Ready to generate Week 2 picks with expert data!")

if __name__ == "__main__":
    main()
