#!/usr/bin/env python3
"""
Migrate 2025 season data from v1 to v2 database and prepare for ML-enhanced picks
"""

import pandas as pd
from database_manager import DatabaseManager
from ml_model import NFLConfidenceMLModel
import json
from datetime import datetime

class Season2025Migrator:
    """Migrate 2025 season and prepare ML-enhanced picks"""
    
    def __init__(self):
        self.db_v1 = DatabaseManager(version="v1")
        self.db_v2 = DatabaseManager(version="v2")
        self.ml_model = NFLConfidenceMLModel(self.db_v2)
        self.ml_model.load_model()
    
    def migrate_2025_games(self):
        """Migrate 2025 games from v1 to v2 database"""
        
        print("🔄 Migrating 2025 games from v1 to v2 database...")
        
        # Get 2025 games from v1
        with self.db_v1.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.id, g.season_year, g.week, g.home_team_id, g.away_team_id,
                       t1.name as home_team, t2.name as away_team,
                       g.home_score, g.away_score, g.game_date
                FROM games g
                JOIN teams t1 ON g.home_team_id = t1.id
                JOIN teams t2 ON g.away_team_id = t2.id
                WHERE g.season_year = 2025
                ORDER BY g.week, g.game_date
            """)
            
            columns = [description[0] for description in cursor.description]
            games_2025 = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        print(f"📊 Found {len(games_2025)} 2025 games in v1 database")
        
        # Migrate to v2 database
        migrated_count = 0
        for game in games_2025:
            try:
                # Upsert game in v2 database
                game_id = self.db_v2.upsert_game(
                    season_year=game['season_year'],
                    week=game['week'],
                    home_team=game['home_team'],
                    away_team=game['away_team'],
                    game_date=game['game_date'],
                    home_score=game['home_score'],
                    away_score=game['away_score']
                )
                migrated_count += 1
                
            except Exception as e:
                print(f"⚠️  Error migrating game {game['home_team']} vs {game['away_team']}: {e}")
                continue
        
        print(f"✅ Migrated {migrated_count} 2025 games to v2 database")
        return migrated_count
    
    def load_week1_results(self):
        """Load Week 1 actual results and update games"""
        
        print("🔄 Loading Week 1 actual results...")
        
        # Get Week 1 games
        with self.db_v2.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.id, g.home_team_id, g.away_team_id,
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
        
        print(f"📊 Found {len(week1_games)} Week 1 games")
        
        # Check which games have results
        completed_games = [g for g in week1_games if g['home_score'] is not None and g['away_score'] is not None]
        print(f"✅ {len(completed_games)} games have results")
        
        return week1_games, completed_games
    
    def generate_ml_week1_picks(self, week1_games):
        """Generate what the ML model would have recommended for Week 1"""
        
        print("🤖 Generating ML model recommendations for Week 1...")
        
        ml_recommendations = []
        
        for game in week1_games:
            # Create test data for this game
            test_data = pd.DataFrame([{
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'pick_team': game['home_team'],  # Try home team first
                'home_ml': -110,  # Default ML odds
                'away_ml': -110,  # Default ML odds
                'week': game['week'],
                'season_year': game['season_year']
            }])
            
            # Prepare features and predict for home team
            X_home = self.ml_model.prepare_features(test_data)
            X_home = X_home.fillna(X_home.mean())
            home_prediction = self.ml_model.model.predict(self.ml_model.scaler.transform(X_home))[0]
            home_confidence = max(1, min(16, int(home_prediction * 16)))
            
            # Try away team
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
            
            ml_recommendations.append({
                'game_id': game['id'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'pick_team': pick_team,
                'confidence_points': confidence,
                'win_probability': win_prob,
                'home_score': game['home_score'],
                'away_score': game['away_score']
            })
        
        print(f"✅ Generated {len(ml_recommendations)} ML recommendations")
        return ml_recommendations
    
    def load_original_week1_picks(self):
        """Load original Week 1 picks from CSV"""
        
        try:
            original_df = pd.read_csv('data/outputs/2025/week-week1-picks.csv')
            print(f"✅ Loaded {len(original_df)} original Week 1 picks from CSV")
            return original_df
        except FileNotFoundError:
            print("❌ Original Week 1 picks CSV not found")
            return pd.DataFrame()
    
    def compare_week1_picks(self, original_df, ml_recommendations):
        """Compare original picks vs ML recommendations"""
        
        print("📊 Comparing original picks vs ML recommendations...")
        
        comparison = []
        
        for ml_rec in ml_recommendations:
            # Find matching original pick
            original_match = original_df[
                (original_df['home_team'] == ml_rec['home_team']) & 
                (original_df['away_team'] == ml_rec['away_team'])
            ]
            
            if not original_match.empty:
                orig_row = original_match.iloc[0]
                
                # Determine actual winner
                home_score = ml_rec['home_score']
                away_score = ml_rec['away_score']
                
                if home_score is not None and away_score is not None:
                    if home_score > away_score:
                        actual_winner = ml_rec['home_team']
                    else:
                        actual_winner = ml_rec['away_team']
                    
                    original_correct = (orig_row['pick_team'] == actual_winner)
                    ml_correct = (ml_rec['pick_team'] == actual_winner)
                    
                    comparison.append({
                        'game': f"{ml_rec['away_team']} @ {ml_rec['home_team']}",
                        'original_pick': orig_row['pick_team'],
                        'original_confidence': orig_row['confidence_points'],
                        'ml_pick': ml_rec['pick_team'],
                        'ml_confidence': ml_rec['confidence_points'],
                        'ml_win_prob': ml_rec['win_probability'],
                        'actual_winner': actual_winner,
                        'original_correct': original_correct,
                        'ml_correct': ml_correct,
                        'confidence_change': ml_rec['confidence_points'] - orig_row['confidence_points'],
                        'pick_changed': orig_row['pick_team'] != ml_rec['pick_team'],
                        'home_score': home_score,
                        'away_score': away_score,
                        'margin': abs(home_score - away_score)
                    })
        
        comparison_df = pd.DataFrame(comparison)
        print(f"✅ Created comparison for {len(comparison_df)} games")
        return comparison_df
    
    def generate_comparison_report(self, comparison_df):
        """Generate detailed comparison report"""
        
        report = []
        report.append("# Week 1 Picks: Original vs ML Model Comparison (2025 Season)")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if comparison_df.empty:
            report.append("❌ No comparison data available")
            return "\n".join(report)
        
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
        
        # Complete comparison table
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
    
    def save_results(self, comparison_df, report):
        """Save comparison results"""
        
        # Save CSV
        comparison_df.to_csv('data/outputs/2025/week1-ml-comparison-2025.csv', index=False)
        print("💾 Saved comparison to data/outputs/2025/week1-ml-comparison-2025.csv")
        
        # Save Markdown report
        with open('data/outputs/2025/week1-ml-comparison-2025-report.md', 'w') as f:
            f.write(report)
        print("💾 Saved report to data/outputs/2025/week1-ml-comparison-2025-report.md")
        
        # Save JSON
        comparison_dict = {
            'summary': {
                'total_games': len(comparison_df),
                'pick_changes': int(comparison_df['pick_changed'].sum()) if not comparison_df.empty else 0,
                'original_accuracy': float(comparison_df['original_correct'].mean()) if not comparison_df.empty else 0,
                'ml_accuracy': float(comparison_df['ml_correct'].mean()) if not comparison_df.empty else 0,
                'avg_original_confidence': float(comparison_df['original_confidence'].mean()) if not comparison_df.empty else 0,
                'avg_ml_confidence': float(comparison_df['ml_confidence'].mean()) if not comparison_df.empty else 0,
                'avg_confidence_change': float(comparison_df['confidence_change'].mean()) if not comparison_df.empty else 0
            },
            'games': comparison_df.to_dict('records') if not comparison_df.empty else []
        }
        
        with open('data/outputs/2025/week1-ml-comparison-2025.json', 'w') as f:
            json.dump(comparison_dict, f, indent=2)
        print("💾 Saved JSON to data/outputs/2025/week1-ml-comparison-2025.json")

def main():
    """Run 2025 season migration and Week 1 comparison"""
    
    print("🔄 Migrating 2025 season and comparing Week 1 picks...")
    
    migrator = Season2025Migrator()
    
    # Step 1: Migrate 2025 games
    migrated_count = migrator.migrate_2025_games()
    if migrated_count == 0:
        print("❌ No games migrated. Check v1 database.")
        return
    
    # Step 2: Load Week 1 results
    week1_games, completed_games = migrator.load_week1_results()
    
    # Step 3: Generate ML recommendations
    ml_recommendations = migrator.generate_ml_week1_picks(week1_games)
    
    # Step 4: Load original picks
    original_df = migrator.load_original_week1_picks()
    if original_df.empty:
        print("❌ No original picks found")
        return
    
    # Step 5: Compare picks
    comparison_df = migrator.compare_week1_picks(original_df, ml_recommendations)
    
    # Step 6: Generate report
    report = migrator.generate_comparison_report(comparison_df)
    
    # Step 7: Save results
    migrator.save_results(comparison_df, report)
    
    print("✅ 2025 season migration and Week 1 comparison complete!")
    print("📊 Check the generated files for detailed analysis")
    print("💡 Ready to generate Week 2 picks with ML model!")

if __name__ == "__main__":
    main()


