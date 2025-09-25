#!/usr/bin/env python3
"""
Fix ML Model Confidence Calibration
Addresses the overconfident predictions that led to poor Week 1 performance
"""

import pandas as pd
import numpy as np
from database_manager import DatabaseManager
from ml_model import NFLConfidenceMLModel

def analyze_confidence_issues():
    """Analyze the confidence calibration problems"""
    
    print("🔍 Analyzing ML Model Confidence Issues...")
    
    # Load Week 1 comparison data
    df = pd.read_csv('data/outputs/2025/week1-live-ml-comparison.csv')
    
    print(f"\n📊 Week 1 Performance Analysis:")
    print(f"   Original Accuracy: {df['original_correct'].mean():.1%}")
    print(f"   ML Model Accuracy: {df['ml_correct'].mean():.1%}")
    
    # Analyze confidence vs accuracy
    print(f"\n🎯 Confidence vs Accuracy Analysis:")
    
    # High confidence wrong picks
    high_conf_wrong = df[(df['ml_confidence'] >= 12) & (df['ml_correct'] == False)]
    print(f"   High Confidence (12+ pts) Wrong Picks: {len(high_conf_wrong)}")
    
    for _, row in high_conf_wrong.iterrows():
        print(f"     - {row['game']}: {row['ml_pick']} ({row['ml_confidence']} pts, {row['ml_win_prob']:.1%}) → {row['actual_winner']}")
    
    # Win probability calibration
    print(f"\n📈 Win Probability Calibration:")
    print(f"   Average ML Win Prob for Wrong Picks: {df[df['ml_correct'] == False]['ml_win_prob'].mean():.1%}")
    print(f"   Average ML Win Prob for Correct Picks: {df[df['ml_correct'] == True]['ml_win_prob'].mean():.1%}")
    
    return df

def create_improved_confidence_mapping():
    """Create improved confidence point mapping with uncertainty penalty"""
    
    print("\n🛠️ Creating Improved Confidence Mapping...")
    
    # More conservative confidence mapping
    confidence_mapping = {
        (0.95, 1.00): 16,  # Very high confidence
        (0.90, 0.95): 15,  # High confidence
        (0.85, 0.90): 14,  # High confidence
        (0.80, 0.85): 13,  # Medium-high confidence
        (0.75, 0.80): 12,  # Medium-high confidence
        (0.70, 0.75): 11,  # Medium confidence
        (0.65, 0.70): 10,  # Medium confidence
        (0.60, 0.65): 9,   # Medium-low confidence
        (0.55, 0.60): 8,   # Medium-low confidence
        (0.50, 0.55): 7,   # Low confidence
    }
    
    def map_confidence(win_prob):
        """Map win probability to confidence points with uncertainty penalty"""
        
        # Add uncertainty penalty - reduce confidence for probabilities near 0.5
        uncertainty_penalty = 1.0 - abs(win_prob - 0.5) * 2  # Max penalty at 0.5
        adjusted_prob = win_prob - (uncertainty_penalty * 0.1)  # Reduce by up to 10%
        
        # Map to confidence points
        for (min_prob, max_prob), conf_points in confidence_mapping.items():
            if min_prob <= adjusted_prob < max_prob:
                return conf_points
        
        # Default to low confidence
        return 7
    
    return map_confidence

def test_improved_mapping():
    """Test the improved confidence mapping on Week 1 data"""
    
    print("\n🧪 Testing Improved Confidence Mapping...")
    
    df = pd.read_csv('data/outputs/2025/week1-live-ml-comparison.csv')
    map_confidence = create_improved_confidence_mapping()
    
    # Apply improved mapping
    df['improved_confidence'] = df['ml_win_prob'].apply(map_confidence)
    
    # Calculate new accuracy (assuming same picks, just different confidence)
    print(f"\n📊 Improved Confidence Results:")
    print(f"   Original ML Accuracy: {df['ml_correct'].mean():.1%}")
    print(f"   Improved Confidence Range: {df['improved_confidence'].min()}-{df['improved_confidence'].max()}")
    print(f"   Average Confidence: {df['improved_confidence'].mean():.1f}")
    
    # Show confidence distribution
    conf_dist = df['improved_confidence'].value_counts().sort_index()
    print(f"\n📈 Confidence Distribution:")
    for conf, count in conf_dist.items():
        print(f"   {conf} points: {count} games")
    
    return df

def main():
    """Main function to fix ML confidence calibration"""
    
    print("🔧 Fixing ML Model Confidence Calibration")
    print("=" * 50)
    
    # Step 1: Analyze current issues
    df = analyze_confidence_issues()
    
    # Step 2: Test improved mapping
    df_improved = test_improved_mapping()
    
    # Step 3: Save improved results
    output_file = 'data/outputs/2025/week1-improved-confidence.csv'
    df_improved.to_csv(output_file, index=False)
    print(f"\n💾 Saved improved confidence analysis to {output_file}")
    
    print(f"\n✅ Confidence calibration analysis complete!")
    print(f"💡 Key insights:")
    print(f"   - ML model was overconfident (too many 12-14 point picks)")
    print(f"   - Win probabilities don't match actual outcomes")
    print(f"   - Need uncertainty penalty for probabilities near 0.5")
    print(f"   - Consider retraining with Week 1 feedback")

if __name__ == "__main__":
    main()


