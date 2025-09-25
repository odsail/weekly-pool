#!/usr/bin/env python3
"""
Compare Week 1 picks: Original vs ML Model predictions
"""

import pandas as pd
from database_manager import DatabaseManager
from ml_model import NFLConfidenceMLModel
import json
from datetime import datetime

class Week1MLComparison:
    """Compare original Week 1 picks with ML model predictions"""
    
    def __init__(self):
        self.db_manager = DatabaseManager(version="v2")
        self.ml_model = NFLConfidenceMLModel(self.db_manager)
        self.ml_model.load_model()
    
    def load_original_week1_picks(self) -> pd.DataFrame:
        """Load original Week 1 picks from CSV"""
        try:
            # Try to load from CSV file
            df = pd.read_csv('data/outputs/2025/week-week1-picks.csv')
            print(f"✅ Loaded {len(df)} original Week 1 picks from CSV")
            return df
        except FileNotFoundError:
            print("❌ Original Week 1 picks CSV not found")
            return pd.DataFrame()
    
    def get_week1_games_from_db(self) -> pd.DataFrame:
        """Get Week 1 games from database"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.id, g.season_year, g.week, 
                       t1.name as home_team, t2.name as away_team,
                       g.home_score, g.away_score, g.game_date
                FROM games g
                JOIN teams t1 ON g.home_team_id = t1.id
                JOIN teams t2 ON g.away_team_id = t2.id
                WHERE g.season_year = 2024 AND g.week = 1
                ORDER BY g.game_date
            """)
            
            columns = [description[0] for description in cursor.description]
            games_df = pd.DataFrame([dict(zip(columns, row)) for row in cursor.fetchall()])
            
        print(f"✅ Found {len(games_df)} Week 1 games in database")
        return games_df
    
    def generate_ml_predictions(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Generate ML model predictions for Week 1 games"""
        
        ml_predictions = []
        
        for _, game in games_df.iterrows():
            # Create test data for this game
            test_data = pd.DataFrame([{
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'pick_team': game['home_team'],  # Assume picking home team initially
                'home_ml': -110,  # Default ML odds
                'away_ml': -110,  # Default ML odds
                'week': game['week'],
                'season_year': game['season_year']
            }])
            
            # Prepare features
            X = self.ml_model.prepare_features(test_data)
            X = X.fillna(X.mean())
            
            # Make prediction for home team
            home_prediction = self.ml_model.model.predict(self.ml_model.scaler.transform(X))[0]
            home_confidence = max(1, min(16, int(home_prediction * 16)))
            
            # Now try away team
            test_data_away = test_data.copy()
            test_data_away['pick_team'] = game['away_team']
            X_away = self.ml_model.prepare_features(test_data_away)
            X_away = X_away.fillna(X_away.mean())
            
            away_prediction = self.ml_model.model.predict(self.ml_model.scaler.transform(X_away))[0]
            away_confidence = max(1, min(16, int(away_prediction * 16)))
            
            # Choose the team with higher confidence
            if home_confidence >= away_confidence:
                pick_team = game['home_team']
                confidence = home_confidence
                win_prob = home_prediction
            else:
                pick_team = game['away_team']
                confidence = away_confidence
                win_prob = away_prediction
            
            ml_predictions.append({
                'game_id': game['id'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'pick_team': pick_team,
                'confidence_points': confidence,
                'win_probability': win_prob,
                'home_confidence': home_confidence,
                'away_confidence': away_confidence,
                'home_score': game['home_score'],
                'away_score': game['away_score']
            })
        
        ml_df = pd.DataFrame(ml_predictions)
        print(f"✅ Generated {len(ml_df)} ML predictions for Week 1")
        return ml_df
    
    def compare_picks(self, original_df: pd.DataFrame, ml_df: pd.DataFrame) -> pd.DataFrame:
        """Compare original picks with ML predictions"""
        
        # Merge the dataframes
        comparison = []
        
        for _, ml_row in ml_df.iterrows():
            # Find matching original pick
            original_match = original_df[
                (original_df['home_team'] == ml_row['home_team']) & 
                (original_df['away_team'] == ml_row['away_team'])
            ]
            
            if not original_match.empty:
                orig_row = original_match.iloc[0]
                
                # Determine if original pick was correct
                home_score = ml_row['home_score']
                away_score = ml_row['away_score']
                
                if home_score > away_score:
                    actual_winner = ml_row['home_team']
                else:
                    actual_winner = ml_row['away_team']
                
                original_correct = (orig_row['pick_team'] == actual_winner)
                ml_correct = (ml_row['pick_team'] == actual_winner)
                
                comparison.append({
                    'game': f"{ml_row['away_team']} @ {ml_row['home_team']}",
                    'original_pick': orig_row['pick_team'],
                    'original_confidence': orig_row['confidence_points'],
                    'ml_pick': ml_row['pick_team'],
                    'ml_confidence': ml_row['confidence_points'],
                    'ml_win_prob': ml_row['win_probability'],
                    'actual_winner': actual_winner,
                    'original_correct': original_correct,
                    'ml_correct': ml_correct,
                    'confidence_change': ml_row['confidence_points'] - orig_row['confidence_points'],
                    'pick_changed': orig_row['pick_team'] != ml_row['pick_team'],
                    'home_score': home_score,
                    'away_score': away_score,
                    'margin': abs(home_score - away_score)
                })
        
        comparison_df = pd.DataFrame(comparison)
        print(f"✅ Created comparison for {len(comparison_df)} games")
        return comparison_df
    
    def generate_comparison_report(self, comparison_df: pd.DataFrame):
        """Generate detailed comparison report"""
        
        report = []
        report.append("# Week 1 Picks: Original vs ML Model Comparison")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary statistics
        total_games = len(comparison_df)
        pick_changes = comparison_df['pick_changed'].sum()
        original_accuracy = comparison_df['original_correct'].mean()
        ml_accuracy = comparison_df['ml_correct'].mean()
        
        report.append("## Summary Statistics")
        report.append(f"- **Total Games**: {total_games}")
        report.append(f"- **Pick Changes**: {pick_changes} ({pick_changes/total_games*100:.1f}%)")
        report.append(f"- **Original Accuracy**: {original_accuracy:.1%}")
        report.append(f"- **ML Model Accuracy**: {ml_accuracy:.1%}")
        report.append(f"- **Accuracy Change**: {ml_accuracy - original_accuracy:+.1%}")
        report.append("")
        
        # Confidence analysis
        avg_original_conf = comparison_df['original_confidence'].mean()
        avg_ml_conf = comparison_df['ml_confidence'].mean()
        avg_confidence_change = comparison_df['confidence_change'].mean()
        
        report.append("## Confidence Analysis")
        report.append(f"- **Average Original Confidence**: {avg_original_conf:.1f} points")
        report.append(f"- **Average ML Confidence**: {avg_ml_conf:.1f} points")
        report.append(f"- **Average Confidence Change**: {avg_confidence_change:+.1f} points")
        report.append("")
        
        # Games where picks changed
        if pick_changes > 0:
            report.append("## Games Where Picks Changed")
            changed_games = comparison_df[comparison_df['pick_changed']]
            for _, game in changed_games.iterrows():
                report.append(f"### {game['game']}")
                report.append(f"- **Original**: {game['original_pick']} ({game['original_confidence']} pts)")
                report.append(f"- **ML Model**: {game['ml_pick']} ({game['ml_confidence']} pts)")
                report.append(f"- **Actual Winner**: {game['actual_winner']}")
                report.append(f"- **Original Correct**: {'✅' if game['original_correct'] else '❌'}")
                report.append(f"- **ML Correct**: {'✅' if game['ml_correct'] else '❌'}")
                report.append(f"- **Score**: {game['away_score']}-{game['home_score']} (margin: {game['margin']})")
                report.append("")
        
        # Confidence changes
        report.append("## Significant Confidence Changes")
        significant_changes = comparison_df[abs(comparison_df['confidence_change']) >= 3]
        if not significant_changes.empty:
            for _, game in significant_changes.iterrows():
                report.append(f"### {game['game']}")
                report.append(f"- **Original**: {game['original_confidence']} pts")
                report.append(f"- **ML Model**: {game['ml_confidence']} pts")
                report.append(f"- **Change**: {game['confidence_change']:+d} pts")
                report.append(f"- **ML Win Probability**: {game['ml_win_prob']:.3f}")
                report.append("")
        
        # Game-by-game comparison
        report.append("## Complete Game-by-Game Comparison")
        report.append("")
        report.append("| Game | Original Pick | ML Pick | Orig Conf | ML Conf | Change | Orig ✓ | ML ✓ | Winner | Score |")
        report.append("|------|---------------|---------|-----------|---------|--------|--------|------|--------|-------|")
        
        for _, game in comparison_df.iterrows():
            orig_check = "✅" if game['original_correct'] else "❌"
            ml_check = "✅" if game['ml_correct'] else "❌"
            change_str = f"{game['confidence_change']:+d}" if game['confidence_change'] != 0 else "0"
            
            report.append(f"| {game['game']} | {game['original_pick']} | {game['ml_pick']} | "
                         f"{game['original_confidence']} | {game['ml_confidence']} | {change_str} | "
                         f"{orig_check} | {ml_check} | {game['actual_winner']} | "
                         f"{game['away_score']}-{game['home_score']} |")
        
        return "\n".join(report)
    
    def save_comparison(self, comparison_df: pd.DataFrame, report: str):
        """Save comparison results"""
        
        # Save CSV
        comparison_df.to_csv('data/outputs/2025/week1-ml-comparison.csv', index=False)
        print("💾 Saved comparison to data/outputs/2025/week1-ml-comparison.csv")
        
        # Save Markdown report
        with open('data/outputs/2025/week1-ml-comparison-report.md', 'w') as f:
            f.write(report)
        print("💾 Saved report to data/outputs/2025/week1-ml-comparison-report.md")
        
        # Save JSON for programmatic access
        comparison_dict = {
            'summary': {
                'total_games': len(comparison_df),
                'pick_changes': int(comparison_df['pick_changed'].sum()),
                'original_accuracy': float(comparison_df['original_correct'].mean()),
                'ml_accuracy': float(comparison_df['ml_correct'].mean()),
                'avg_original_confidence': float(comparison_df['original_confidence'].mean()),
                'avg_ml_confidence': float(comparison_df['ml_confidence'].mean()),
                'avg_confidence_change': float(comparison_df['confidence_change'].mean())
            },
            'games': comparison_df.to_dict('records')
        }
        
        with open('data/outputs/2025/week1-ml-comparison.json', 'w') as f:
            json.dump(comparison_dict, f, indent=2)
        print("💾 Saved JSON to data/outputs/2025/week1-ml-comparison.json")

def main():
    """Run Week 1 ML comparison"""
    
    print("🔄 Comparing Week 1 picks: Original vs ML Model")
    
    comparator = Week1MLComparison()
    
    # Load original picks
    original_df = comparator.load_original_week1_picks()
    if original_df.empty:
        print("❌ Cannot proceed without original Week 1 picks")
        return
    
    # Get Week 1 games from database
    games_df = comparator.get_week1_games_from_db()
    if games_df.empty:
        print("❌ No Week 1 games found in database")
        return
    
    # Generate ML predictions
    ml_df = comparator.generate_ml_predictions(games_df)
    
    # Compare picks
    comparison_df = comparator.compare_picks(original_df, ml_df)
    
    # Generate report
    report = comparator.generate_comparison_report(comparison_df)
    
    # Save results
    comparator.save_comparison(comparison_df, report)
    
    print("✅ Week 1 ML comparison complete!")
    print("📊 Check the generated files for detailed analysis")

if __name__ == "__main__":
    main()
