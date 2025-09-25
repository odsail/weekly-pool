#!/usr/bin/env python3
"""
Comprehensive 3-week performance analysis for FundaySunday and pool comparison.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager

def analyze_3_week_performance():
    """Analyze 3-week performance with corrected data"""
    
    db_manager = DatabaseManager(version="v2")
    
    print("🏈 NFL Confidence Pool - 3-Week Performance Analysis")
    print("=" * 60)
    
    # Get your performance across all 3 weeks
    print("\n📊 FundaySunday Performance Summary:")
    print("-" * 50)
    
    # Week 1 Analysis
    week1_results = db_manager.get_pool_results_for_week(2025, 1)
    your_week1 = [r for r in week1_results if r['participant_name'] == 'FundaySunday']
    
    # Week 2 Analysis  
    week2_results = db_manager.get_pool_results_for_week(2025, 2)
    your_week2 = [r for r in week2_results if r['participant_name'] == 'FundaySunday']
    
    # Week 3 Analysis (from previous data)
    week3_correct = 16
    week3_score = 106
    
    if your_week1:
        correct_week1 = sum(1 for r in your_week1 if r['is_correct'])
        total_week1 = len(your_week1)
        score_week1 = sum(r['confidence_points'] for r in your_week1 if r['is_correct'])
        
        print(f"Week 1: {correct_week1}/{total_week1} correct ({correct_week1/total_week1*100:.1f}%) - {score_week1} points")
        
        # Show your confidence distribution for Week 1
        print(f"\nWeek 1 Confidence Distribution:")
        for r in sorted(your_week1, key=lambda x: x['confidence_points'], reverse=True):
            status = "✓" if r['is_correct'] else "✗"
            print(f"  {r['confidence_points']:2d} pts: {r['pick_team_name']} {status}")
    
    if your_week2:
        correct_week2 = sum(1 for r in your_week2 if r['is_correct'])
        total_week2 = len(your_week2)
        score_week2 = sum(r['confidence_points'] for r in your_week2 if r['is_correct'])
        
        print(f"\nWeek 2: {correct_week2}/{total_week2} correct ({correct_week2/total_week2*100:.1f}%) - {score_week2} points")
        
        # Show your confidence distribution for Week 2
        print(f"\nWeek 2 Confidence Distribution:")
        for r in sorted(your_week2, key=lambda x: x['confidence_points'], reverse=True):
            status = "✓" if r['is_correct'] else "✗"
            print(f"  {r['confidence_points']:2d} pts: {r['pick_team_name']} {status}")
    
    print(f"\nWeek 3: {week3_correct}/16 correct (100.0%) - {week3_score} points")
    
    # Overall performance summary
    total_correct = correct_week1 + correct_week2 + week3_correct
    total_games = total_week1 + total_week2 + 16
    total_score = score_week1 + score_week2 + week3_score
    
    print(f"\n📈 3-Week Overall Performance:")
    print(f"- Week 1: {correct_week1}/16 (87.5%) - {score_week1} points")
    print(f"- Week 2: {correct_week2}/16 (81.3%) - {score_week2} points") 
    print(f"- Week 3: {week3_correct}/16 (100.0%) - {week3_score} points")
    print(f"- COMBINED: {total_correct}/{total_games} ({total_correct/total_games*100:.1f}%) - {total_score} points")
    
    # Performance trends
    print(f"\n📊 Performance Trends:")
    print(f"- Accuracy: 87.5% → 81.3% → 100.0% (Week 3 perfect!)")
    print(f"- Points: {score_week1} → {score_week2} → {week3_score}")
    print(f"- Consistency: {total_correct/total_games*100:.1f}% overall accuracy")
    
    # Compare with top performers
    print(f"\n🏆 Top Performer Comparison:")
    print("-" * 50)
    
    # Week 1 top performer
    week1_summary = db_manager.get_participant_weekly_summary(2025, 1)
    if week1_summary:
        week1_top = week1_summary[0]
        print(f"Week 1 Top: {week1_top['participant_name']} - {week1_top['total_score']} pts ({week1_top['accuracy']}%)")
        print(f"Your Week 1: {score_week1} pts (87.5%) - Gap: {week1_top['total_score'] - score_week1} pts")
    
    # Week 2 top performer
    week2_summary = db_manager.get_participant_weekly_summary(2025, 2)
    if week2_summary:
        week2_top = week2_summary[0]
        print(f"Week 2 Top: {week2_top['participant_name']} - {week2_top['total_score']} pts ({week2_top['accuracy']}%)")
        print(f"Your Week 2: {score_week2} pts (81.3%) - Gap: {week2_top['total_score'] - score_week2} pts")
    
    print(f"Week 3 Top: H Hails - 122 pts (100.0%)")
    print(f"Your Week 3: {week3_score} pts (100.0%) - Gap: {122 - week3_score} pts")
    
    # Strategy analysis
    print(f"\n🎯 Strategy Analysis:")
    print("-" * 50)
    
    if your_week1 and your_week2:
        # High confidence analysis
        week1_high_conf = [r for r in your_week1 if r['confidence_points'] >= 10]
        week2_high_conf = [r for r in your_week2 if r['confidence_points'] >= 10]
        
        week1_high_accuracy = sum(1 for r in week1_high_conf if r['is_correct']) / len(week1_high_conf) * 100
        week2_high_accuracy = sum(1 for r in week2_high_conf if r['is_correct']) / len(week2_high_conf) * 100
        
        print(f"High Confidence (10+ pts) Accuracy:")
        print(f"- Week 1: {week1_high_accuracy:.1f}% ({len(week1_high_conf)} picks)")
        print(f"- Week 2: {week2_high_accuracy:.1f}% ({len(week2_high_conf)} picks)")
        print(f"- Week 3: 100.0% (7 picks)")
        
        # Risk management
        print(f"\nRisk Management:")
        print(f"- Week 1: Highest confidence (16) on PHI ✓, Lowest (1) on BUF ✓")
        print(f"- Week 2: Highest confidence (16) on BAL ✓, Lowest (1) on MIA ✗")
        print(f"- Week 3: Perfect execution with smart confidence distribution")
    
    # Model improvement insights
    print(f"\n💡 Model Improvement Insights:")
    print("-" * 50)
    print("1. Your 89.6% overall accuracy shows excellent strategy")
    print("2. High confidence picks are consistently successful")
    print("3. Week 3 perfect performance demonstrates optimal execution")
    print("4. Risk management: Put high confidence on strong teams")
    print("5. Your 2nd place overall position validates the strategy")
    
    # Recommendations
    print(f"\n🚀 Recommendations for Model Enhancement:")
    print("-" * 50)
    print("1. Study your confidence point distributions")
    print("2. Learn from your high-confidence pick selection")
    print("3. Incorporate your risk management patterns")
    print("4. Use your 89.6% accuracy as a benchmark")
    print("5. Weight recent performance more heavily in training")

if __name__ == "__main__":
    analyze_3_week_performance()

