#!/usr/bin/env python3
"""
Week 2 Results Analysis
Compare original picks vs ML model performance
"""

import pandas as pd
import sqlite3
from datetime import datetime
import os

def analyze_week2_results():
    """Analyze Week 2 results and compare model performance"""
    
    # Connect to database
    db_path = "data/nfl_pool_v2.db"
    conn = sqlite3.connect(db_path)
    
    print("🔍 Week 2 Results Analysis")
    print("=" * 50)
    
    # Get Week 2 games with results
    query = """
    SELECT 
        g.id as game_id,
        g.week,
        g.game_date,
        ht.name as home_team,
        at.name as away_team,
        g.home_score,
        g.away_score,
        g.is_completed,
        g.is_international,
        o.home_ml,
        o.away_ml,
        o.total_points
    FROM games g
    JOIN teams ht ON g.home_team_id = ht.id
    JOIN teams at ON g.away_team_id = at.id
    LEFT JOIN odds o ON g.id = o.game_id
    WHERE g.season_year = 2025 AND g.week = 2
    ORDER BY g.game_date
    """
    
    games_df = pd.read_sql_query(query, conn)
    print(f"📊 Found {len(games_df)} Week 2 games")
    
    # Get original Week 2 picks
    original_picks_query = """
    SELECT 
        p.game_id,
        pt.name as pick_team,
        p.confidence_points as confidence,
        ht.name as home_team,
        at.name as away_team,
        g.home_score,
        g.away_score
    FROM picks p
    JOIN games g ON p.game_id = g.id
    JOIN teams ht ON g.home_team_id = ht.id
    JOIN teams at ON g.away_team_id = at.id
    JOIN teams pt ON p.pick_team_id = pt.id
    WHERE g.season_year = 2025 AND g.week = 2
    ORDER BY p.confidence_points DESC
    """
    
    original_picks_df = pd.read_sql_query(original_picks_query, conn)
    print(f"📊 Found {len(original_picks_df)} original Week 2 picks")
    
    # Get ML model picks (from hybrid model output)
    ml_picks_file = "data/outputs/2025/week2-hybrid-picks.md"
    if os.path.exists(ml_picks_file):
        with open(ml_picks_file, 'r') as f:
            ml_content = f.read()
        print(f"📊 Found ML picks file: {ml_picks_file}")
    else:
        print("⚠️  ML picks file not found")
        ml_content = ""
    
    # Analyze original picks performance
    print("\n🎯 Original Picks Analysis")
    print("-" * 30)
    
    original_correct = 0
    original_total = 0
    original_analysis = []
    
    for _, pick in original_picks_df.iterrows():
        if pick['home_score'] is not None and pick['away_score'] is not None:
            # Determine actual winner
            if pick['home_score'] > pick['away_score']:
                actual_winner = pick['home_team']
            elif pick['away_score'] > pick['home_score']:
                actual_winner = pick['away_team']
            else:
                actual_winner = "TIE"
            
            # Check if pick was correct
            is_correct = (pick['pick_team'] == actual_winner)
            if is_correct:
                original_correct += 1
            original_total += 1
            
            original_analysis.append({
                'game': f"{pick['away_team']} @ {pick['home_team']}",
                'pick': pick['pick_team'],
                'confidence': pick['confidence'],
                'actual_winner': actual_winner,
                'correct': is_correct,
                'score': f"{pick['away_score']}-{pick['home_score']}"
            })
    
    original_accuracy = (original_correct / original_total * 100) if original_total > 0 else 0
    print(f"✅ Original Picks: {original_correct}/{original_total} ({original_accuracy:.1f}%)")
    
    # Analyze ML model performance (if available)
    print("\n🤖 ML Model Analysis")
    print("-" * 30)
    
    # Parse ML picks from markdown file
    ml_analysis = []
    if ml_content:
        lines = ml_content.split('\n')
        for line in lines:
            if '|' in line and not line.startswith('|') and 'Points' not in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 6:
                    try:
                        points = int(parts[1])
                        pick = parts[2]
                        win_pct = float(parts[3].replace('%', ''))
                        home_team = parts[4]
                        away_team = parts[6]
                        
                        # Find corresponding game in database
                        game_match = games_df[
                            (games_df['home_team'] == home_team) & 
                            (games_df['away_team'] == away_team)
                        ]
                        
                        if not game_match.empty:
                            game = game_match.iloc[0]
                            if game['home_score'] is not None and game['away_score'] is not None:
                                # Determine actual winner
                                if game['home_score'] > game['away_score']:
                                    actual_winner = game['home_team']
                                elif game['away_score'] > game['home_score']:
                                    actual_winner = game['away_team']
                                else:
                                    actual_winner = "TIE"
                                
                                # Check if pick was correct
                                is_correct = (pick == actual_winner)
                                
                                ml_analysis.append({
                                    'game': f"{away_team} @ {home_team}",
                                    'pick': pick,
                                    'confidence': points,
                                    'win_pct': win_pct,
                                    'actual_winner': actual_winner,
                                    'correct': is_correct,
                                    'score': f"{game['away_score']}-{game['home_score']}"
                                })
                    except (ValueError, IndexError):
                        continue
    
    ml_correct = sum(1 for a in ml_analysis if a['correct'])
    ml_total = len(ml_analysis)
    ml_accuracy = (ml_correct / ml_total * 100) if ml_total > 0 else 0
    print(f"✅ ML Model: {ml_correct}/{ml_total} ({ml_accuracy:.1f}%)")
    
    # Create detailed comparison
    print("\n📊 Detailed Game-by-Game Analysis")
    print("-" * 50)
    
    comparison_data = []
    for orig in original_analysis:
        # Find corresponding ML pick
        ml_match = next((ml for ml in ml_analysis if ml['game'] == orig['game']), None)
        
        comparison_data.append({
            'game': orig['game'],
            'original_pick': orig['pick'],
            'original_conf': orig['confidence'],
            'ml_pick': ml_match['pick'] if ml_match else 'N/A',
            'ml_conf': ml_match['confidence'] if ml_match else 'N/A',
            'actual_winner': orig['actual_winner'],
            'original_correct': orig['correct'],
            'ml_correct': ml_match['correct'] if ml_match else False,
            'pick_agreement': orig['pick'] == ml_match['pick'] if ml_match else False,
            'score': orig['score']
        })
    
    # Display results
    for game in comparison_data:
        orig_status = "✅" if game['original_correct'] else "❌"
        ml_status = "✅" if game['ml_correct'] else "❌"
        agreement = "🤝" if game['pick_agreement'] else "⚔️"
        
        print(f"{game['game']}")
        print(f"  Original: {game['original_pick']} (Conf: {game['original_conf']}) {orig_status}")
        print(f"  ML Model: {game['ml_pick']} (Conf: {game['ml_conf']}) {ml_status}")
        print(f"  Actual: {game['actual_winner']} {game['score']} {agreement}")
        print()
    
    # Summary statistics
    print("\n📈 Summary Statistics")
    print("-" * 30)
    print(f"Original Picks Accuracy: {original_accuracy:.1f}%")
    print(f"ML Model Accuracy: {ml_accuracy:.1f}%")
    
    agreement_count = sum(1 for g in comparison_data if g['pick_agreement'])
    agreement_pct = (agreement_count / len(comparison_data) * 100) if comparison_data else 0
    print(f"Pick Agreement: {agreement_count}/{len(comparison_data)} ({agreement_pct:.1f}%)")
    
    # Save detailed analysis
    output_dir = "data/outputs/2025"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save comparison CSV
    comparison_df = pd.DataFrame(comparison_data)
    comparison_file = f"{output_dir}/week2-comparison-analysis.csv"
    comparison_df.to_csv(comparison_file, index=False)
    print(f"\n💾 Saved detailed analysis to: {comparison_file}")
    
    # Save summary report
    report_file = f"{output_dir}/week2-analysis-report.md"
    with open(report_file, 'w') as f:
        f.write("# Week 2 Results Analysis\n\n")
        f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Original Picks:** {original_correct}/{original_total} ({original_accuracy:.1f}%)\n")
        f.write(f"- **ML Model:** {ml_correct}/{ml_total} ({ml_accuracy:.1f}%)\n")
        f.write(f"- **Pick Agreement:** {agreement_count}/{len(comparison_data)} ({agreement_pct:.1f}%)\n\n")
        
        f.write("## Game-by-Game Results\n\n")
        f.write("| Game | Original Pick | ML Pick | Actual Winner | Original | ML | Agreement |\n")
        f.write("|------|---------------|---------|---------------|----------|----|----------|\n")
        
        for game in comparison_data:
            orig_status = "✅" if game['original_correct'] else "❌"
            ml_status = "✅" if game['ml_correct'] else "❌"
            agreement = "🤝" if game['pick_agreement'] else "⚔️"
            
            f.write(f"| {game['game']} | {game['original_pick']} | {game['ml_pick']} | {game['actual_winner']} | {orig_status} | {ml_status} | {agreement} |\n")
    
    print(f"💾 Saved summary report to: {report_file}")
    
    conn.close()
    
    return {
        'original_accuracy': original_accuracy,
        'ml_accuracy': ml_accuracy,
        'agreement_pct': agreement_pct,
        'total_games': len(comparison_data)
    }

if __name__ == "__main__":
    results = analyze_week2_results()
    print(f"\n🎯 Analysis Complete!")
    print(f"Original: {results['original_accuracy']:.1f}% | ML: {results['ml_accuracy']:.1f}% | Agreement: {results['agreement_pct']:.1f}%")
