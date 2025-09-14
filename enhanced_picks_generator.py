#!/usr/bin/env python3
"""
Enhanced picks generator that uses the database for improved workflow.
This replaces the old file-based approach with a database-driven process.
"""
import os
import sys
import argparse
from datetime import datetime, date
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import fetch_odds, events_to_dataframe, export_picks, assign_confidence_points
from database_manager import DatabaseManager
from ml_model import NFLConfidenceMLModel
from espn_prior_week_analysis import ESPNPriorWeekAnalyzer

class EnhancedPicksGenerator:
    """Database-driven picks generator with ML enhancement"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.ml_model = NFLConfidenceMLModel(self.db_manager)
        self.analyzer = ESPNPriorWeekAnalyzer()
    
    def generate_week_picks(self, week: int, year: int = None, use_ml: bool = True) -> bool:
        """
        Complete workflow for generating picks for a given week:
        1. Fetch odds from API
        2. Store in database
        3. Generate picks (with ML if available)
        4. Store picks in database
        5. Export to files
        """
        if year is None:
            year = datetime.now().year
        
        print(f"🎯 Generating picks for Week {week}, {year}")
        print("=" * 50)
        
        # Step 1: Fetch and store odds data
        print("📡 Step 1: Fetching odds data...")
        payload = fetch_odds(week=week)
        
        if not payload or 'events' not in payload:
            print("❌ No odds data available")
            return False
        
        # Store odds in database
        self._store_odds_in_db(payload, year, week)
        print(f"✅ Stored odds for {len(payload['events'])} games")
        
        # Step 2: Convert to dataframe and generate picks
        print("\n🎮 Step 2: Generating picks...")
        df = events_to_dataframe(payload)
        
        if df.empty:
            print("❌ No games found")
            return False
        
        # Step 3: Apply ML enhancement if available
        if use_ml:
            print("🤖 Step 3: Applying ML enhancement...")
            try:
                self.ml_model.load_model()
                df_with_ml = self.ml_model.predict_confidence(df)
                df['confidence_points'] = df_with_ml['ml_confidence_points']
                df['ml_probability'] = df_with_ml['ml_predicted_probability']
                print("✅ ML confidence points applied")
            except Exception as e:
                print(f"⚠️  ML model not available ({e}), using standard ranking")
                df = assign_confidence_points(df)
        else:
            df = assign_confidence_points(df)
        
        # Step 4: Store picks in database
        print("\n💾 Step 4: Storing picks in database...")
        self._store_picks_in_db(df, year, week)
        
        # Step 5: Export to files
        print("\n📄 Step 5: Exporting picks...")
        output_dir = f"data/outputs/{year}"
        os.makedirs(output_dir, exist_ok=True)
        
        csv_path = f"{output_dir}/week-week{week}-picks.csv"
        md_path = f"{output_dir}/week-week{week}-picks.md"
        
        export_picks(df, out_csv=csv_path, out_md=md_path)
        
        print(f"\n🎉 Week {week} picks generated successfully!")
        print(f"📁 Files: {csv_path}, {md_path}")
        print(f"🎮 Games: {len(df)}")
        
        return True
    
    def analyze_prior_week(self, week: int, year: int = None) -> bool:
        """
        Analyze the prior week's results and update the ML model
        """
        if year is None:
            year = datetime.now().year
        
        prior_week = week - 1
        if prior_week < 1:
            print(f"❌ No prior week to analyze for Week {week}")
            return False
        
        print(f"📊 Analyzing Week {prior_week} results...")
        
        # Run the analysis
        analysis = self.analyzer.analyze_prior_week(year, prior_week)
        
        if not analysis:
            print(f"❌ No analysis data for Week {prior_week}")
            return False
        
        # Store analysis in database
        self._store_analysis_in_db(analysis, year, prior_week)
        
        # Update picks with results
        self._update_picks_with_results(year, prior_week, analysis)
        
        # Retrain ML model if we have enough data
        print("\n🤖 Retraining ML model...")
        try:
            results = self.ml_model.train_model()
            print(f"✅ Model retrained - Accuracy: {results['accuracy']:.3f}")
        except Exception as e:
            print(f"⚠️  Model training failed: {e}")
        
        return True
    
    def _store_odds_in_db(self, payload: Dict, year: int, week: int):
        """Store odds data in database"""
        for event in payload.get('events', []):
            home_team = event['home_team']
            away_team = event['away_team']
            
            # Create game
            game_id = self.db_manager.upsert_game(
                year, week, home_team, away_team, 
                event.get('commence_time', '')
            )
            
            # Store odds for each bookmaker
            for bookmaker_data in event.get('bookmakers', []):
                bookmaker = bookmaker_data.get('title', 'Unknown')
                markets = bookmaker_data.get('markets', [])
                
                # H2H odds
                h2h_market = next((m for m in markets if m.get('key') == 'h2h'), {})
                h2h = h2h_market.get('outcomes', [])
                home_ml = None
                away_ml = None
                home_win_prob = None
                away_win_prob = None
                
                for outcome in h2h:
                    if outcome['name'] == home_team:
                        home_ml = outcome.get('price')
                        home_win_prob = outcome.get('probability')
                    elif outcome['name'] == away_team:
                        away_ml = outcome.get('price')
                        away_win_prob = outcome.get('probability')
                
                # Totals
                totals_market = next((m for m in markets if m.get('key') == 'totals'), {})
                totals = totals_market.get('outcomes', [])
                total_points = None
                for outcome in totals:
                    if 'over' in outcome.get('name', '').lower():
                        total_points = outcome.get('point')
                        break
                
                # Insert odds
                self.db_manager.insert_odds(
                    game_id, bookmaker, home_ml, away_ml, total_points,
                    home_win_prob, away_win_prob
                )
    
    def _store_picks_in_db(self, df, year: int, week: int):
        """Store picks in database"""
        for _, row in df.iterrows():
            try:
                # Extract team names
                home_team = row['home_team']
                away_team = row['away_team']
                
                # Get game ID
                game_id = self.db_manager.get_game_id(year, week, home_team, away_team)
                if not game_id:
                    print(f"⚠️  Game not found: {away_team} @ {home_team}")
                    continue
                
                # Insert pick
                self.db_manager.insert_pick(
                    game_id, year, week, row['pick_team'], 
                    row['confidence_points'], row['pick_prob'],
                    row.get('total_points')
                )
                
            except Exception as e:
                print(f"⚠️  Error storing pick for {row['teams']}: {e}")
    
    def _store_analysis_in_db(self, analysis: Dict, year: int, week: int):
        """Store analysis results in database"""
        # Insert main analysis result
        analysis_id = self.db_manager.insert_analysis_result(
            year, week,
            analysis['overall_accuracy'],
            analysis['correct_picks'],
            analysis['total_picks'],
            analysis.get('avg_error', 0.0),
            analysis['dominance_analysis']['blowouts'],
            analysis['dominance_analysis']['close_games'],
            analysis['dominance_analysis']['average_margin']
        )
        
        # Insert confidence accuracy data
        for conf_points, data in analysis['confidence_accuracy'].items():
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO confidence_accuracy 
                    (analysis_id, confidence_points, correct_picks, total_picks, accuracy)
                    VALUES (?, ?, ?, ?, ?)
                """, (analysis_id, int(conf_points), data['correct'], 
                      data['total'], data['accuracy']))
                conn.commit()
    
    def _update_picks_with_results(self, year: int, week: int, analysis: Dict):
        """Update picks with actual results"""
        # Get all picks for the week
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.game_id, p.pick_team_id, p.confidence_points,
                       ht.name as home_team, at.name as away_team, pt.name as pick_team
                FROM picks p
                JOIN games g ON p.game_id = g.id
                JOIN teams ht ON g.home_team_id = ht.id
                JOIN teams at ON g.away_team_id = at.id
                JOIN teams pt ON p.pick_team_id = pt.id
                WHERE p.season_year = ? AND p.week = ?
            """, (year, week))
            picks = cursor.fetchall()
        
        # Update each pick with result
        updated_count = 0
        for pick_id, game_id, pick_team_id, confidence_points, home_team, away_team, pick_team in picks:
            # Find the corresponding game in analysis data
            game_analysis = None
            for game in analysis.get('games_analyzed', []):
                if (game['teams']['home'] == home_team and 
                    game['teams']['away'] == away_team):
                    game_analysis = game
                    break
            
            if game_analysis:
                # Check if pick was correct
                actual_winner = game_analysis['actual']['winner']
                is_correct = (pick_team == actual_winner)
                
                # Update the pick
                self.db_manager.update_pick_result(pick_id, is_correct)
                updated_count += 1
        
        print(f"✅ Updated {updated_count} picks with results")
    
    def get_week_summary(self, week: int, year: int = None) -> Dict:
        """Get summary of picks and analysis for a week"""
        if year is None:
            year = datetime.now().year
        
        with self.db_manager.get_connection() as conn:
            # Get picks summary
            picks_df = self.db_manager.get_game_features(year, week)
            
            # Get analysis summary if available
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM analysis_results 
                WHERE season_year = ? AND week = ?
            """, (year, week))
            analysis = cursor.fetchone()
        
        return {
            'picks': picks_df.to_dict('records') if not picks_df.empty else [],
            'analysis': dict(zip([col[0] for col in cursor.description], analysis)) if analysis else None
        }

def main():
    parser = argparse.ArgumentParser(description="Enhanced NFL confidence picks generator")
    parser.add_argument("--week", type=int, required=True, help="Week number")
    parser.add_argument("--year", type=int, help="Year (defaults to current year)")
    parser.add_argument("--analyze-prior", action="store_true", help="Analyze prior week first")
    parser.add_argument("--no-ml", action="store_true", help="Disable ML enhancement")
    
    args = parser.parse_args()
    
    generator = EnhancedPicksGenerator()
    
    # Analyze prior week if requested
    if args.analyze_prior:
        if not generator.analyze_prior_week(args.week, args.year):
            print("⚠️  Prior week analysis failed, continuing with picks generation")
    
    # Generate picks
    success = generator.generate_week_picks(
        args.week, args.year, use_ml=not args.no_ml
    )
    
    if success:
        print("\n🎉 Enhanced picks generation completed!")
        print("💡 The database now contains all odds, picks, and analysis data")
    else:
        print("❌ Failed to generate picks")

if __name__ == "__main__":
    main()
