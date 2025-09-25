#!/usr/bin/env python3
"""
Week 4 Analysis Framework
Track and analyze Week 4 picks performance across different strategies.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
from datetime import datetime
import json

def setup_week4_analysis():
    """Set up Week 4 analysis framework"""
    
    print("📊 Week 4 Analysis Framework Setup")
    print("=" * 50)
    
    db_manager = DatabaseManager(version="v2")
    
    # Create Week 4 picks in database
    create_week4_picks_in_database(db_manager)
    
    # Create analysis tracking
    create_week4_analysis_tracking(db_manager)
    
    # Generate analysis reports
    generate_week4_analysis_reports(db_manager)
    
    print("\n✅ Week 4 analysis framework ready!")
    print("📁 Check data/outputs/2025/ for analysis reports")

def create_week4_picks_in_database(db_manager):
    """Create Week 4 picks records in database"""
    
    print("\n📝 Creating Week 4 picks in database...")
    
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
    
    # Strategies to track
    strategies = [
        {"name": "Pool Winner Strategy", "file": "week-week4-pool-winner-strategy.md"},
        {"name": "Your Strategy", "file": "week-week4-your-strategy.md"},
        {"name": "Expert Enhanced", "file": "week-week4-expert-enhanced.md"}
    ]
    
    for strategy in strategies:
        print(f"  📊 Processing {strategy['name']}...")
        
        # Read picks from markdown file
        picks = read_picks_from_markdown(f"data/outputs/2025/{strategy['file']}")
        
        # Store in database
        for pick in picks:
            game_id = db_manager.get_game_id(2025, 4, pick['home_team'], pick['away_team'])
            pick_team_id = db_manager.get_team_id(pick['pick_team'])
            
            if game_id and pick_team_id:
                db_manager.insert_pick(
                    game_id=game_id,
                    season_year=2025,
                    week=4,
                    pick_team=pick['pick_team'],
                    confidence_points=pick['confidence'],
                    win_probability=0.8,  # Default for now
                    total_points_prediction=None
                )
        
        print(f"    ✅ Stored {len(picks)} picks for {strategy['name']}")

def read_picks_from_markdown(filename):
    """Read picks from markdown file"""
    
    picks = []
    
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        # Find the picks table
        in_table = False
        for line in lines:
            line = line.strip()
            
            if line.startswith('| Points | Pick | Game |'):
                in_table = True
                continue
            
            if in_table and line.startswith('|') and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4:
                    confidence = int(parts[1])
                    pick_team = parts[2]
                    game = parts[3]
                    
                    # Parse game to get home/away teams
                    if ' @ ' in game:
                        away_team, home_team = game.split(' @ ')
                        picks.append({
                            'confidence': confidence,
                            'pick_team': pick_team,
                            'home_team': home_team,
                            'away_team': away_team,
                            'game': game
                        })
            
            if in_table and line.startswith('##'):
                break
    
    except FileNotFoundError:
        print(f"    ⚠️  File not found: {filename}")
    
    return picks

def create_week4_analysis_tracking(db_manager):
    """Create Week 4 analysis tracking records"""
    
    print("\n📈 Creating Week 4 analysis tracking...")
    
    # Create analysis record for Week 4
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO analysis_results 
            (season_year, week, overall_accuracy, correct_picks, total_picks, 
             avg_total_points_error, blowouts_count, close_games_count, avg_margin, analysis_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (2025, 4, 0.0, 0, 16, 0.0, 0, 0, 0.0, datetime.now().isoformat()))
        
        analysis_id = cursor.lastrowid
        print(f"    ✅ Created analysis record (ID: {analysis_id})")

def generate_week4_analysis_reports(db_manager):
    """Generate Week 4 analysis reports"""
    
    print("\n📊 Generating Week 4 analysis reports...")
    
    # Create output directory
    os.makedirs("data/outputs/2025", exist_ok=True)
    
    # Generate strategy comparison report
    generate_strategy_comparison_report()
    
    # Generate confidence analysis report
    generate_confidence_analysis_report()
    
    # Generate team performance report
    generate_team_performance_report()

def generate_strategy_comparison_report():
    """Generate strategy comparison report"""
    
    filename = "data/outputs/2025/week4-strategy-comparison.md"
    
    with open(filename, "w") as f:
        f.write("# Week 4 Strategy Comparison Analysis\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Strategy Overview\n\n")
        f.write("| Strategy | Description | Key Features |\n")
        f.write("|----------|-------------|-------------|\n")
        f.write("| Pool Winner | Based on successful pool performers | High accuracy teams, proven patterns |\n")
        f.write("| Your Strategy | Based on FundaySunday patterns | Your successful pick patterns |\n")
        f.write("| Expert Enhanced | Expert consensus + odds + ML | Multi-factor approach |\n")
        
        f.write("\n## Key Insights\n\n")
        f.write("1. **High Agreement**: 14/16 games have unanimous picks across all strategies\n")
        f.write("2. **Strategy Alignment**: Pool Winner and Your Strategy agree on all 16 games\n")
        f.write("3. **Expert Divergence**: Expert Enhanced differs on 2 games (PHI @ TB, GB @ DAL)\n")
        
        f.write("\n## Recommendations\n\n")
        f.write("1. **Primary Strategy**: Use Pool Winner + Your Strategy (100% agreement)\n")
        f.write("2. **Confidence Points**: Distribute 16-1 based on win probability\n")
        f.write("3. **Risk Management**: Monitor the 2 games where strategies differ\n")

def generate_confidence_analysis_report():
    """Generate confidence analysis report"""
    
    filename = "data/outputs/2025/week4-confidence-analysis.md"
    
    with open(filename, "w") as f:
        f.write("# Week 4 Confidence Analysis\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Confidence Distribution\n\n")
        f.write("| Confidence | Games | Strategy |\n")
        f.write("|------------|-------|----------|\n")
        f.write("| 16 pts | Arizona Cardinals | Highest confidence pick |\n")
        f.write("| 15 pts | Pittsburgh Steelers | Strong home team |\n")
        f.write("| 14 pts | Atlanta Falcons | Favorable matchup |\n")
        f.write("| 13 pts | Buffalo Bills | Consistent performer |\n")
        f.write("| 12 pts | Detroit Lions | Home field advantage |\n")
        f.write("| 11 pts | New England Patriots | Veteran team |\n")
        f.write("| 10 pts | New York Giants | Upset potential |\n")
        f.write("| 9 pts | Philadelphia Eagles | Road game |\n")
        f.write("| 8 pts | Houston Texans | Close matchup |\n")
        f.write("| 7 pts | Los Angeles Rams | Neutral game |\n")
        f.write("| 6 pts | San Francisco 49ers | Strong team |\n")
        f.write("| 5 pts | Kansas City Chiefs | Elite team |\n")
        f.write("| 4 pts | Las Vegas Raiders | Home advantage |\n")
        f.write("| 3 pts | Green Bay Packers | Road challenge |\n")
        f.write("| 2 pts | Miami Dolphins | Close game |\n")
        f.write("| 1 pt | Denver Broncos | Lowest confidence |\n")
        
        f.write("\n## Risk Management\n\n")
        f.write("1. **High Confidence (16-12 pts)**: 5 games - Strong favorites\n")
        f.write("2. **Medium Confidence (11-7 pts)**: 5 games - Solid picks\n")
        f.write("3. **Low Confidence (6-1 pts)**: 6 games - Risk management\n")

def generate_team_performance_report():
    """Generate team performance report"""
    
    filename = "data/outputs/2025/week4-team-performance.md"
    
    with open(filename, "w") as f:
        f.write("# Week 4 Team Performance Analysis\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Team Pick Frequency\n\n")
        f.write("| Team | Picks | Confidence Range | Strategy |\n")
        f.write("|------|-------|------------------|----------|\n")
        f.write("| Arizona Cardinals | 3/3 | 16 pts | All strategies |\n")
        f.write("| Pittsburgh Steelers | 3/3 | 15 pts | All strategies |\n")
        f.write("| Atlanta Falcons | 3/3 | 14 pts | All strategies |\n")
        f.write("| Buffalo Bills | 3/3 | 13 pts | All strategies |\n")
        f.write("| Detroit Lions | 3/3 | 12 pts | All strategies |\n")
        f.write("| New England Patriots | 3/3 | 11 pts | All strategies |\n")
        f.write("| New York Giants | 3/3 | 10 pts | All strategies |\n")
        f.write("| Philadelphia Eagles | 2/3 | 9 pts | Pool+Your |\n")
        f.write("| Tampa Bay Buccaneers | 1/3 | 9 pts | Expert only |\n")
        f.write("| Houston Texans | 3/3 | 8 pts | All strategies |\n")
        f.write("| Los Angeles Rams | 3/3 | 7 pts | All strategies |\n")
        f.write("| San Francisco 49ers | 3/3 | 6 pts | All strategies |\n")
        f.write("| Kansas City Chiefs | 3/3 | 5 pts | All strategies |\n")
        f.write("| Las Vegas Raiders | 3/3 | 4 pts | All strategies |\n")
        f.write("| Green Bay Packers | 2/3 | 3 pts | Pool+Your |\n")
        f.write("| Dallas Cowboys | 1/3 | 3 pts | Expert only |\n")
        f.write("| Miami Dolphins | 3/3 | 2 pts | All strategies |\n")
        f.write("| Denver Broncos | 3/3 | 1 pt | All strategies |\n")
        
        f.write("\n## Key Observations\n\n")
        f.write("1. **Unanimous Picks**: 14 teams picked by all 3 strategies\n")
        f.write("2. **Strategy Divergence**: Only 2 games show disagreement\n")
        f.write("3. **Confidence Distribution**: Well-balanced from 16 to 1 points\n")

if __name__ == "__main__":
    setup_week4_analysis()
