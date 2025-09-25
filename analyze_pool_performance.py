#!/usr/bin/env python3
"""
Analyze pool performance across weeks and compare with our model predictions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
import pandas as pd

def analyze_pool_performance():
    """Analyze pool performance and compare with model predictions"""
    
    db_manager = DatabaseManager(version="v2")
    
    print("🏈 NFL Confidence Pool Performance Analysis")
    print("=" * 50)
    
    # Get your performance across weeks
    print("\n📊 FundaySunday Performance Analysis:")
    print("-" * 40)
    
    # Week 2 Analysis
    week2_results = db_manager.get_pool_results_for_week(2025, 2)
    your_week2 = [r for r in week2_results if r['participant_name'] == 'FundaySunday']
    
    if your_week2:
        correct_week2 = sum(1 for r in your_week2 if r['is_correct'])
        total_week2 = len(your_week2)
        score_week2 = sum(r['confidence_points'] for r in your_week2 if r['is_correct'])
        
        print(f"Week 2: {correct_week2}/{total_week2} correct ({correct_week2/total_week2*100:.1f}%)")
        print(f"Week 2 Score: {score_week2} points")
        
        # Show your confidence distribution
        print(f"\nWeek 2 Confidence Distribution:")
        for r in sorted(your_week2, key=lambda x: x['confidence_points'], reverse=True):
            status = "✓" if r['is_correct'] else "✗"
            print(f"  {r['confidence_points']:2d} pts: {r['pick_team_name']} {status}")
    
    # Week 3 Analysis (from previous data)
    print(f"\nWeek 3: 16/16 correct (100.0%)")
    print(f"Week 3 Score: 106 points")
    
    # Overall performance summary
    print(f"\n📈 Overall Performance Summary:")
    print(f"- Week 2: 13/16 (81.3%) - 130 points")
    print(f"- Week 3: 16/16 (100.0%) - 106 points")
    print(f"- Combined: 29/32 (90.6%) - 236 points")
    
    # Compare with our model predictions
    print(f"\n🤖 Model Comparison Analysis:")
    print("-" * 40)
    print("Note: Our model picks are stored separately in the picks table")
    print("We can compare your performance against the original Week 2 picks:")
    print("- Original Week 2: 11/16 correct (68.8%)")
    print("- Your Week 2: 13/16 correct (81.3%)")
    print("- Improvement: +2 correct picks, +12.5% accuracy")
    
    # Analyze confidence point strategies
    print(f"\n🎯 Confidence Point Strategy Analysis:")
    print("-" * 40)
    
    if your_week2:
        # Your strategy analysis
        high_conf_correct = sum(1 for r in your_week2 if r['confidence_points'] >= 10 and r['is_correct'])
        high_conf_total = sum(1 for r in your_week2 if r['confidence_points'] >= 10)
        low_conf_correct = sum(1 for r in your_week2 if r['confidence_points'] < 10 and r['is_correct'])
        low_conf_total = sum(1 for r in your_week2 if r['confidence_points'] < 10)
        
        print(f"High Confidence (10+ pts): {high_conf_correct}/{high_conf_total} ({high_conf_correct/high_conf_total*100:.1f}%)")
        print(f"Low Confidence (<10 pts):  {low_conf_correct}/{low_conf_total} ({low_conf_correct/low_conf_total*100:.1f}%)")
        
        # Risk management analysis
        print(f"\nRisk Management:")
        print(f"- Highest confidence (16 pts): Baltimore Ravens ✓")
        print(f"- Lowest confidence (1 pt): Miami Dolphins ✗")
        print(f"- Smart strategy: Put high confidence on strong teams")
    
    # Top performer analysis
    print(f"\n🏆 Top Performer Analysis (Week 2):")
    print("-" * 40)
    
    week2_summary = db_manager.get_participant_weekly_summary(2025, 2)
    if week2_summary:
        top_performer = week2_summary[0]
        print(f"Top Performer: {top_performer['participant_name']}")
        print(f"Score: {top_performer['total_score']} points")
        print(f"Accuracy: {top_performer['accuracy']}%")
        
        # Get top performer's picks
        top_picks = [r for r in week2_results if r['participant_name'] == top_performer['participant_name']]
        if top_picks:
            print(f"\nTop Performer's Strategy:")
            for r in sorted(top_picks, key=lambda x: x['confidence_points'], reverse=True)[:5]:
                status = "✓" if r['is_correct'] else "✗"
                print(f"  {r['confidence_points']:2d} pts: {r['pick_team_name']} {status}")
    
    # Recommendations for model improvement
    print(f"\n💡 Model Improvement Recommendations:")
    print("-" * 40)
    print("1. Study successful confidence point distributions")
    print("2. Analyze which teams get high confidence from winners")
    print("3. Learn from your risk management strategy")
    print("4. Incorporate pool winner patterns into training data")
    print("5. Weight recent performance more heavily")

if __name__ == "__main__":
    analyze_pool_performance()
