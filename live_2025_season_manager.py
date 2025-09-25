#!/usr/bin/env python3
"""
Live 2025 season manager - fetch current data and manage weekly picks
"""

import requests
import pandas as pd
from database_manager import DatabaseManager
from ml_model import NFLConfidenceMLModel
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class Live2025SeasonManager:
    """Manage 2025 season with live API data"""
    
    def __init__(self):
        self.db_manager = DatabaseManager(version="v2")
        self.ml_model = NFLConfidenceMLModel(self.db_manager)
        self.ml_model.load_model()
        
        # API configuration
        self.odds_api_key = os.getenv('ODDS_API_KEY')
        self.odds_base_url = "https://api.the-odds-api.com/v4"
        self.espn_base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        
        if not self.odds_api_key:
            raise ValueError("ODDS_API_KEY not found in environment variables")
    
    def fetch_week1_games_from_espn(self):
        """Fetch Week 1 games from ESPN API"""
        
        print("🔄 Fetching Week 1 games from ESPN API...")
        
        # Week 1 date range (September 4-8, 2025)
        start_date = "20250904"
        end_date = "20250908"
        
        url = f"{self.espn_base_url}/scoreboard"
        params = {
            'dates': f"{start_date}-{end_date}",
            'limit': 1000
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            events = data.get('events', [])
            print(f"✅ Fetched {len(events)} Week 1 games from ESPN")
            return events
            
        except Exception as e:
            print(f"❌ Error fetching Week 1 games: {e}")
            return []
    
    def fetch_full_2025_season_from_espn(self):
        """Fetch all 2025 regular season games from ESPN API"""
        
        print("🔄 Fetching full 2025 regular season games from ESPN API...")
        
        all_events = []
        
        # Fetch games week by week to get complete season
        for week in range(1, 19):  # Regular season weeks 1-18
            week_events = self._fetch_week_games_from_espn(week)
            all_events.extend(week_events)
            print(f"   Week {week}: {len(week_events)} games")
        
        print(f"✅ Fetched {len(all_events)} total games from ESPN")
        return all_events
    
    def _fetch_week_games_from_espn(self, week):
        """Fetch games for a specific week from ESPN"""
        
        # Calculate approximate dates for each week
        week_dates = self._get_week_dates_2025(week)
        
        all_events = []
        for start_date, end_date in week_dates:
            url = f"{self.espn_base_url}/scoreboard"
            params = {
                'dates': f"{start_date}-{end_date}",
                'limit': 1000
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                events = data.get('events', [])
                all_events.extend(events)
                
            except Exception as e:
                print(f"⚠️  Error fetching week {week} games: {e}")
                continue
        
        return all_events
    
    def _get_week_dates_2025(self, week):
        """Get date ranges for each week in 2025 season"""
        
        # Week 1: Sept 4-8
        # Week 2: Sept 11-15
        # Week 3: Sept 18-22
        # etc.
        
        week_start_dates = {
            1: ("20250904", "20250908"),
            2: ("20250911", "20250915"),
            3: ("20250918", "20250922"),
            4: ("20250925", "20250929"),
            5: ("20251002", "20251006"),
            6: ("20251009", "20251013"),
            7: ("20251016", "20251020"),
            8: ("20251023", "20251027"),
            9: ("20251030", "20251103"),
            10: ("20251106", "20251110"),
            11: ("20251113", "20251117"),
            12: ("20251120", "20251124"),
            13: ("20251127", "20251201"),
            14: ("20251204", "20251208"),
            15: ("20251211", "20251215"),
            16: ("20251218", "20251222"),
            17: ("20251225", "20251229"),
            18: ("20260101", "20260105")
        }
        
        return [week_start_dates.get(week, ("20250904", "20250908"))]
    
    def _determine_week_from_date(self, game_date):
        """Determine NFL week from game date"""
        
        if not game_date:
            return 1
        
        try:
            from datetime import datetime
            game_dt = datetime.strptime(game_date, '%Y-%m-%d')
            
            # Week 1 starts September 4, 2025
            season_start = datetime(2025, 9, 4)
            days_diff = (game_dt - season_start).days
            
            if days_diff < 0:
                return 1
            elif days_diff < 7:
                return 1
            elif days_diff < 14:
                return 2
            elif days_diff < 21:
                return 3
            elif days_diff < 28:
                return 4
            elif days_diff < 35:
                return 5
            elif days_diff < 42:
                return 6
            elif days_diff < 49:
                return 7
            elif days_diff < 56:
                return 8
            elif days_diff < 63:
                return 9
            elif days_diff < 70:
                return 10
            elif days_diff < 77:
                return 11
            elif days_diff < 84:
                return 12
            elif days_diff < 91:
                return 13
            elif days_diff < 98:
                return 14
            elif days_diff < 105:
                return 15
            elif days_diff < 112:
                return 16
            elif days_diff < 119:
                return 17
            else:
                return 18
                
        except:
            return 1
    
    def fetch_week1_results(self):
        """Fetch Week 1 results from ESPN API"""
        
        print("🔄 Fetching Week 1 results from ESPN API...")
        
        # Week 1 date range (September 4-8, 2025) - Wednesday to Monday
        start_date = "20250904"
        end_date = "20250908"
        
        url = f"{self.espn_base_url}/scoreboard"
        params = {
            'dates': f"{start_date}-{end_date}",
            'limit': 1000
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            events = data.get('events', [])
            print(f"✅ Fetched {len(events)} Week 1 games from ESPN")
            
            # Process and return results
            week1_results = []
            for event in events:
                if event.get('status', {}).get('type', {}).get('name') == 'STATUS_FINAL':
                    week1_results.append(self._process_espn_game(event))
            
            print(f"✅ Found {len(week1_results)} completed Week 1 games")
            return week1_results
            
        except Exception as e:
            print(f"❌ Error fetching Week 1 results: {e}")
            return []
    
    def _process_espn_game(self, event):
        """Process ESPN game data"""
        
        # Extract team information
        competitions = event.get('competitions', [])
        if not competitions:
            return None
        
        competition = competitions[0]
        competitors = competition.get('competitors', [])
        
        if len(competitors) != 2:
            return None
        
        # Determine home/away teams
        home_team = None
        away_team = None
        home_score = None
        away_score = None
        
        for competitor in competitors:
            team_name = competitor.get('team', {}).get('displayName', '')
            score = competitor.get('score', '0')
            is_home = competitor.get('homeAway') == 'home'
            
            if is_home:
                home_team = team_name
                home_score = int(score) if score else None
            else:
                away_team = team_name
                away_score = int(score) if score else None
        
        # Extract game date
        date_str = event.get('date', '')
        game_date = None
        if date_str:
            try:
                game_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).strftime('%Y-%m-%d')
            except:
                game_date = None
        
        return {
            'away_team': away_team,
            'home_team': home_team,
            'away_score': away_score,
            'home_score': home_score,
            'game_date': game_date,
            'status': event.get('status', {}).get('type', {}).get('name', '')
        }
    
    def update_database_with_espn_data(self, events, week1_results=None):
        """Update database with ESPN API data"""
        
        print("🔄 Updating database with ESPN data...")
        
        # Process events and update games
        games_updated = 0
        for event in events:
            try:
                # Process ESPN event data
                game_data = self._process_espn_game(event)
                if not game_data:
                    continue
                
                home_team = game_data['home_team']
                away_team = game_data['away_team']
                home_score = game_data['home_score']
                away_score = game_data['away_score']
                game_date = game_data['game_date']
                
                # Determine week from game date
                week = self._determine_week_from_date(game_date)
                
                # Upsert game
                game_id = self.db_manager.upsert_game(
                    season_year=2025,
                    week=week,
                    home_team=home_team,
                    away_team=away_team,
                    game_date=game_date,
                    home_score=home_score,
                    away_score=away_score
                )
                
                games_updated += 1
                
            except Exception as e:
                print(f"⚠️  Error updating game: {e}")
                continue
        
        print(f"✅ Updated {games_updated} games in database")
        return games_updated
    
    def _determine_week(self, commence_time):
        """Determine NFL week from commence time"""
        
        try:
            game_date = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
            
            # Simple week determination (you might want more sophisticated logic)
            season_start = datetime(2025, 9, 5)  # Week 1 start
            days_diff = (game_date - season_start).days
            
            if days_diff < 0:
                return 1  # Pre-season or early games
            elif days_diff < 7:
                return 1
            elif days_diff < 14:
                return 2
            elif days_diff < 21:
                return 3
            # Add more weeks as needed
            
            return min(18, (days_diff // 7) + 1)  # Cap at 18 weeks
            
        except:
            return 1  # Default to week 1
    
    def generate_ml_week1_picks(self):
        """Generate ML model recommendations for Week 1"""
        
        print("🤖 Generating ML model recommendations for Week 1...")
        
        # Get Week 1 games from database
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
    
    def compare_week1_picks(self, ml_recommendations):
        """Compare original picks vs ML recommendations"""
        
        print("📊 Comparing original picks vs ML recommendations...")
        
        # Load original picks
        try:
            original_df = pd.read_csv('data/outputs/2025/week-week1-picks.csv')
        except FileNotFoundError:
            print("❌ Original Week 1 picks CSV not found")
            return pd.DataFrame()
        
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
    
    def save_comparison_results(self, comparison_df):
        """Save comparison results"""
        
        if comparison_df.empty:
            print("❌ No comparison data to save")
            return
        
        # Generate report
        report = self._generate_comparison_report(comparison_df)
        
        # Save files
        comparison_df.to_csv('data/outputs/2025/week1-live-ml-comparison.csv', index=False)
        with open('data/outputs/2025/week1-live-ml-comparison-report.md', 'w') as f:
            f.write(report)
        
        print("💾 Saved comparison results")
        print("📊 Check data/outputs/2025/ for detailed analysis")
    
    def _generate_comparison_report(self, comparison_df):
        """Generate comparison report"""
        
        report = []
        report.append("# Week 1 Picks: Original vs ML Model (Live 2025 Season)")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_games = len(comparison_df)
        pick_changes = comparison_df['pick_changed'].sum()
        original_accuracy = comparison_df['original_correct'].mean()
        ml_accuracy = comparison_df['ml_correct'].mean()
        
        report.append("## Summary")
        report.append(f"- **Total Games**: {total_games}")
        report.append(f"- **Pick Changes**: {pick_changes} ({pick_changes/total_games*100:.1f}%)")
        report.append(f"- **Original Accuracy**: {original_accuracy:.1%}")
        report.append(f"- **ML Model Accuracy**: {ml_accuracy:.1%}")
        report.append(f"- **Accuracy Change**: {ml_accuracy - original_accuracy:+.1%}")
        report.append("")
        
        # Game-by-game comparison
        report.append("## Game-by-Game Comparison")
        report.append("| Game | Original | ML | Orig Conf | ML Conf | Change | Orig ✓ | ML ✓ | Winner | Score |")
        report.append("|------|----------|----|-----------|---------|--------|--------|------|--------|-------|")
        
        for _, game in comparison_df.iterrows():
            orig_check = "✅" if game['original_correct'] else "❌"
            ml_check = "✅" if game['ml_correct'] else "❌"
            change_str = f"{game['confidence_change']:+d}" if game['confidence_change'] != 0 else "0"
            
            report.append(f"| {game['game']} | {game['original_pick']} | {game['ml_pick']} | "
                         f"{game['original_confidence']} | {game['ml_confidence']} | {change_str} | "
                         f"{orig_check} | {ml_check} | {game['actual_winner']} | "
                         f"{game['away_score']}-{game['home_score']} |")
        
        return "\n".join(report)

def main():
    """Run live 2025 season management"""
    
    print("🔄 Starting live 2025 season management...")
    
    manager = Live2025SeasonManager()
    
    # Step 1: Fetch Week 1 games and results for comparison
    print("\n📊 Step 1: Analyzing Week 1 picks...")
    week1_events = manager.fetch_week1_games_from_espn()
    if not week1_events:
        print("❌ No Week 1 games fetched from ESPN.")
        return
    
    # Step 2: Update database with Week 1 data (ESPN data includes results)
    week1_games_updated = manager.update_database_with_espn_data(week1_events)
    if week1_games_updated == 0:
        print("❌ No Week 1 games updated in database")
        return
    
    # Step 3: Generate ML recommendations for Week 1
    ml_recommendations = manager.generate_ml_week1_picks()
    
    # Step 4: Compare Week 1 picks
    comparison_df = manager.compare_week1_picks(ml_recommendations)
    
    # Step 5: Save Week 1 comparison results
    manager.save_comparison_results(comparison_df)
    
    # Step 6: Load full 2025 season
    print("\n📅 Step 2: Loading full 2025 season...")
    all_season_events = manager.fetch_full_2025_season_from_espn()
    if all_season_events:
        # Update database with all season games
        all_games_updated = manager.update_database_with_espn_data(all_season_events)
        print(f"✅ Updated {all_games_updated} total games in database")
    
    print("\n✅ Live 2025 season management complete!")
    print("📊 Week 1 comparison saved to data/outputs/2025/")
    print("💡 Ready to generate Week 2 picks with updated model!")

if __name__ == "__main__":
    main()
