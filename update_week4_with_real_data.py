#!/usr/bin/env python3
"""
Update Week 4 model with real performance data from Excel files.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
from datetime import datetime

def update_week4_with_real_data():
    """Update Week 4 model with real performance data"""
    
    print("🔄 Updating Week 4 Model with Real Performance Data")
    print("=" * 60)
    
    db_manager = DatabaseManager(version="v2")
    
    # Analyze FundaySunday's actual performance
    performance_analysis = analyze_fundaysunday_performance(db_manager)
    
    # Generate updated Week 4 picks
    updated_picks = generate_updated_week4_picks(performance_analysis)
    
    # Create updated documentation
    create_updated_week4_files(updated_picks, performance_analysis)
    
    print("\n✅ Week 4 model updated with real performance data!")

def analyze_fundaysunday_performance(db_manager):
    """Analyze FundaySunday's actual performance from the database"""
    
    print("\n📊 Analyzing FundaySunday's Real Performance...")
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pr.week, pr.confidence_points, pr.is_correct, t.name as pick_team,
                   ht.name as home_team, at.name as away_team
            FROM pool_results pr
            JOIN teams t ON pr.pick_team_id = t.id
            JOIN games g ON pr.game_id = g.id
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            WHERE pr.season_year = 2025 AND pr.participant_name = 'FundaySunday'
            ORDER BY pr.week, pr.confidence_points DESC
        """)
        
        results = cursor.fetchall()
        
        # Analyze performance
        weekly_performance = {}
        team_performance = {}
        confidence_performance = {}
        
        for week, confidence, is_correct, pick_team, home_team, away_team in results:
            # Weekly performance
            if week not in weekly_performance:
                weekly_performance[week] = {'correct': 0, 'total': 0, 'points': 0}
            weekly_performance[week]['total'] += 1
            if is_correct:
                weekly_performance[week]['correct'] += 1
                weekly_performance[week]['points'] += confidence
            
            # Team performance
            if pick_team not in team_performance:
                team_performance[pick_team] = {'correct': 0, 'total': 0}
            team_performance[pick_team]['total'] += 1
            if is_correct:
                team_performance[pick_team]['correct'] += 1
            
            # Confidence performance
            if confidence not in confidence_performance:
                confidence_performance[confidence] = {'correct': 0, 'total': 0}
            confidence_performance[confidence]['total'] += 1
            if is_correct:
                confidence_performance[confidence]['correct'] += 1
        
        # Calculate accuracy rates
        for week in weekly_performance:
            week_data = weekly_performance[week]
            week_data['accuracy'] = week_data['correct'] / week_data['total']
        
        for team in team_performance:
            team_data = team_performance[team]
            team_data['accuracy'] = team_data['correct'] / team_data['total']
        
        for conf in confidence_performance:
            conf_data = confidence_performance[conf]
            conf_data['accuracy'] = conf_data['correct'] / conf_data['total']
        
        # Calculate overall performance
        total_correct = sum(1 for _, _, is_correct, _, _, _ in results if is_correct)
        total_picks = len(results)
        overall_accuracy = total_correct / total_picks if total_picks > 0 else 0
        
        return {
            'weekly_performance': weekly_performance,
            'team_performance': team_performance,
            'confidence_performance': confidence_performance,
            'overall_accuracy': overall_accuracy,
            'total_correct': total_correct,
            'total_picks': total_picks
        }

def generate_updated_week4_picks(performance_analysis):
    """Generate updated Week 4 picks based on real performance"""
    
    print("\n🎯 Generating Updated Week 4 Picks...")
    
    # Week 4 games
    week4_games = [
        {"home": "Arizona Cardinals", "away": "Seattle Seahawks"},
        {"home": "Pittsburgh Steelers", "away": "Minnesota Vikings"},
        {"home": "Atlanta Falcons", "away": "Washington Commanders"},
        {"home": "Buffalo Bills", "away": "New Orleans Saints"},
        {"home": "Detroit Lions", "away": "Cleveland Browns"},
        {"home": "New England Patriots", "away": "Carolina Panthers"},
        {"home": "New York Giants", "away": "Los Angeles Chargers"},
        {"home": "Tampa Bay Buccaneers", "away": "Philadelphia Eagles"},
        {"home": "Houston Texans", "away": "Tennessee Titans"},
        {"home": "Los Angeles Rams", "away": "Indianapolis Colts"},
        {"home": "San Francisco 49ers", "away": "Jacksonville Jaguars"},
        {"home": "Kansas City Chiefs", "away": "Baltimore Ravens"},
        {"home": "Las Vegas Raiders", "away": "Chicago Bears"},
        {"home": "Dallas Cowboys", "away": "Green Bay Packers"},
        {"home": "Miami Dolphins", "away": "New York Jets"},
        {"home": "Denver Broncos", "away": "Cincinnati Bengals"}
    ]
    
    picks = []
    
    for game in week4_games:
        # Determine pick based on real performance
        pick_team = determine_pick_from_real_performance(game, performance_analysis)
        
        # Determine confidence based on real performance
        confidence = determine_confidence_from_real_performance(pick_team, performance_analysis)
        
        picks.append({
            "game": f"{game['away']} @ {game['home']}",
            "pick": pick_team,
            "confidence": confidence,
            "home_team": game['home'],
            "away_team": game['away']
        })
    
    # Sort by confidence (highest first)
    picks.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Reassign confidence points 16-1
    for i, pick in enumerate(picks):
        pick['confidence'] = 16 - i
    
    return picks

def determine_pick_from_real_performance(game, performance_analysis):
    """Determine pick based on real performance data"""
    
    home_team = game['home']
    away_team = game['away']
    
    # Check real success rate with each team
    home_accuracy = performance_analysis['team_performance'].get(home_team, {}).get('accuracy', 0.5)
    away_accuracy = performance_analysis['team_performance'].get(away_team, {}).get('accuracy', 0.5)
    
    # Special consideration for Vikings with Carson Wentz
    if away_team == "Minnesota Vikings" and home_team == "Pittsburgh Steelers":
        print(f"  🎯 Special consideration: Vikings with Carson Wentz")
        # Give edge to Vikings due to Wentz factor
        away_accuracy += 0.15
    
    # Pick the team with better real performance
    if home_accuracy > away_accuracy:
        return home_team
    elif away_accuracy > home_accuracy:
        return away_team
    else:
        # Default to home team if equal
        return home_team

def determine_confidence_from_real_performance(pick_team, performance_analysis):
    """Determine confidence based on real performance"""
    
    team_accuracy = performance_analysis['team_performance'].get(pick_team, {}).get('accuracy', 0.5)
    
    # Convert accuracy to confidence (0.0-1.0 -> 1-16)
    confidence = int(team_accuracy * 15) + 1
    confidence = max(1, min(16, confidence))  # Clamp between 1-16
    
    return confidence

def create_updated_week4_files(picks, performance_analysis):
    """Create updated Week 4 files with real performance data"""
    
    print("\n📝 Creating Updated Week 4 Files...")
    
    # Create output directory
    os.makedirs("data/outputs/2025", exist_ok=True)
    
    # Create main updated picks file
    create_updated_picks_file(picks, performance_analysis)
    
    # Create performance analysis file
    create_performance_analysis_file(performance_analysis)

def create_updated_picks_file(picks, performance_analysis):
    """Create updated picks file with real performance data"""
    
    filename = "data/outputs/2025/week-week4-updated-with-real-data.md"
    
    with open(filename, "w") as f:
        f.write("# Week 4 Picks - Updated with Real Performance Data\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Model Documentation\n\n")
        f.write("**Model Name:** FundaySunday Real Performance Strategy\n")
        f.write("**Model Version:** 2.0 (Updated with real Excel data)\n")
        f.write("**Model Type:** Real Performance Analysis\n")
        f.write("**Training Data:** Weeks 1-3 actual pool results (Excel files)\n")
        f.write(f"**Performance:** {performance_analysis['total_correct']}/{performance_analysis['total_picks']} correct ({performance_analysis['overall_accuracy']:.1%} accuracy)\n\n")
        
        f.write("## Model Methodology\n\n")
        f.write("1. **Real Performance Analysis:** Analyzed actual success rate with each team\n")
        f.write("2. **Confidence Calibration:** Adjusted confidence points based on real performance\n")
        f.write("3. **Special Factors:** Considered Carson Wentz factor for Vikings\n")
        f.write("4. **Stack Ranking:** Assigned 16-1 confidence points based on real win probability\n\n")
        
        f.write("## Real Performance Analysis Summary\n\n")
        f.write(f"- **Overall Accuracy:** {performance_analysis['overall_accuracy']:.1%}\n")
        f.write(f"- **Total Correct Picks:** {performance_analysis['total_correct']}\n")
        f.write(f"- **Total Picks:** {performance_analysis['total_picks']}\n\n")
        
        f.write("### Weekly Performance\n")
        for week in sorted(performance_analysis['weekly_performance'].keys()):
            week_data = performance_analysis['weekly_performance'][week]
            f.write(f"- **Week {week}:** {week_data['accuracy']:.1%} ({week_data['correct']}/{week_data['total']}) - {week_data['points']} points\n")
        
        f.write("\n### Team Performance\n")
        f.write("| Team | Accuracy | Correct | Total |\n")
        f.write("|------|----------|---------|-------|\n")
        
        for team, data in sorted(performance_analysis['team_performance'].items(), 
                                key=lambda x: x[1]['accuracy'], reverse=True):
            f.write(f"| {team} | {data['accuracy']:.1%} | {data['correct']} | {data['total']} |\n")
        
        f.write("\n## Updated Week 4 Picks\n\n")
        f.write("| Points | Pick | Game | Real Performance Basis |\n")
        f.write("|--------|------|------|------------------------|\n")
        
        for pick in picks:
            team_accuracy = performance_analysis['team_performance'].get(pick['pick'], {}).get('accuracy', 0.5)
            f.write(f"| {pick['confidence']} | {pick['pick']} | {pick['game']} | {team_accuracy:.1%} real success rate |\n")
        
        f.write(f"\n## Summary\n")
        f.write(f"- **Total Games**: {len(picks)}\n")
        f.write(f"- **Total Confidence Points**: {sum(p['confidence'] for p in picks)}\n")
        f.write(f"- **Model**: FundaySunday Real Performance Strategy v2.0\n")
        f.write(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def create_performance_analysis_file(performance_analysis):
    """Create detailed performance analysis file"""
    
    filename = "data/outputs/2025/week4-real-performance-analysis.md"
    
    with open(filename, "w") as f:
        f.write("# Week 4 Real Performance Analysis\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Overview\n\n")
        f.write("This analysis is based on FundaySunday's actual performance from Weeks 1-3,\n")
        f.write("as extracted from the Excel pool results files.\n\n")
        
        f.write("## Key Findings\n\n")
        f.write(f"- **Overall Accuracy:** {performance_analysis['overall_accuracy']:.1%}\n")
        f.write(f"- **Total Correct Picks:** {performance_analysis['total_correct']}\n")
        f.write(f"- **Total Picks:** {performance_analysis['total_picks']}\n\n")
        
        f.write("## Weekly Breakdown\n\n")
        for week in sorted(performance_analysis['weekly_performance'].keys()):
            week_data = performance_analysis['weekly_performance'][week]
            f.write(f"### Week {week}\n")
            f.write(f"- **Accuracy:** {week_data['accuracy']:.1%}\n")
            f.write(f"- **Correct Picks:** {week_data['correct']}/{week_data['total']}\n")
            f.write(f"- **Points Earned:** {week_data['points']}\n\n")
        
        f.write("## Team Performance Analysis\n\n")
        f.write("### Top Performing Teams\n")
        f.write("| Team | Accuracy | Correct | Total |\n")
        f.write("|------|----------|---------|-------|\n")
        
        top_teams = sorted(performance_analysis['team_performance'].items(), 
                          key=lambda x: x[1]['accuracy'], reverse=True)[:10]
        
        for team, data in top_teams:
            f.write(f"| {team} | {data['accuracy']:.1%} | {data['correct']} | {data['total']} |\n")
        
        f.write("\n### Bottom Performing Teams\n")
        f.write("| Team | Accuracy | Correct | Total |\n")
        f.write("|------|----------|---------|-------|\n")
        
        bottom_teams = sorted(performance_analysis['team_performance'].items(), 
                             key=lambda x: x[1]['accuracy'])[:10]
        
        for team, data in bottom_teams:
            f.write(f"| {team} | {data['accuracy']:.1%} | {data['correct']} | {data['total']} |\n")

if __name__ == "__main__":
    update_week4_with_real_data()

