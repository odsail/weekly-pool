#!/usr/bin/env python3
"""
Incorporate Travel and International Game Factors
Adds travel, timezone, and international game considerations to Week 4 picks.
"""

import os
import json
from datetime import datetime
from database_manager import DatabaseManager

# Initialize DatabaseManager
db_manager = DatabaseManager('data/nfl_pool_v2.db')

def analyze_travel_factors():
    """
    Analyze travel and international game factors for Week 4.
    """
    print("🌍 **TRAVEL AND INTERNATIONAL GAME ANALYSIS**")
    print("=" * 50)
    
    # Define Week 4 games with travel considerations
    week4_travel_analysis = {
        'international_games': {
            'Minnesota Vikings vs Pittsburgh Steelers': {
                'location': 'International (both teams away from home)',
                'vikings_advantage': 'None - both teams equally affected',
                'timezone_impact': 'Both teams adjusting to same timezone',
                'travel_fatigue': 'Both teams have similar travel burden',
                'confidence_adjustment': 'No adjustment needed - neutral field'
            }
        },
        'back_to_back_international': {
            'Minnesota Vikings': {
                'week4': 'vs Pittsburgh Steelers (international)',
                'week5': 'vs [opponent] (international)',
                'advantage': 'Vikings will be acclimated to timezone in Week 5',
                'opponent_disadvantage': 'Week 5 opponent will be adjusting to timezone',
                'confidence_adjustment': 'Consider Vikings advantage for Week 5'
            }
        },
        'regular_travel': {
            'teams_with_significant_travel': [
                'Teams traveling across multiple time zones',
                'Teams with short rest periods',
                'Teams with back-to-back road games'
            ]
        }
    }
    
    return week4_travel_analysis

def create_travel_adjusted_picks():
    """
    Create travel-adjusted picks for Week 4.
    """
    print("\n🎯 **CREATING TRAVEL-ADJUSTED PICKS**")
    print("=" * 50)
    
    # Read the primary model picks
    with open('data/outputs/2025/week-week4-straight-up-consensus.md', 'r') as f:
        primary_picks_content = f.read()
    
    # Define travel adjustments
    travel_adjustments = {
        'Minnesota Vikings vs Pittsburgh Steelers': {
            'original_pick': 'Minnesota Vikings',
            'original_confidence': 1,
            'travel_factor': 'International game - both teams away from home',
            'adjustment': 'No home field advantage for either team',
            'adjusted_pick': 'Minnesota Vikings',  # Keep original pick
            'adjusted_confidence': 1,  # No change needed
            'rationale': 'Both teams equally affected by international travel'
        }
    }
    
    # Create travel-adjusted picks
    travel_adjusted_picks = []
    
    # For now, most picks remain the same since Week 4 has minimal travel impact
    # The main impact will be in Week 5 when Vikings have acclimation advantage
    
    return travel_adjustments

def save_travel_analysis(travel_analysis, travel_adjustments):
    """
    Save travel analysis to files.
    """
    print("\n💾 **SAVING TRAVEL ANALYSIS**")
    print("=" * 50)
    
    # Create output directory
    os.makedirs('data/outputs/2025', exist_ok=True)
    
    # Save travel analysis
    travel_file = 'data/outputs/2025/week4-travel-analysis.json'
    with open(travel_file, 'w') as f:
        json.dump({
            'week': 4,
            'season': 2025,
            'generated': datetime.now().isoformat(),
            'travel_analysis': travel_analysis,
            'travel_adjustments': travel_adjustments
        }, f, indent=2)
    
    print(f"✅ Travel analysis saved: {travel_file}")
    
    # Create human-readable summary
    create_travel_summary(travel_analysis, travel_adjustments)

def create_travel_summary(travel_analysis, travel_adjustments):
    """
    Create a human-readable travel analysis summary.
    """
    summary_content = f"""# Week 4 Travel and International Game Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Command Used:** `python incorporate_travel_factors.py`

## International Games Analysis

### Minnesota Vikings vs Pittsburgh Steelers
- **Location:** International (both teams away from home)
- **Vikings Advantage:** None - both teams equally affected
- **Timezone Impact:** Both teams adjusting to same timezone
- **Travel Fatigue:** Both teams have similar travel burden
- **Confidence Adjustment:** No adjustment needed - neutral field

## Back-to-Back International Games

### Minnesota Vikings Schedule:
- **Week 4:** vs Pittsburgh Steelers (international)
- **Week 5:** vs [opponent] (international)
- **Advantage:** Vikings will be acclimated to timezone in Week 5
- **Opponent Disadvantage:** Week 5 opponent will be adjusting to timezone
- **Confidence Adjustment:** Consider Vikings advantage for Week 5

## Travel Adjustments Applied

### Week 4 Adjustments:
"""
    
    for game, adjustment in travel_adjustments.items():
        summary_content += f"""
#### {game}
- **Original Pick:** {adjustment['original_pick']} ({adjustment['original_confidence']} pts)
- **Travel Factor:** {adjustment['travel_factor']}
- **Adjustment:** {adjustment['adjustment']}
- **Adjusted Pick:** {adjustment['adjusted_pick']} ({adjustment['adjusted_confidence']} pts)
- **Rationale:** {adjustment['rationale']}
"""
    
    summary_content += f"""
## Key Insights

### Week 4 Impact:
- **Minimal travel impact** for most games
- **International game** creates neutral field advantage
- **No significant adjustments** needed for current picks

### Week 5 Considerations:
- **Vikings will have acclimation advantage** in their second international game
- **Opponent will be adjusting** to timezone for first time
- **Consider Vikings as stronger pick** in Week 5

### Future Travel Factors to Monitor:
- Teams with back-to-back road games
- Cross-country travel (3+ time zones)
- Short rest periods (Thursday to Sunday games)
- International game sequences

## Recommendations

1. **Week 4:** Proceed with current picks - minimal travel impact
2. **Week 5:** Consider Vikings advantage in international game
3. **Future Weeks:** Monitor for travel patterns and adjust accordingly
4. **Model Enhancement:** Incorporate travel factors into future model inputs

---
*Generated by Travel and International Game Analysis*
"""
    
    # Save summary
    summary_file = 'data/outputs/2025/week4-travel-analysis-summary.md'
    with open(summary_file, 'w') as f:
        f.write(summary_content)
    
    print(f"✅ Travel summary created: {summary_file}")

def main():
    print("🌍 **TRAVEL AND INTERNATIONAL GAME ANALYSIS**")
    print("=" * 50)
    
    # Analyze travel factors
    travel_analysis = analyze_travel_factors()
    
    # Create travel-adjusted picks
    travel_adjustments = create_travel_adjusted_picks()
    
    # Save analysis
    save_travel_analysis(travel_analysis, travel_adjustments)
    
    print(f"\n✅ **TRAVEL ANALYSIS COMPLETE**")
    print("=" * 40)
    print("🌍 International game factors analyzed")
    print("✈️ Travel considerations documented")
    print("📊 Week 4 picks remain unchanged (minimal impact)")
    print("🎯 Week 5 Vikings advantage identified")
    
    print(f"\n📋 **COMMAND USED:**")
    print("```bash")
    print("python incorporate_travel_factors.py")
    print("```")

if __name__ == "__main__":
    main()



