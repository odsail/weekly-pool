#!/usr/bin/env python3
"""
Generate Week 4 picks using our improved models and insights from pool data.
This will incorporate lessons learned from the successful pool performers.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
from team_name_mapper import TeamNameMapper
from datetime import datetime
import requests
import json

def generate_week4_picks():
    """Generate Week 4 picks using multiple approaches"""
    
    print("🏈 Week 4 Picks Generation")
    print("=" * 50)
    
    # Initialize components
    db_manager = DatabaseManager(version="v2")
    team_mapper = TeamNameMapper()
    
    # Get Week 4 games
    week4_games = get_week4_games(db_manager)
    if not week4_games:
        print("❌ No Week 4 games found in database")
        return
    
    print(f"📅 Found {len(week4_games)} Week 4 games")
    
    # Get current odds for Week 4
    print("\n📊 Fetching current odds...")
    odds_data = fetch_week4_odds()
    
    # Generate picks using different approaches
    print("\n🎯 Generating picks using multiple approaches...")
    
    # Approach 1: Pool Winner Strategy (based on successful patterns)
    pool_winner_picks = generate_pool_winner_strategy(week4_games, odds_data, db_manager)
    
    # Approach 2: Your Strategy (based on your successful patterns)
    your_strategy_picks = generate_your_strategy(week4_games, odds_data, db_manager)
    
    # Approach 3: Expert Consensus Enhanced
    expert_enhanced_picks = generate_expert_enhanced_picks(week4_games, odds_data, db_manager)
    
    # Create output files
    create_week4_output_files(pool_winner_picks, your_strategy_picks, expert_enhanced_picks)
    
    print("\n✅ Week 4 picks generated successfully!")
    print("📁 Check data/outputs/2025/ for the results")

def get_week4_games(db_manager):
    """Get Week 4 games from database"""
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.id, g.season_year, g.week, g.home_team_id, g.away_team_id,
                   ht.name as home_team, at.name as away_team, g.game_date
            FROM games g
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            WHERE g.season_year = 2025 AND g.week = 4
            ORDER BY g.game_date
        """)
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def fetch_week4_odds():
    """Fetch current odds for Week 4 games"""
    
    # This would normally fetch from The Odds API
    # For now, return mock data structure
    return {
        "games": [
            {"home": "Team A", "away": "Team B", "home_ml": -150, "away_ml": 130, "total": 45.5},
            # Add more games as needed
        ]
    }

def generate_pool_winner_strategy(games, odds_data, db_manager):
    """Generate picks based on successful pool winner patterns"""
    
    print("  🏆 Pool Winner Strategy...")
    
    # Analyze successful patterns from pool data
    successful_patterns = analyze_successful_patterns(db_manager)
    
    picks = []
    confidence_points = list(range(16, 0, -1))  # 16 to 1
    
    for i, game in enumerate(games):
        # Use successful patterns to determine pick
        pick_team = determine_pick_from_patterns(game, successful_patterns)
        confidence = confidence_points[i] if i < len(confidence_points) else 1
        
        picks.append({
            "game": f"{game['away_team']} @ {game['home_team']}",
            "pick": pick_team,
            "confidence": confidence,
            "method": "pool_winner_patterns"
        })
    
    return picks

def generate_your_strategy(games, odds_data, db_manager):
    """Generate picks based on your successful strategy patterns"""
    
    print("  🎯 Your Strategy (FundaySunday patterns)...")
    
    # Analyze your successful patterns
    your_patterns = analyze_your_successful_patterns(db_manager)
    
    picks = []
    confidence_points = list(range(16, 0, -1))  # 16 to 1
    
    for i, game in enumerate(games):
        # Use your successful patterns
        pick_team = determine_pick_from_your_patterns(game, your_patterns)
        confidence = confidence_points[i] if i < len(confidence_points) else 1
        
        picks.append({
            "game": f"{game['away_team']} @ {game['home_team']}",
            "pick": pick_team,
            "confidence": confidence,
            "method": "your_successful_patterns"
        })
    
    return picks

def generate_expert_enhanced_picks(games, odds_data, db_manager):
    """Generate picks using expert consensus enhanced approach"""
    
    print("  🧠 Expert Enhanced Strategy...")
    
    picks = []
    confidence_points = list(range(16, 0, -1))  # 16 to 1
    
    for i, game in enumerate(games):
        # Use expert consensus + odds + historical patterns
        pick_team = determine_expert_enhanced_pick(game, odds_data, db_manager)
        confidence = confidence_points[i] if i < len(confidence_points) else 1
        
        picks.append({
            "game": f"{game['away_team']} @ {game['home_team']}",
            "pick": pick_team,
            "confidence": confidence,
            "method": "expert_enhanced"
        })
    
    return picks

def analyze_successful_patterns(db_manager):
    """Analyze patterns from successful pool performers"""
    
    # Get top performers' patterns
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pr.pick_team_id, t.name as pick_team, 
                   COUNT(*) as pick_count,
                   AVG(pr.confidence_points) as avg_confidence,
                   SUM(CASE WHEN pr.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
                   COUNT(*) as total_picks
            FROM pool_results pr
            JOIN teams t ON pr.pick_team_id = t.id
            WHERE pr.season_year = 2025 AND pr.week IN (1, 2, 3)
            AND pr.participant_name IN ('Raiderjim', 'Spanish Flies', 'Big Chuck', 'Commish', 'I.P. Daly')
            GROUP BY pr.pick_team_id, t.name
            HAVING correct_picks * 1.0 / total_picks >= 0.8
            ORDER BY correct_picks * 1.0 / total_picks DESC, pick_count DESC
        """)
        
        results = cursor.fetchall()
        
        patterns = {}
        for pick_team_id, pick_team, pick_count, avg_confidence, correct_picks, total_picks in results:
            accuracy = correct_picks / total_picks
            patterns[pick_team] = {
                "accuracy": accuracy,
                "pick_count": pick_count,
                "avg_confidence": avg_confidence
            }
        
        return patterns

def analyze_your_successful_patterns(db_manager):
    """Analyze your successful patterns"""
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pr.pick_team_id, t.name as pick_team, 
                   COUNT(*) as pick_count,
                   AVG(pr.confidence_points) as avg_confidence,
                   SUM(CASE WHEN pr.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
                   COUNT(*) as total_picks
            FROM pool_results pr
            JOIN teams t ON pr.pick_team_id = t.id
            WHERE pr.season_year = 2025 AND pr.week IN (1, 2, 3)
            AND pr.participant_name = 'FundaySunday'
            GROUP BY pr.pick_team_id, t.name
            ORDER BY correct_picks * 1.0 / total_picks DESC, pick_count DESC
        """)
        
        results = cursor.fetchall()
        
        patterns = {}
        for pick_team_id, pick_team, pick_count, avg_confidence, correct_picks, total_picks in results:
            accuracy = correct_picks / total_picks
            patterns[pick_team] = {
                "accuracy": accuracy,
                "pick_count": pick_count,
                "avg_confidence": avg_confidence
            }
        
        return patterns

def determine_pick_from_patterns(game, patterns):
    """Determine pick based on successful patterns"""
    
    home_team = game['home_team']
    away_team = game['away_team']
    
    # Check if either team has successful patterns
    home_accuracy = patterns.get(home_team, {}).get('accuracy', 0.5)
    away_accuracy = patterns.get(away_team, {}).get('accuracy', 0.5)
    
    # Pick the team with higher success rate
    if home_accuracy > away_accuracy:
        return home_team
    elif away_accuracy > home_accuracy:
        return away_team
    else:
        # Default to home team if equal
        return home_team

def determine_pick_from_your_patterns(game, patterns):
    """Determine pick based on your successful patterns"""
    
    home_team = game['home_team']
    away_team = game['away_team']
    
    # Check your success with each team
    home_accuracy = patterns.get(home_team, {}).get('accuracy', 0.5)
    away_accuracy = patterns.get(away_team, {}).get('accuracy', 0.5)
    
    # Pick the team you've had more success with
    if home_accuracy > away_accuracy:
        return home_team
    elif away_accuracy > home_accuracy:
        return away_team
    else:
        # Default to home team if equal
        return home_team

def determine_expert_enhanced_pick(game, odds_data, db_manager):
    """Determine pick using expert consensus enhanced approach"""
    
    # This would incorporate:
    # 1. Expert consensus from CBS Sports
    # 2. Current odds analysis
    # 3. Historical performance patterns
    # 4. Team form and matchups
    
    # For now, default to home team
    return game['home_team']

def create_week4_output_files(pool_winner_picks, your_strategy_picks, expert_enhanced_picks):
    """Create output files for Week 4 picks"""
    
    # Create output directory
    os.makedirs("data/outputs/2025", exist_ok=True)
    
    # Create markdown files for each approach
    create_week4_markdown("pool-winner-strategy", pool_winner_picks)
    create_week4_markdown("your-strategy", your_strategy_picks)
    create_week4_markdown("expert-enhanced", expert_enhanced_picks)
    
    # Create comparison file
    create_week4_comparison(pool_winner_picks, your_strategy_picks, expert_enhanced_picks)

def create_week4_markdown(strategy_name, picks):
    """Create markdown file for a specific strategy"""
    
    filename = f"data/outputs/2025/week-week4-{strategy_name}.md"
    
    with open(filename, "w") as f:
        f.write(f"# Week 4 Picks - {strategy_name.replace('-', ' ').title()}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Picks\n\n")
        f.write("| Points | Pick | Game | Method |\n")
        f.write("|--------|------|------|--------|\n")
        
        for pick in picks:
            f.write(f"| {pick['confidence']} | {pick['pick']} | {pick['game']} | {pick['method']} |\n")
        
        f.write(f"\n## Summary\n")
        f.write(f"- **Total Games**: {len(picks)}\n")
        f.write(f"- **Total Confidence Points**: {sum(p['confidence'] for p in picks)}\n")
        f.write(f"- **Method**: {strategy_name.replace('-', ' ').title()}\n")
        f.write(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def create_week4_comparison(pool_winner_picks, your_strategy_picks, expert_enhanced_picks):
    """Create comparison file for all strategies"""
    
    filename = "data/outputs/2025/week-week4-comparison.md"
    
    with open(filename, "w") as f:
        f.write("# Week 4 Picks - Strategy Comparison\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Strategy Comparison\n\n")
        f.write("| Game | Pool Winner | Your Strategy | Expert Enhanced | Agreement |\n")
        f.write("|------|-------------|---------------|-----------------|----------|\n")
        
        for i in range(len(pool_winner_picks)):
            game = pool_winner_picks[i]['game']
            pool_pick = pool_winner_picks[i]['pick']
            your_pick = your_strategy_picks[i]['pick']
            expert_pick = expert_enhanced_picks[i]['pick']
            
            # Check agreement
            if pool_pick == your_pick == expert_pick:
                agreement = "🎯 All"
            elif pool_pick == your_pick:
                agreement = "🏆 Pool+You"
            elif pool_pick == expert_pick:
                agreement = "🏆 Pool+Expert"
            elif your_pick == expert_pick:
                agreement = "🎯 You+Expert"
            else:
                agreement = "⚔️ None"
            
            f.write(f"| {game} | {pool_pick} | {your_pick} | {expert_pick} | {agreement} |\n")
        
        f.write(f"\n## Summary\n")
        f.write(f"- **Total Games**: {len(pool_winner_picks)}\n")
        f.write(f"- **All Agree**: {sum(1 for i in range(len(pool_winner_picks)) if pool_winner_picks[i]['pick'] == your_strategy_picks[i]['pick'] == expert_enhanced_picks[i]['pick'])}\n")
        f.write(f"- **Pool+You Agree**: {sum(1 for i in range(len(pool_winner_picks)) if pool_winner_picks[i]['pick'] == your_strategy_picks[i]['pick'])}\n")
        f.write(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    generate_week4_picks()

