#!/usr/bin/env python3
"""
Comprehensive Week 2 analysis including both Week 1 and Week 2 results
"""

import pandas as pd
import sqlite3
from datetime import datetime
import os

def comprehensive_week2_analysis():
    """Analyze both Week 1 and Week 2 results comprehensively"""
    
    # Connect to database
    db_path = "data/nfl_pool_v2.db"
    conn = sqlite3.connect(db_path)
    
    print("🔍 Comprehensive Week 2 Analysis (Including Week 1)")
    print("=" * 60)
    
    # Get both Week 1 and Week 2 results
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
        g.is_international
    FROM games g
    JOIN teams ht ON g.home_team_id = ht.id
    JOIN teams at ON g.away_team_id = at.id
    WHERE g.season_year = 2025 AND g.week IN (1, 2)
    ORDER BY g.week, g.game_date
    """
    
    games_df = pd.read_sql_query(query, conn)
    print(f"📊 Found {len(games_df)} total games (Week 1 + Week 2)")
    
    # Get all picks for both weeks
    picks_query = """
    SELECT 
        p.game_id,
        pt.name as pick_team,
        p.confidence_points as confidence,
        p.win_probability,
        ht.name as home_team,
        at.name as away_team,
        g.home_score,
        g.away_score,
        g.week
    FROM picks p
    JOIN games g ON p.game_id = g.id
    JOIN teams ht ON g.home_team_id = ht.id
    JOIN teams at ON g.away_team_id = at.id
    JOIN teams pt ON p.pick_team_id = pt.id
    WHERE g.season_year = 2025 AND g.week IN (1, 2)
    ORDER BY g.week, p.confidence_points DESC
    """
    
    picks_df = pd.read_sql_query(picks_query, conn)
    print(f"📊 Found {len(picks_df)} total picks (Week 1 + Week 2)")
    
    # Analyze by week
    week1_picks = picks_df[picks_df['week'] == 1]
    week2_picks = picks_df[picks_df['week'] == 2]
    
    print(f"\n📈 Week 1 Analysis")
    print("-" * 30)
    week1_correct = 0
    week1_total = 0
    week1_analysis = []
    
    for _, pick in week1_picks.iterrows():
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
                week1_correct += 1
            week1_total += 1
            
            week1_analysis.append({
                'week': 1,
                'game': f"{pick['away_team']} @ {pick['home_team']}",
                'pick': pick['pick_team'],
                'confidence': pick['confidence'],
                'actual_winner': actual_winner,
                'correct': is_correct,
                'score': f"{pick['away_score']}-{pick['home_score']}"
            })
    
    week1_accuracy = (week1_correct / week1_total * 100) if week1_total > 0 else 0
    print(f"✅ Week 1 Picks: {week1_correct}/{week1_total} ({week1_accuracy:.1f}%)")
    
    print(f"\n📈 Week 2 Analysis")
    print("-" * 30)
    week2_correct = 0
    week2_total = 0
    week2_analysis = []
    
    for _, pick in week2_picks.iterrows():
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
                week2_correct += 1
            week2_total += 1
            
            week2_analysis.append({
                'week': 2,
                'game': f"{pick['away_team']} @ {pick['home_team']}",
                'pick': pick['pick_team'],
                'confidence': pick['confidence'],
                'actual_winner': actual_winner,
                'correct': is_correct,
                'score': f"{pick['away_score']}-{pick['home_score']}"
            })
    
    week2_accuracy = (week2_correct / week2_total * 100) if week2_total > 0 else 0
    print(f"✅ Week 2 Picks: {week2_correct}/{week2_total} ({week2_accuracy:.1f}%)")
    
    # Combined analysis
    print(f"\n📊 Combined Analysis (Week 1 + Week 2)")
    print("-" * 40)
    total_correct = week1_correct + week2_correct
    total_games = week1_total + week2_total
    combined_accuracy = (total_correct / total_games * 100) if total_games > 0 else 0
    
    print(f"✅ Combined Accuracy: {total_correct}/{total_games} ({combined_accuracy:.1f}%)")
    print(f"📈 Week 1: {week1_accuracy:.1f}% | Week 2: {week2_accuracy:.1f}%")
    
    # Confidence level analysis
    print(f"\n🎯 Confidence Level Analysis")
    print("-" * 35)
    
    all_analysis = week1_analysis + week2_analysis
    confidence_stats = {}
    
    for game in all_analysis:
        conf = game['confidence']
        if conf not in confidence_stats:
            confidence_stats[conf] = {'correct': 0, 'total': 0}
        confidence_stats[conf]['total'] += 1
        if game['correct']:
            confidence_stats[conf]['correct'] += 1
    
    for conf in sorted(confidence_stats.keys(), reverse=True):
        stats = confidence_stats[conf]
        accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"Confidence {conf:2d}: {stats['correct']:2d}/{stats['total']:2d} ({accuracy:5.1f}%)")
    
    # Save comprehensive analysis
    output_dir = "data/outputs/2025"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save detailed analysis
    all_analysis_df = pd.DataFrame(all_analysis)
    analysis_file = f"{output_dir}/comprehensive-week1-2-analysis.csv"
    all_analysis_df.to_csv(analysis_file, index=False)
    print(f"\n💾 Saved comprehensive analysis to: {analysis_file}")
    
    # Save summary report
    report_file = f"{output_dir}/comprehensive-week1-2-report.md"
    with open(report_file, 'w') as f:
        f.write("# Comprehensive Week 1-2 Analysis\n\n")
        f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Week 1:** {week1_correct}/{week1_total} ({week1_accuracy:.1f}%)\n")
        f.write(f"- **Week 2:** {week2_correct}/{week2_total} ({week2_accuracy:.1f}%)\n")
        f.write(f"- **Combined:** {total_correct}/{total_games} ({combined_accuracy:.1f}%)\n\n")
        
        f.write("## Confidence Level Performance\n\n")
        f.write("| Confidence | Correct | Total | Accuracy |\n")
        f.write("|------------|---------|-------|----------|\n")
        for conf in sorted(confidence_stats.keys(), reverse=True):
            stats = confidence_stats[conf]
            accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            f.write(f"| {conf:2d} | {stats['correct']:2d} | {stats['total']:2d} | {accuracy:5.1f}% |\n")
        
        f.write("\n## Game-by-Game Results\n\n")
        f.write("| Week | Game | Pick | Confidence | Actual Winner | Result | Score |\n")
        f.write("|------|------|------|------------|---------------|--------|-------|\n")
        
        for game in all_analysis:
            result = "✅" if game['correct'] else "❌"
            f.write(f"| {game['week']} | {game['game']} | {game['pick']} | {game['confidence']} | {game['actual_winner']} | {result} | {game['score']} |\n")
    
    print(f"💾 Saved summary report to: {report_file}")
    
    conn.close()
    
    return {
        'week1_accuracy': week1_accuracy,
        'week2_accuracy': week2_accuracy,
        'combined_accuracy': combined_accuracy,
        'total_games': total_games,
        'confidence_stats': confidence_stats
    }

if __name__ == "__main__":
    results = comprehensive_week2_analysis()
    print(f"\n🎯 Comprehensive Analysis Complete!")
    print(f"Week 1: {results['week1_accuracy']:.1f}% | Week 2: {results['week2_accuracy']:.1f}% | Combined: {results['combined_accuracy']:.1f}%")


