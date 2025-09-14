#!/usr/bin/env python3
"""
Machine Learning model for NFL confidence pool predictions.
Uses historical data to improve confidence point assignments.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Dict, List, Tuple, Optional
import joblib
import os
from database_manager import DatabaseManager

class NFLConfidenceMLModel:
    """ML model for predicting optimal confidence points"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.model_path = "models/confidence_model.pkl"
        
        # Ensure models directory exists
        os.makedirs("models", exist_ok=True)
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML model"""
        features_df = df.copy()
        
        # Encode categorical variables
        categorical_cols = ['home_team', 'away_team', 'pick_team']
        for col in categorical_cols:
            if col in features_df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    features_df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(features_df[col])
                else:
                    features_df[f'{col}_encoded'] = self.label_encoders[col].transform(features_df[col])
        
        # Create derived features
        if 'home_ml' in features_df.columns and 'away_ml' in features_df.columns:
            features_df['ml_difference'] = features_df['home_ml'] - features_df['away_ml']
            features_df['ml_ratio'] = features_df['home_ml'] / features_df['away_ml'].replace(0, 1)
        
        if 'home_win_prob' in features_df.columns and 'away_win_prob' in features_df.columns:
            features_df['prob_difference'] = features_df['home_win_prob'] - features_df['away_win_prob']
            features_df['prob_ratio'] = features_df['home_win_prob'] / features_df['away_win_prob'].replace(0, 0.01)
        
        # Add historical performance features
        features_df = self._add_historical_features(features_df)
        
        # Add week and season features
        if 'week' in features_df.columns:
            features_df['week_sin'] = np.sin(2 * np.pi * features_df['week'] / 18)  # 18-week season
            features_df['week_cos'] = np.cos(2 * np.pi * features_df['week'] / 18)
        
        # Select feature columns
        feature_cols = [
            'home_ml', 'away_ml', 'total_points', 'home_win_prob', 'away_win_prob',
            'ml_difference', 'ml_ratio', 'prob_difference', 'prob_ratio',
            'week_sin', 'week_cos', 'home_team_encoded', 'away_team_encoded', 'pick_team_encoded'
        ]
        
        # Add historical features
        historical_cols = [col for col in features_df.columns if col.startswith('hist_')]
        feature_cols.extend(historical_cols)
        
        # Filter to available columns
        self.feature_columns = [col for col in feature_cols if col in features_df.columns]
        
        return features_df[self.feature_columns]
    
    def _add_historical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add historical performance features"""
        for _, row in df.iterrows():
            # Get team performance history
            home_team = row.get('home_team')
            away_team = row.get('away_team')
            pick_team = row.get('pick_team')
            
            if home_team:
                home_history = self.db_manager.get_team_performance_history(home_team, weeks_back=4)
                if not home_history.empty:
                    df.loc[df.index == row.name, 'hist_home_win_pct'] = home_history['win_percentage'].mean()
                    df.loc[df.index == row.name, 'hist_home_pt_diff'] = home_history['point_differential'].mean()
            
            if away_team:
                away_history = self.db_manager.get_team_performance_history(away_team, weeks_back=4)
                if not away_history.empty:
                    df.loc[df.index == row.name, 'hist_away_win_pct'] = away_history['win_percentage'].mean()
                    df.loc[df.index == row.name, 'hist_away_pt_diff'] = away_history['point_differential'].mean()
            
            if pick_team:
                pick_history = self.db_manager.get_team_performance_history(pick_team, weeks_back=4)
                if not pick_history.empty:
                    df.loc[df.index == row.name, 'hist_pick_win_pct'] = pick_history['win_percentage'].mean()
                    df.loc[df.index == row.name, 'hist_pick_pt_diff'] = pick_history['point_differential'].mean()
        
        return df
    
    def train_model(self, test_size: float = 0.2) -> Dict:
        """Train the ML model"""
        print("🔄 Loading training data...")
        
        # Get all historical picks data
        df = self.db_manager.get_all_picks_for_ml()
        
        if df.empty:
            raise ValueError("No training data available. Need historical picks with results.")
        
        print(f"📊 Training on {len(df)} historical picks")
        
        # Prepare features
        X = self.prepare_features(df)
        y = df['is_correct'].astype(int)  # Binary classification: correct/incorrect
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model (using ensemble for better performance)
        print("🤖 Training Random Forest model...")
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        # For confidence points, we'll predict the probability of being correct
        # and then map that to confidence points
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        y_pred_binary = (y_pred > 0.5).astype(int)
        
        accuracy = accuracy_score(y_test, y_pred_binary)
        mse = mean_squared_error(y_test, y_pred)
        
        print(f"✅ Model trained successfully!")
        print(f"   Accuracy: {accuracy:.3f}")
        print(f"   MSE: {mse:.3f}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='accuracy')
        print(f"   CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Save model
        self.save_model()
        
        return {
            'accuracy': accuracy,
            'mse': mse,
            'cv_accuracy': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_))
        }
    
    def predict_confidence(self, game_data: pd.DataFrame) -> pd.DataFrame:
        """Predict confidence points for new games"""
        if self.model is None:
            self.load_model()
        
        if self.model is None:
            raise ValueError("No trained model available. Train model first.")
        
        # Prepare features
        X = self.prepare_features(game_data)
        X = X.fillna(X.mean())
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict probabilities
        probabilities = self.model.predict(X_scaled)
        
        # Map probabilities to confidence points (1-16 scale)
        # Higher probability = higher confidence points
        confidence_points = np.round(probabilities * 15 + 1).astype(int)
        confidence_points = np.clip(confidence_points, 1, 16)
        
        # Add predictions to dataframe
        result_df = game_data.copy()
        result_df['ml_predicted_probability'] = probabilities
        result_df['ml_confidence_points'] = confidence_points
        
        return result_df
    
    def save_model(self):
        """Save trained model and preprocessing objects"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns
        }
        joblib.dump(model_data, self.model_path)
        print(f"💾 Model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model and preprocessing objects"""
        if os.path.exists(self.model_path):
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            self.feature_columns = model_data['feature_columns']
            print(f"📂 Model loaded from {self.model_path}")
        else:
            print(f"❌ No model found at {self.model_path}")
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance from trained model"""
        if self.model is None:
            self.load_model()
        
        if self.model is None:
            return pd.DataFrame()
        
        importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df

def main():
    """Example usage of the ML model"""
    db_manager = DatabaseManager()
    ml_model = NFLConfidenceMLModel(db_manager)
    
    # Train model
    try:
        results = ml_model.train_model()
        print("\n🎯 Training Results:")
        for key, value in results.items():
            if key != 'feature_importance':
                print(f"   {key}: {value}")
        
        print("\n🔍 Top Feature Importance:")
        importance_df = ml_model.get_feature_importance()
        print(importance_df.head(10))
        
    except ValueError as e:
        print(f"❌ Training failed: {e}")
        print("💡 Need historical picks data to train the model")

if __name__ == "__main__":
    main()
