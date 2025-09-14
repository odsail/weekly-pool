#!/usr/bin/env python3
"""
Comprehensive prior week analysis system combining multiple data sources.
This analyzes Week N-1 results to improve Week N picks.
"""
import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from test_working_sportsdataio import WorkingSportsDataIO
from espn_api import ESPNAPI

class ComprehensiveAnalyzer:
    """Comprehensive analysis system for prior week results"""
    
    def __init__(self):
        self.sportsdataio = WorkingSportsDataIO()
        self.espn_api = ESPNAPI()
        self.team_mapping = self.sportsdataio.create_team_mapping()
        self.accuracy_history = []
    
    def analyze_prior_week(self, year: int, week: int) -> Dict:
        """
        Analyze the prior week's results to improve current week picks.
        
        Args:
            year: NFL season year
            week: Current week number (analyzes week-1)
            
        Returns:
            Comprehensive analysis results
        """
        prior_week = week - 1
        if prior_week < 1:
            print(f"❌ Cannot analyze prior week for Week {week}")
            return {}
        
        print(f"🔍 Analyzing Week {prior_week} results to improve Week {week} picks...")
        
        # Get our predictions for the prior week
        predictions = self._load_week_predictions(year, prior_week)
        if not predictions:
            print(f"❌ No predictions found for Week {prior_week}")
            return {}
        
        # Get actual results from ESPN
        actual_results = self.espn_api.get_week_results(year, prior_week)
        if not actual_results:
            print(f"❌ No results found for Week {prior_week}")
            return {}
        
        # Match predictions with results
        matched_games = self._match_predictions_with_results(predictions, actual_results)
        
        if not matched_games:
            print(f"❌ No games could be matched between predictions and results")
            return {}
        
        # Perform comprehensive analysis
        analysis = self._perform_comprehensive_analysis(matched_games, year, prior_week)
        
        # Save analysis for future use
        self._save_analysis(year, prior_week, analysis)
        
        return analysis
    
    def get_confidence_adjustments(self, current_week: int) -> Dict:
        """
        Get confidence adjustments based on historical accuracy.
        
        Args:
            current_week: Current week number
            
        Returns:
            Dictionary with confidence point adjustments
        """
        # Load all previous week analyses
        all_analyses = self._load_all_analyses()
        
        if not all_analyses:
            print("📊 No historical data available for adjustments")
            return {}
        
        # Calculate weighted accuracy by confidence level
        adjustments = self._calculate_confidence_adjustments(all_analyses, current_week)
        
        return adjustments
    
    def _load_week_predictions(self, year: int, week: int) -> Optional[pd.DataFrame]:
        """Load our predictions for a specific week"""
        try:
            # Try different possible file names
            possible_files = [
                f"data/outputs/{year}/week-week{week}-picks.csv",
                f"data/outputs/{year}/week{week}-picks.csv",
                f"data/outputs/{year}/week-{week}-picks.csv"
            ]
            
            for file_path in possible_files:
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                    print(f"📁 Loaded predictions from {file_path}")
                    return df
            
            print(f"❌ No prediction file found for Week {week}")
            return None
            
        except Exception as e:
            print(f"❌ Error loading predictions: {e}")
            return None
    
    def _match_predictions_with_results(self, predictions: pd.DataFrame, results: List[Dict]) -> List[Dict]:
        """Match our predictions with actual results"""
        matched_games = []
        
        for _, pred_row in predictions.iterrows():
            pred_home = pred_row.get("home_team", "").strip()
            pred_away = pred_row.get("away_team", "").strip()
            
            # Find matching result
            for result in results:
                result_home = result.get("home_team", "").strip()
                result_away = result.get("away_team", "").strip()
                
                # Match by team names (case insensitive)
                if (pred_home.lower() == result_home.lower() and 
                    pred_away.lower() == result_away.lower()):
                    
                    matched_game = {
                        "prediction": {
                            "pick_team": pred_row.get("pick_team"),
                            "confidence_points": pred_row.get("confidence_points"),
                            "pick_prob": pred_row.get("pick_prob"),
                            "total_points": pred_row.get("total_points")
                        },
                        "actual": {
                            "winner": result.get("winner"),
                            "home_score": result.get("home_score"),
                            "away_score": result.get("away_score"),
                            "total_points": result.get("total_points")
                        },
                        "teams": {
                            "home": pred_home,
                            "away": pred_away
                        }
                    }
                    matched_games.append(matched_game)
                    break
        
        print(f"✅ Matched {len(matched_games)} games out of {len(predictions)} predictions")
        return matched_games
    
    def _perform_comprehensive_analysis(self, matched_games: List[Dict], year: int, week: int) -> Dict:
        """Perform comprehensive analysis of matched games"""
        if not matched_games:
            return {}
        
        # Basic accuracy metrics
        correct_picks = sum(1 for game in matched_games 
                          if game["prediction"]["pick_team"] == game["actual"]["winner"])
        total_picks = len(matched_games)
        overall_accuracy = correct_picks / total_picks if total_picks > 0 else 0
        
        # Accuracy by confidence level
        confidence_accuracy = {}
        for game in matched_games:
            conf_points = game["prediction"]["confidence_points"]
            is_correct = game["prediction"]["pick_team"] == game["actual"]["winner"]
            
            if conf_points not in confidence_accuracy:
                confidence_accuracy[conf_points] = {"correct": 0, "total": 0}
            
            confidence_accuracy[conf_points]["total"] += 1
            if is_correct:
                confidence_accuracy[conf_points]["correct"] += 1
        
        # Calculate accuracy percentages
        for conf_points in confidence_accuracy:
            data = confidence_accuracy[conf_points]
            data["accuracy"] = data["correct"] / data["total"] if data["total"] > 0 else 0
        
        # Total points accuracy (tiebreaker)
        total_points_errors = []
        for game in matched_games:
            pred_total = game["prediction"]["total_points"]
            actual_total = game["actual"]["total_points"]
            if pred_total is not None and actual_total is not None:
                error = abs(pred_total - actual_total)
                total_points_errors.append(error)
        
        avg_total_error = np.mean(total_points_errors) if total_points_errors else 0
        
        # Team performance analysis
        team_performance = self._analyze_team_performance(matched_games)
        
        # Game dominance analysis
        dominance_analysis = self._analyze_game_dominance(matched_games)
        
        analysis = {
            "week": week,
            "year": year,
            "overall_accuracy": overall_accuracy,
            "correct_picks": correct_picks,
            "total_picks": total_picks,
            "confidence_accuracy": confidence_accuracy,
            "total_points_accuracy": {
                "avg_error": avg_total_error,
                "errors": total_points_errors
            },
            "team_performance": team_performance,
            "dominance_analysis": dominance_analysis,
            "games_analyzed": matched_games
        }
        
        return analysis
    
    def _analyze_team_performance(self, matched_games: List[Dict]) -> Dict:
        """Analyze team performance patterns"""
        team_stats = {}
        
        for game in matched_games:
            home_team = game["teams"]["home"]
            away_team = game["teams"]["away"]
            home_score = game["actual"]["home_score"]
            away_score = game["actual"]["away_score"]
            
            # Initialize team stats if not exists
            for team in [home_team, away_team]:
                if team not in team_stats:
                    team_stats[team] = {
                        "games": 0,
                        "wins": 0,
                        "total_points_scored": 0,
                        "total_points_allowed": 0,
                        "point_differential": 0,
                        "dominant_wins": 0,  # Wins by 14+ points
                        "close_wins": 0,     # Wins by 7 or fewer points
                        "blowout_losses": 0  # Losses by 14+ points
                    }
            
            # Update home team stats
            team_stats[home_team]["games"] += 1
            team_stats[home_team]["total_points_scored"] += home_score
            team_stats[home_team]["total_points_allowed"] += away_score
            team_stats[home_team]["point_differential"] += (home_score - away_score)
            
            if home_score > away_score:
                team_stats[home_team]["wins"] += 1
                margin = home_score - away_score
                if margin >= 14:
                    team_stats[home_team]["dominant_wins"] += 1
                elif margin <= 7:
                    team_stats[home_team]["close_wins"] += 1
            else:
                margin = away_score - home_score
                if margin >= 14:
                    team_stats[home_team]["blowout_losses"] += 1
            
            # Update away team stats
            team_stats[away_team]["games"] += 1
            team_stats[away_team]["total_points_scored"] += away_score
            team_stats[away_team]["total_points_allowed"] += home_score
            team_stats[away_team]["point_differential"] += (away_score - home_score)
            
            if away_score > home_score:
                team_stats[away_team]["wins"] += 1
                margin = away_score - home_score
                if margin >= 14:
                    team_stats[away_team]["dominant_wins"] += 1
                elif margin <= 7:
                    team_stats[away_team]["close_wins"] += 1
            else:
                margin = home_score - away_score
                if margin >= 14:
                    team_stats[away_team]["blowout_losses"] += 1
        
        # Calculate averages and percentages
        for team, stats in team_stats.items():
            if stats["games"] > 0:
                stats["win_percentage"] = stats["wins"] / stats["games"]
                stats["avg_points_scored"] = stats["total_points_scored"] / stats["games"]
                stats["avg_points_allowed"] = stats["total_points_allowed"] / stats["games"]
                stats["avg_point_differential"] = stats["point_differential"] / stats["games"]
        
        return team_stats
    
    def _analyze_game_dominance(self, matched_games: List[Dict]) -> Dict:
        """Analyze game dominance patterns"""
        dominance_stats = {
            "total_games": len(matched_games),
            "dominant_wins": 0,      # Wins by 14+ points
            "close_games": 0,        # Games decided by 7 or fewer points
            "blowouts": 0,           # Games decided by 14+ points
            "average_margin": 0,
            "margins": []
        }
        
        for game in matched_games:
            home_score = game["actual"]["home_score"]
            away_score = game["actual"]["away_score"]
            margin = abs(home_score - away_score)
            
            dominance_stats["margins"].append(margin)
            
            if margin >= 14:
                dominance_stats["blowouts"] += 1
                if margin >= 14:
                    dominance_stats["dominant_wins"] += 1
            elif margin <= 7:
                dominance_stats["close_games"] += 1
        
        if dominance_stats["margins"]:
            dominance_stats["average_margin"] = np.mean(dominance_stats["margins"])
        
        return dominance_stats
    
    def _save_analysis(self, year: int, week: int, analysis: Dict):
        """Save analysis results for future reference"""
        try:
            os.makedirs(f"data/analysis/{year}", exist_ok=True)
            file_path = f"data/analysis/{year}/week{week}-analysis.json"
            
            with open(file_path, "w") as f:
                json.dump(analysis, f, indent=2)
            
            print(f"💾 Saved analysis to {file_path}")
            
        except Exception as e:
            print(f"❌ Error saving analysis: {e}")
    
    def _load_all_analyses(self) -> List[Dict]:
        """Load all previous week analyses"""
        analyses = []
        
        try:
            # Look for analysis files in data/analysis/
            if os.path.exists("data/analysis/"):
                for year_dir in os.listdir("data/analysis/"):
                    year_path = os.path.join("data/analysis", year_dir)
                    if not os.path.isdir(year_path):
                        continue
                    
                    for file_name in os.listdir(year_path):
                        if file_name.startswith("week") and file_name.endswith("-analysis.json"):
                            file_path = os.path.join(year_path, file_name)
                            with open(file_path, "r") as f:
                                analysis = json.load(f)
                                analysis["week"] = int(file_name.split("week")[1].split("-")[0])
                                analysis["year"] = int(year_dir)
                                analyses.append(analysis)
            
            # Sort by week
            analyses.sort(key=lambda x: (x["year"], x["week"]))
            
        except Exception as e:
            print(f"❌ Error loading analyses: {e}")
        
        return analyses
    
    def _calculate_confidence_adjustments(self, all_analyses: List[Dict], current_week: int) -> Dict:
        """Calculate confidence adjustments based on historical accuracy"""
        adjustments = {}
        
        # Collect accuracy data by confidence level
        confidence_data = {}
        
        for analysis in all_analyses:
            week_num = analysis["week"]
            # Use exponential weighting (recent weeks matter more)
            weight = 0.9 ** (current_week - week_num - 1)
            
            for conf_points, data in analysis.get("confidence_accuracy", {}).items():
                if conf_points not in confidence_data:
                    confidence_data[conf_points] = {"weighted_accuracy": 0, "total_weight": 0}
                
                confidence_data[conf_points]["weighted_accuracy"] += data["accuracy"] * weight
                confidence_data[conf_points]["total_weight"] += weight
        
        # Calculate weighted average accuracy for each confidence level
        for conf_points, data in confidence_data.items():
            if data["total_weight"] > 0:
                weighted_avg = data["weighted_accuracy"] / data["total_weight"]
                # Adjustment factor: if accuracy is lower than expected, reduce confidence
                expected_accuracy = 0.5 + (conf_points - 1) * 0.02  # Rough expected accuracy
                adjustment_factor = weighted_avg / expected_accuracy if expected_accuracy > 0 else 1.0
                adjustments[conf_points] = adjustment_factor
        
        return adjustments

def main():
    """Test the comprehensive analyzer"""
    analyzer = ComprehensiveAnalyzer()
    
    # Analyze Week 1 (since we're in Week 2)
    analysis = analyzer.analyze_prior_week(2025, 2)
    
    if analysis:
        print("\n📊 Week 1 Comprehensive Analysis Results:")
        print("=" * 50)
        print(f"Overall Accuracy: {analysis['overall_accuracy']:.1%}")
        print(f"Correct Picks: {analysis['correct_picks']}/{analysis['total_picks']}")
        print(f"Average Total Points Error: {analysis['total_points_accuracy']['avg_error']:.1f}")
        
        print("\nAccuracy by Confidence Level:")
        for conf_points in sorted(analysis['confidence_accuracy'].keys()):
            data = analysis['confidence_accuracy'][conf_points]
            print(f"  {conf_points:2d} points: {data['accuracy']:.1%} ({data['correct']}/{data['total']})")
        
        print("\nTeam Performance Summary:")
        for team, stats in analysis['team_performance'].items():
            if stats['games'] > 0:
                print(f"  {team}: {stats['wins']}/{stats['games']} wins ({stats['win_percentage']:.1%}), "
                      f"Avg Score: {stats['avg_points_scored']:.1f}, "
                      f"Avg Allowed: {stats['avg_points_allowed']:.1f}")
        
        print("\nGame Dominance Analysis:")
        dom = analysis['dominance_analysis']
        print(f"  Total Games: {dom['total_games']}")
        print(f"  Blowouts (14+ pts): {dom['blowouts']}")
        print(f"  Close Games (≤7 pts): {dom['close_games']}")
        print(f"  Average Margin: {dom['average_margin']:.1f} points")
        
        # Get adjustments for Week 2
        adjustments = analyzer.get_confidence_adjustments(2)
        if adjustments:
            print("\nConfidence Adjustments for Week 2:")
            for conf_points, factor in sorted(adjustments.items()):
                print(f"  {conf_points:2d} points: {factor:.2f}x adjustment")

if __name__ == "__main__":
    main()
