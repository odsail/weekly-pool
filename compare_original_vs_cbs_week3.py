#!/usr/bin/env python3
"""
Compare Original Week 3 picks vs CBS Expert Enhanced picks
"""

import pandas as pd
import os

def compare_week3_picks():
    """Compare original picks with CBS expert enhanced picks"""
    
    print("🔍 Week 3 Picks Comparison: Original vs CBS Expert Enhanced")
    print("=" * 60)
    
    # Read both CSV files
    original_file = "data/outputs/2025/week-week3-original-picks.csv"
    cbs_file = "data/outputs/2025/week-week3-cbs-expert-picks.csv"
    
    if not os.path.exists(original_file):
        print(f"❌ Original file not found: {original_file}")
        return
    
    if not os.path.exists(cbs_file):
        print(f"❌ CBS file not found: {cbs_file}")
        return
    
    original_df = pd.read_csv(original_file)
    cbs_df = pd.read_csv(cbs_file)
    
    # Create comparison
    comparison_data = []
    
    for _, orig_row in original_df.iterrows():
        # Find matching game in CBS data
        cbs_match = None
        for _, cbs_row in cbs_df.iterrows():
            if (orig_row['away_team'] == cbs_row['away_team'] and 
                orig_row['home_team'] == cbs_row['home_team']):
                cbs_match = cbs_row
                break
        
        if cbs_match is not None:
            pick_changed = orig_row['pick_team'] != cbs_match['pick_team']
            confidence_change = cbs_match['confidence_points'] - orig_row['confidence_points']
            
            comparison_data.append({
                'game': f"{orig_row['away_team']} @ {orig_row['home_team']}",
                'original_pick': orig_row['pick_team'],
                'original_conf': orig_row['confidence_points'],
                'original_prob': f"{orig_row['pick_prob']*100:.1f}%",
                'cbs_pick': cbs_match['pick_team'],
                'cbs_conf': cbs_match['confidence_points'],
                'cbs_prob': f"{cbs_match['combined_confidence']*100:.1f}%",
                'pick_changed': pick_changed,
                'confidence_change': confidence_change,
                'method': cbs_match['pick_method']
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Display results
    print(f"\n📊 Detailed Comparison:")
    print("-" * 60)
    
    for _, row in comparison_df.iterrows():
        change_indicator = "🔄" if row['pick_changed'] else "✅"
        conf_change = f"{row['confidence_change']:+d}" if row['confidence_change'] != 0 else "0"
        
        print(f"{change_indicator} {row['game']}")
        print(f"   Original: {row['original_pick']} ({row['original_conf']} pts, {row['original_prob']})")
        print(f"   CBS:      {row['cbs_pick']} ({row['cbs_conf']} pts, {row['cbs_prob']}) [{row['method']}]")
        if row['pick_changed']:
            print(f"   ⚠️  PICK CHANGED! Confidence change: {conf_change}")
        print()
    
    # Summary statistics
    total_games = len(comparison_df)
    picks_changed = len(comparison_df[comparison_df['pick_changed'] == True])
    picks_unchanged = total_games - picks_changed
    
    print(f"📈 Summary Statistics:")
    print(f"   Total Games: {total_games}")
    print(f"   Picks Changed: {picks_changed} ({picks_changed/total_games*100:.1f}%)")
    print(f"   Picks Unchanged: {picks_unchanged} ({picks_unchanged/total_games*100:.1f}%)")
    
    # Method breakdown
    method_counts = comparison_df['method'].value_counts()
    print(f"\n🎯 Method Breakdown:")
    for method, count in method_counts.items():
        print(f"   {method}: {count} games")
    
    # Save comparison to file
    output_file = "data/outputs/2025/week3-original-vs-cbs-comparison.csv"
    comparison_df.to_csv(output_file, index=False)
    print(f"\n💾 Saved comparison: {output_file}")
    
    return comparison_df

if __name__ == "__main__":
    compare_week3_picks()


