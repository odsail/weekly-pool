#!/usr/bin/env python3
"""
Export prior week analysis results to CSV and Markdown formats.
This creates readable reports similar to the picks files.
"""
import os
import json
import pandas as pd
from typing import Dict, List, Optional
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from espn_prior_week_analysis import ESPNPriorWeekAnalyzer

class AnalysisExporter:
    """Export analysis results to readable formats"""
    
    def __init__(self):
        self.analyzer = ESPNPriorWeekAnalyzer()
    
    def export_week_analysis(self, year: int, week: int) -> bool:
        """
        Export analysis results for a specific week to CSV and Markdown.
        
        Args:
            year: NFL season year
            week: Week number to analyze
            
        Returns:
            True if successful, False otherwise
        """
        print(f"📊 Exporting Week {week} analysis results...")
        
        # Load the analysis data
        analysis_file = f"data/analysis/{year}/week{week}-analysis.json"
        if not os.path.exists(analysis_file):
            print(f"❌ Analysis file not found: {analysis_file}")
            return False
        
        try:
            with open(analysis_file, "r") as f:
                analysis = json.load(f)
        except Exception as e:
            print(f"❌ Error loading analysis: {e}")
            return False
        
        # Create output directory
        os.makedirs(f"data/outputs/{year}", exist_ok=True)
        
        # Export to CSV
        csv_success = self._export_to_csv(analysis, year, week)
        
        # Export to Markdown
        md_success = self._export_to_markdown(analysis, year, week)
        
        return csv_success and md_success
    
    def _export_to_csv(self, analysis: Dict, year: int, week: int) -> bool:
        """Export analysis to CSV format"""
        try:
            # Create summary data
            summary_data = {
                "metric": [
                    "Overall Accuracy",
                    "Correct Picks", 
                    "Total Picks",
                    "Average Total Points Error",
                    "Total Games",
                    "Blowouts (14+ pts)",
                    "Close Games (≤7 pts)",
                    "Average Margin"
                ],
                "value": [
                    f"{analysis['overall_accuracy']:.1%}",
                    analysis['correct_picks'],
                    analysis['total_picks'],
                    f"{analysis['total_points_accuracy']['avg_error']:.1f}",
                    analysis['dominance_analysis']['total_games'],
                    analysis['dominance_analysis']['blowouts'],
                    analysis['dominance_analysis']['close_games'],
                    f"{analysis['dominance_analysis']['average_margin']:.1f}"
                ]
            }
            
            # Create confidence accuracy data
            conf_data = []
            for conf_points, data in analysis['confidence_accuracy'].items():
                conf_data.append({
                    "confidence_points": int(conf_points),
                    "correct_picks": data['correct'],
                    "total_picks": data['total'],
                    "accuracy": f"{data['accuracy']:.1%}"
                })
            
            # Create team performance data
            team_data = []
            for team, stats in analysis['team_performance'].items():
                if stats['games'] > 0:
                    team_data.append({
                        "team": team,
                        "games": stats['games'],
                        "wins": stats['wins'],
                        "win_percentage": f"{stats['win_percentage']:.1%}",
                        "avg_points_scored": f"{stats['avg_points_scored']:.1f}",
                        "avg_points_allowed": f"{stats['avg_points_allowed']:.1f}",
                        "avg_point_differential": f"{stats['avg_point_differential']:.1f}",
                        "dominant_wins": stats['dominant_wins'],
                        "close_wins": stats['close_wins'],
                        "blowout_losses": stats['blowout_losses']
                    })
            
            # Create game-by-game analysis data
            game_data = []
            for game in analysis['games_analyzed']:
                game_data.append({
                    "home_team": game['teams']['home'],
                    "away_team": game['teams']['away'],
                    "predicted_winner": game['prediction']['pick_team'],
                    "actual_winner": game['actual']['winner'],
                    "correct": "Yes" if game['prediction']['pick_team'] == game['actual']['winner'] else "No",
                    "confidence_points": game['prediction']['confidence_points'],
                    "predicted_total": game['prediction']['total_points'],
                    "actual_total": game['actual']['total_points'],
                    "total_error": abs(game['prediction']['total_points'] - game['actual']['total_points']) if game['prediction']['total_points'] and game['actual']['total_points'] else None,
                    "home_score": game['actual']['home_score'],
                    "away_score": game['actual']['away_score'],
                    "margin": abs(game['actual']['home_score'] - game['actual']['away_score'])
                })
            
            # Export summary
            summary_df = pd.DataFrame(summary_data)
            summary_file = f"data/outputs/{year}/week{week}-analysis-summary.csv"
            summary_df.to_csv(summary_file, index=False)
            print(f"✅ Exported summary to {summary_file}")
            
            # Export confidence accuracy
            conf_df = pd.DataFrame(conf_data)
            conf_file = f"data/outputs/{year}/week{week}-confidence-accuracy.csv"
            conf_df.to_csv(conf_file, index=False)
            print(f"✅ Exported confidence accuracy to {conf_file}")
            
            # Export team performance
            team_df = pd.DataFrame(team_data)
            team_file = f"data/outputs/{year}/week{week}-team-performance.csv"
            team_df.to_csv(team_file, index=False)
            print(f"✅ Exported team performance to {team_file}")
            
            # Export game-by-game analysis
            game_df = pd.DataFrame(game_data)
            game_file = f"data/outputs/{year}/week{week}-game-analysis.csv"
            game_df.to_csv(game_file, index=False)
            print(f"✅ Exported game analysis to {game_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return False
    
    def _export_to_markdown(self, analysis: Dict, year: int, week: int) -> bool:
        """Export analysis to Markdown format"""
        try:
            md_file = f"data/outputs/{year}/week{week}-analysis-report.md"
            
            with open(md_file, "w") as f:
                # Header
                f.write(f"# Week {week} Analysis Report\n\n")
                f.write(f"**Season:** {year}  \n")
                f.write(f"**Analysis Date:** {analysis.get('analysis_date', 'N/A')}  \n\n")
                
                # Summary
                f.write("## 📊 Summary\n\n")
                f.write(f"- **Overall Accuracy:** {analysis['overall_accuracy']:.1%}\n")
                f.write(f"- **Correct Picks:** {analysis['correct_picks']}/{analysis['total_picks']}\n")
                f.write(f"- **Average Total Points Error:** {analysis['total_points_accuracy']['avg_error']:.1f}\n\n")
                
                # Confidence Accuracy
                f.write("## 🎯 Accuracy by Confidence Level\n\n")
                f.write("| Points | Correct | Total | Accuracy |\n")
                f.write("|--------|---------|-------|----------|\n")
                
                for conf_points in sorted(analysis['confidence_accuracy'].keys(), key=int):
                    data = analysis['confidence_accuracy'][conf_points]
                    f.write(f"| {int(conf_points):2d} | {data['correct']:2d} | {data['total']:2d} | {data['accuracy']:6.1%} |\n")
                
                f.write("\n")
                
                # Game Dominance
                dom = analysis['dominance_analysis']
                f.write("## 🏈 Game Dominance Analysis\n\n")
                f.write(f"- **Total Games:** {dom['total_games']}\n")
                f.write(f"- **Blowouts (14+ pts):** {dom['blowouts']}\n")
                f.write(f"- **Close Games (≤7 pts):** {dom['close_games']}\n")
                f.write(f"- **Average Margin:** {dom['average_margin']:.1f} points\n\n")
                
                # Team Performance
                f.write("## 👥 Team Performance Summary\n\n")
                f.write("| Team | Games | Wins | Win% | Avg Score | Avg Allowed | Diff |\n")
                f.write("|------|-------|------|------|-----------|-------------|------|\n")
                
                # Sort teams by win percentage
                team_performance = analysis['team_performance']
                sorted_teams = sorted(team_performance.items(), 
                                    key=lambda x: x[1]['win_percentage'] if x[1]['games'] > 0 else 0, 
                                    reverse=True)
                
                for team, stats in sorted_teams:
                    if stats['games'] > 0:
                        f.write(f"| {team} | {stats['games']} | {stats['wins']} | {stats['win_percentage']:5.1%} | {stats['avg_points_scored']:8.1f} | {stats['avg_points_allowed']:11.1f} | {stats['avg_point_differential']:+5.1f} |\n")
                
                f.write("\n")
                
                # Game-by-Game Analysis
                f.write("## 🎮 Game-by-Game Analysis\n\n")
                f.write("| Home | Away | Predicted | Actual | Correct | Points | Total Error | Margin |\n")
                f.write("|------|------|-----------|--------|---------|--------|-------------|--------|\n")
                
                for game in analysis['games_analyzed']:
                    correct = "✅" if game['prediction']['pick_team'] == game['actual']['winner'] else "❌"
                    total_error = ""
                    if game['prediction']['total_points'] and game['actual']['total_points']:
                        error = abs(game['prediction']['total_points'] - game['actual']['total_points'])
                        total_error = f"{error:.1f}"
                    
                    margin = abs(game['actual']['home_score'] - game['actual']['away_score'])
                    f.write(f"| {game['teams']['home']} | {game['teams']['away']} | {game['prediction']['pick_team']} | {game['actual']['winner']} | {correct} | {int(game['prediction']['confidence_points']):2d} | {total_error:11s} | {margin:6.0f} |\n")
                
                f.write("\n")
                
                # Key Insights
                f.write("## 🔍 Key Insights\n\n")
                
                # Overall performance insight
                if analysis['overall_accuracy'] > 0.7:
                    f.write("- ✅ **Excellent Performance:** Above 70% accuracy indicates strong model performance\n")
                elif analysis['overall_accuracy'] > 0.6:
                    f.write("- ✅ **Good Performance:** Above 60% accuracy shows solid predictive capability\n")
                elif analysis['overall_accuracy'] > 0.5:
                    f.write("- ⚠️ **Average Performance:** Around 50% accuracy suggests room for improvement\n")
                else:
                    f.write("- ❌ **Poor Performance:** Below 50% accuracy indicates model needs significant adjustment\n")
                
                # Confidence level insights
                high_conf_accuracy = []
                low_conf_accuracy = []
                for conf_points, data in analysis['confidence_accuracy'].items():
                    if int(conf_points) >= 10 and data['total'] > 0:
                        high_conf_accuracy.append(data['accuracy'])
                    elif int(conf_points) <= 5 and data['total'] > 0:
                        low_conf_accuracy.append(data['accuracy'])
                
                if high_conf_accuracy and low_conf_accuracy:
                    avg_high = sum(high_conf_accuracy) / len(high_conf_accuracy)
                    avg_low = sum(low_conf_accuracy) / len(low_conf_accuracy)
                    
                    if avg_high > avg_low + 0.1:
                        f.write("- 🎯 **Confidence Calibration:** Higher confidence picks performed better, indicating good calibration\n")
                    elif avg_low > avg_high + 0.1:
                        f.write("- ⚠️ **Confidence Calibration:** Lower confidence picks performed better, suggesting overconfidence\n")
                    else:
                        f.write("- 📊 **Confidence Calibration:** Similar performance across confidence levels\n")
                
                # Game dominance insights
                if dom['close_games'] / dom['total_games'] > 0.6:
                    f.write("- 🏈 **Close Games:** High percentage of close games indicates competitive parity\n")
                if dom['blowouts'] / dom['total_games'] > 0.3:
                    f.write("- 💥 **Blowouts:** Significant number of blowouts suggests some teams are clearly superior\n")
                
                # Total points accuracy
                avg_error = analysis['total_points_accuracy']['avg_error']
                if avg_error < 5:
                    f.write("- 🎯 **Total Points:** Very accurate total points predictions\n")
                elif avg_error < 10:
                    f.write("- ✅ **Total Points:** Good total points prediction accuracy\n")
                else:
                    f.write("- ⚠️ **Total Points:** Total points predictions need improvement\n")
                
                f.write("\n")
                
                # Recommendations for next week
                f.write("## 🚀 Recommendations for Next Week\n\n")
                
                # Confidence adjustments
                adjustments = self.analyzer.get_confidence_adjustments(week + 1)
                if adjustments:
                    f.write("### Confidence Adjustments\n\n")
                    f.write("Based on historical performance, consider these adjustments:\n\n")
                    f.write("| Confidence Points | Adjustment Factor | Recommendation |\n")
                    f.write("|-------------------|------------------|----------------|\n")
                    
                    for conf_points, factor in sorted(adjustments.items(), key=lambda x: int(x[0])):
                        if factor > 1.2:
                            recommendation = "Increase confidence"
                        elif factor < 0.8:
                            recommendation = "Decrease confidence"
                        else:
                            recommendation = "Maintain current level"
                        
                        f.write(f"| {int(conf_points):2d} | {factor:5.2f}x | {recommendation} |\n")
                    
                    f.write("\n")
                
                # Team performance recommendations
                f.write("### Team Performance Notes\n\n")
                f.write("Consider these team performance trends:\n\n")
                
                # Top performers
                top_teams = [team for team, stats in sorted_teams[:5] if stats['games'] > 0 and stats['win_percentage'] > 0.5]
                if top_teams:
                    f.write(f"- **Strong Performers:** {', '.join(top_teams)} showed strong Week {week} performance\n")
                
                # Bottom performers
                bottom_teams = [team for team, stats in sorted_teams[-5:] if stats['games'] > 0 and stats['win_percentage'] < 0.5]
                if bottom_teams:
                    f.write(f"- **Struggling Teams:** {', '.join(bottom_teams)} had difficult Week {week} games\n")
                
                f.write("\n")
            
            print(f"✅ Exported analysis report to {md_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting to Markdown: {e}")
            return False

def main():
    """Export Week 1 analysis results"""
    exporter = AnalysisExporter()
    
    # Export Week 1 analysis
    success = exporter.export_week_analysis(2025, 1)
    
    if success:
        print("\n🎉 Week 1 analysis exported successfully!")
        print("📁 Files created:")
        print("   - data/outputs/2025/week1-analysis-summary.csv")
        print("   - data/outputs/2025/week1-confidence-accuracy.csv") 
        print("   - data/outputs/2025/week1-team-performance.csv")
        print("   - data/outputs/2025/week1-game-analysis.csv")
        print("   - data/outputs/2025/week1-analysis-report.md")
    else:
        print("❌ Export failed")

if __name__ == "__main__":
    main()
