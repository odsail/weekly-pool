#!/usr/bin/env python3
"""
Enhanced picks generator that uses ML model for confidence point assignment.
Combines The Odds API data with ML predictions for better accuracy.
"""
import os
import sys
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import fetch_odds, events_to_dataframe, export_picks
from database_manager import DatabaseManager
from ml_model import NFLConfidenceMLModel

class MLPicksGenerator:
    """Generate picks using ML model for confidence assignment"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.ml_model = NFLConfidenceMLModel(self.db_manager)
    
    def generate_ml_picks(self, week: int, year: int = None) -> bool:
        """Generate picks using ML model for confidence assignment"""
        if year is None:
            year = datetime.now().year
        
        print(f"🤖 Generating ML-enhanced picks for Week {week}, {year}...")
        
        # Fetch odds data
        print("📡 Fetching odds data...")
        payload = fetch_odds(week=week)
        
        if not payload or 'events' not in payload:
            print("❌ No odds data available")
            return False
        
        # Convert to dataframe
        df = events_to_dataframe(payload)
        
        if df.empty:
            print("❌ No games found")
            return False
        
        print(f"🎮 Found {len(df)} games")
        
        # Try to load ML model
        try:
            self.ml_model.load_model()
            print("🧠 ML model loaded successfully")
            
            # Generate ML predictions
            df_with_ml = self.ml_model.predict_confidence(df)
            
            # Use ML confidence points instead of simple ranking
            df['confidence_points'] = df_with_ml['ml_confidence_points']
            df['ml_probability'] = df_with_ml['ml_predicted_probability']
            
            print("✅ ML confidence points assigned")
            
        except Exception as e:
            print(f"⚠️  ML model not available ({e}), using standard ranking")
            # Fall back to standard confidence assignment
            from main import assign_confidence_points
            df = assign_confidence_points(df)
        
        # Store picks in database
        self._store_picks_in_db(df, year, week)
        
        # Export picks
        output_dir = f"data/outputs/{year}"
        os.makedirs(output_dir, exist_ok=True)
        
        csv_path = f"{output_dir}/week-week{week}-ml-picks.csv"
        md_path = f"{output_dir}/week-week{week}-ml-picks.md"
        
        export_picks(df, out_csv=csv_path, out_md=md_path)
        
        print(f"✅ ML picks generated:")
        print(f"   📄 {csv_path}")
        print(f"   📄 {md_path}")
        
        return True
    
    def _store_picks_in_db(self, df, year: int, week: int):
        """Store picks in database for future ML training"""
        print("💾 Storing picks in database...")
        
        for _, row in df.iterrows():
            try:
                # Extract team names
                teams = row['teams'].split(' @ ')
                away_team = teams[0]
                home_team = teams[1]
                
                # Get or create game
                game_id = self.db_manager.get_game_id(year, week, home_team, away_team)
                if not game_id:
                    game_id = self.db_manager.upsert_game(
                        year, week, home_team, away_team, 
                        row.get('kickoff', '')
                    )
                
                # Insert pick
                self.db_manager.insert_pick(
                    game_id, year, week, row['pick'], 
                    row['confidence_points'], row['win_probability'],
                    row.get('total_points')
                )
                
            except Exception as e:
                print(f"⚠️  Error storing pick for {row['teams']}: {e}")
    
    def train_model(self) -> bool:
        """Train the ML model on historical data"""
        print("🎓 Training ML model...")
        
        try:
            results = self.ml_model.train_model()
            
            print("✅ Model training completed!")
            print(f"   Accuracy: {results['accuracy']:.3f}")
            print(f"   CV Accuracy: {results['cv_accuracy']:.3f} (+/- {results['cv_std']:.3f})")
            
            print("\n🔍 Top 5 Most Important Features:")
            importance_df = self.ml_model.get_feature_importance()
            for _, row in importance_df.head(5).iterrows():
                print(f"   {row['feature']}: {row['importance']:.3f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Model training failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Generate ML-enhanced NFL confidence picks")
    parser.add_argument("--week", type=int, required=True, help="Week number")
    parser.add_argument("--year", type=int, help="Year (defaults to current year)")
    parser.add_argument("--train", action="store_true", help="Train ML model first")
    
    args = parser.parse_args()
    
    generator = MLPicksGenerator()
    
    # Train model if requested
    if args.train:
        if not generator.train_model():
            print("❌ Training failed, exiting")
            return
    
    # Generate picks
    success = generator.generate_ml_picks(args.week, args.year)
    
    if success:
        print("\n🎉 ML-enhanced picks generated successfully!")
        print("💡 The picks now use machine learning to optimize confidence point assignment")
    else:
        print("❌ Failed to generate picks")

if __name__ == "__main__":
    main()
