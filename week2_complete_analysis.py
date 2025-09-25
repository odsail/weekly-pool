#!/usr/bin/env python3
"""
Complete Week 2 analysis including over/under results
"""

import sqlite3
import pandas as pd
from datetime import datetime

def week2_complete_analysis():
    """Complete Week 2 analysis with over/under results"""
    
    print("📊 Complete Week 2 Analysis - Including Over/Under Results")
    print("=" * 60)
    
    # Connect to database
    conn = sqlite3.connect("data/nfl_pool_v2.db")
    cursor = conn.cursor()
    
    # Get all Week 2 data
    cursor.execute("""
        SELECT 
            ht.name as home_team, 
            at.name as away_team, 
            g.home_score, 
            g.away_score, 
            o.total_points,
            p.pick_team_id,
            pt.name as pick_team,
            p.confidence_points
        FROM games g 
        JOIN teams ht ON g.home_team_id = ht.id 
        JOIN teams at ON g.away_team_id = at.id 
        LEFT JOIN odds o ON g.id = o.game_id 
        LEFT JOIN picks p ON g.id = p.game_id
        LEFT JOIN teams pt ON p.pick_team_id = pt.id
        WHERE g.season_year = 2025 AND g.week = 2 
        ORDER BY p.confidence_points DESC
    """)
    
    results = cursor.fetchall()
    
    print("\n🎯 Week 2 Complete Results:")
    print("-" * 60)
    
    correct_picks = 0
    total_picks = 0
    over_hits = 0
    under_hits = 0
    total_over_under = 0
    
    for home_team, away_team, home_score, away_score, total_points, pick_team_id, pick_team, confidence in results:
        if home_score is not None and away_score is not None:
            actual_total = home_score + away_score
            actual_winner = home_team if home_score > away_score else away_team
            
            # Pick analysis
            pick_correct = "❌"
            if pick_team and pick_team == actual_winner:
                pick_correct = "✅"
                correct_picks += 1
            total_picks += 1
            
            # Over/Under analysis
            over_under_result = ""
            if total_points:
                total_over_under += 1
                if actual_total > total_points:
                    over_under_result = "OVER ✅"
                    over_hits += 1
                elif actual_total < total_points:
                    over_under_result = "UNDER ❌"
                    under_hits += 1
                else:
                    over_under_result = "PUSH"
            
            print(f"{confidence:2d} pts: {pick_team} {pick_correct} | {away_team} @ {home_team}: {away_score}-{home_score} (Total: {actual_total}, O/U: {total_points}) {over_under_result}")
    
    # Summary statistics
    pick_accuracy = (correct_picks / total_picks * 100) if total_picks > 0 else 0
    over_accuracy = (over_hits / total_over_under * 100) if total_over_under > 0 else 0
    
    print(f"\n📈 Summary Statistics:")
    print(f"   Pick Accuracy: {correct_picks}/{total_picks} ({pick_accuracy:.1f}%)")
    print(f"   Over Hits: {over_hits}/{total_over_under} ({over_accuracy:.1f}%)")
    print(f"   Under Hits: {under_hits}/{total_over_under} ({100-over_accuracy:.1f}%)")
    
    # Confidence point analysis
    print(f"\n🎯 Confidence Point Analysis:")
    cursor.execute("""
        SELECT 
            p.confidence_points,
            pt.name as pick_team,
            CASE 
                WHEN pt.name = CASE WHEN g.home_score > g.away_score THEN ht.name ELSE at.name END 
                THEN 1 ELSE 0 
            END as correct
        FROM picks p
        JOIN games g ON p.game_id = g.id
        JOIN teams pt ON p.pick_team_id = pt.id
        JOIN teams ht ON g.home_team_id = ht.id
        JOIN teams at ON g.away_team_id = at.id
        WHERE g.season_year = 2025 AND g.week = 2
        AND g.home_score IS NOT NULL AND g.away_score IS NOT NULL
        ORDER BY p.confidence_points DESC
    """)
    
    confidence_results = cursor.fetchall()
    
    high_confidence_correct = 0
    high_confidence_total = 0
    low_confidence_correct = 0
    low_confidence_total = 0
    
    for conf, pick_team, correct in confidence_results:
        if conf >= 10:  # High confidence (10+ points)
            high_confidence_total += 1
            if correct:
                high_confidence_correct += 1
        else:  # Low confidence (1-9 points)
            low_confidence_total += 1
            if correct:
                low_confidence_correct += 1
    
    high_conf_accuracy = (high_confidence_correct / high_confidence_total * 100) if high_confidence_total > 0 else 0
    low_conf_accuracy = (low_confidence_correct / low_confidence_total * 100) if low_confidence_total > 0 else 0
    
    print(f"   High Confidence (10+ pts): {high_confidence_correct}/{high_confidence_total} ({high_conf_accuracy:.1f}%)")
    print(f"   Low Confidence (1-9 pts): {low_confidence_correct}/{low_confidence_total} ({low_conf_accuracy:.1f}%)")
    
    conn.close()
    
    # Save detailed analysis
    output_file = "data/outputs/2025/week2-complete-analysis.md"
    with open(output_file, 'w') as f:
        f.write("# Week 2 Complete Analysis\n")
        f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Pick Accuracy:** {correct_picks}/{total_picks} ({pick_accuracy:.1f}%)\n")
        f.write(f"- **Over Hits:** {over_hits}/{total_over_under} ({over_accuracy:.1f}%)\n")
        f.write(f"- **Under Hits:** {under_hits}/{total_over_under} ({100-over_accuracy:.1f}%)\n\n")
        
        f.write("## Confidence Analysis\n\n")
        f.write(f"- **High Confidence (10+ pts):** {high_confidence_correct}/{high_confidence_total} ({high_conf_accuracy:.1f}%)\n")
        f.write(f"- **Low Confidence (1-9 pts):** {low_confidence_correct}/{low_confidence_total} ({low_conf_accuracy:.1f}%)\n\n")
        
        f.write("## Game-by-Game Results\n\n")
        f.write("| Points | Pick | Result | Game | Score | Total | O/U |\n")
        f.write("|--------|------|--------|------|-------|-------|-----|\n")
        
        for home_team, away_team, home_score, away_score, total_points, pick_team_id, pick_team, confidence in results:
            if home_score is not None and away_score is not None:
                actual_total = home_score + away_score
                actual_winner = home_team if home_score > away_score else away_team
                pick_correct = "✅" if pick_team == actual_winner else "❌"
                
                over_under_result = ""
                if total_points:
                    if actual_total > total_points:
                        over_under_result = "OVER"
                    elif actual_total < total_points:
                        over_under_result = "UNDER"
                    else:
                        over_under_result = "PUSH"
                
                f.write(f"| {confidence:2d} | {pick_team} | {pick_correct} | {away_team} @ {home_team} | {away_score}-{home_score} | {actual_total} | {over_under_result} |\n")
    
    print(f"\n💾 Saved complete analysis: {output_file}")

if __name__ == "__main__":
    week2_complete_analysis()


