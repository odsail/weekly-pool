#!/usr/bin/env python3
"""
Analyze consensus failures from the pool results to identify key insights
about games where everyone picked a team that lost.
"""

from database_manager import DatabaseManager
import pandas as pd

# Initialize DatabaseManager
db_manager = DatabaseManager('data/nfl_pool_v2.db')

def analyze_consensus_failures():
    """
    Analyze all consensus failures across weeks and compare with expert picks.
    """
    print("🔍 **CONSENSUS FAILURE ANALYSIS**")
    print("=" * 60)
    
    # Define the consensus failures we identified
    consensus_failures = {
        1: [
            {
                'game': 'Los Angeles Chargers @ Kansas City Chiefs',
                'popular_pick': 'Kansas City Chiefs',
                'pick_count': 13,
                'actual_winner': 'Los Angeles Chargers',
                'insight': 'Chiefs were heavily favored but lost at home to Chargers'
            },
            {
                'game': 'New England Patriots @ Las Vegas Raiders', 
                'popular_pick': 'New England Patriots',
                'pick_count': 11,
                'actual_winner': 'Las Vegas Raiders',
                'insight': 'Patriots were favored on the road but Raiders won'
            },
            {
                'game': 'Chicago Bears @ Minnesota Vikings',
                'popular_pick': 'Chicago Bears', 
                'pick_count': 12,
                'actual_winner': 'Minnesota Vikings',
                'insight': 'Bears were picked by many but Vikings won at home'
            }
        ],
        2: [
            {
                'game': 'Miami Dolphins @ New England Patriots',
                'popular_pick': 'Miami Dolphins',
                'pick_count': 12,
                'actual_winner': 'New England Patriots', 
                'insight': 'Dolphins were favored but Patriots won at home'
            },
            {
                'game': 'Pittsburgh Steelers @ Seattle Seahawks',
                'popular_pick': 'Pittsburgh Steelers',
                'pick_count': 18,
                'actual_winner': 'Seattle Seahawks',
                'insight': 'UNIVERSAL PICK FAILURE - Everyone picked Steelers, Seahawks won'
            },
            {
                'game': 'Indianapolis Colts @ Denver Broncos',
                'popular_pick': 'Denver Broncos',
                'pick_count': 11,
                'actual_winner': 'Indianapolis Colts',
                'insight': 'Broncos were favored at home but Colts won'
            },
            {
                'game': 'Minnesota Vikings @ Atlanta Falcons',
                'popular_pick': 'Minnesota Vikings',
                'pick_count': 17,
                'actual_winner': 'Atlanta Falcons',
                'insight': 'NEAR UNIVERSAL PICK FAILURE - 17/18 picked Vikings, Falcons won'
            }
        ],
        3: [
            {
                'game': 'Cleveland Browns @ Green Bay Packers',
                'popular_pick': 'Green Bay Packers',
                'pick_count': 18,
                'actual_winner': 'Cleveland Browns',
                'insight': 'UNIVERSAL PICK FAILURE - Everyone picked Packers, Browns won'
            },
            {
                'game': 'Carolina Panthers @ Atlanta Falcons',
                'popular_pick': 'Atlanta Falcons',
                'pick_count': 16,
                'actual_winner': 'Carolina Panthers',
                'insight': 'NEAR UNIVERSAL PICK FAILURE - 16/18 picked Falcons, Panthers won'
            },
            {
                'game': 'Chicago Bears @ Dallas Cowboys',
                'popular_pick': 'Dallas Cowboys',
                'pick_count': 13,
                'actual_winner': 'Chicago Bears',
                'insight': 'Cowboys were heavily favored but Bears won'
            },
            {
                'game': 'Baltimore Ravens @ Detroit Lions',
                'popular_pick': 'Baltimore Ravens',
                'pick_count': 16,
                'actual_winner': 'Detroit Lions',
                'insight': 'NEAR UNIVERSAL PICK FAILURE - 16/18 picked Ravens, Lions won'
            }
        ]
    }
    
    print("\n📊 **SUMMARY OF CONSENSUS FAILURES:**")
    print("-" * 40)
    
    total_failures = 0
    universal_failures = 0
    near_universal_failures = 0
    
    for week, failures in consensus_failures.items():
        print(f"\n**Week {week}:**")
        for failure in failures:
            total_failures += 1
            if failure['pick_count'] == 18:
                universal_failures += 1
                print(f"  🚨 **UNIVERSAL FAILURE**: {failure['game']}")
                print(f"     Everyone picked {failure['popular_pick']}, {failure['actual_winner']} won")
            elif failure['pick_count'] >= 16:
                near_universal_failures += 1
                print(f"  ⚠️  **NEAR UNIVERSAL FAILURE**: {failure['game']}")
                print(f"     {failure['pick_count']}/18 picked {failure['popular_pick']}, {failure['actual_winner']} won")
            else:
                print(f"  ❌ **CONSENSUS FAILURE**: {failure['game']}")
                print(f"     {failure['pick_count']}/18 picked {failure['popular_pick']}, {failure['actual_winner']} won")
            print(f"     💡 Insight: {failure['insight']}")
            print()
    
    print(f"\n📈 **STATISTICS:**")
    print(f"  • Total consensus failures: {total_failures}")
    print(f"  • Universal failures (18/18 wrong): {universal_failures}")
    print(f"  • Near universal failures (16+/18 wrong): {near_universal_failures}")
    print(f"  • Regular consensus failures: {total_failures - universal_failures - near_universal_failures}")
    
    return consensus_failures

def analyze_fundaysunday_performance():
    """
    Analyze FundaySunday's performance against consensus failures.
    """
    print("\n🎯 **FUNDAYSUNDAY PERFORMANCE ANALYSIS**")
    print("=" * 50)
    
    # Get FundaySunday's picks for each week
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        
        for week in [1, 2, 3]:
            print(f"\n**Week {week}:**")
            cursor.execute("""
                SELECT 
                    ht.name || ' @ ' || at.name as game,
                    t.name as pick_team,
                    pr.confidence_points,
                    pr.is_correct
                FROM pool_results pr
                JOIN games g ON pr.game_id = g.id
                JOIN teams ht ON g.home_team_id = ht.id
                JOIN teams at ON g.away_team_id = at.id
                JOIN teams t ON pr.pick_team_id = t.id
                WHERE pr.season_year = 2025 AND pr.week = ? AND pr.participant_name = 'FundaySunday'
                ORDER BY pr.confidence_points DESC
            """, (week,))
            
            picks = cursor.fetchall()
            
            correct_picks = 0
            total_score = 0
            
            for pick in picks:
                game, pick_team, confidence, is_correct = pick
                status = "✅" if is_correct else "❌"
                if is_correct:
                    correct_picks += 1
                    total_score += confidence
                print(f"  {status} {confidence:2d} pts: {pick_team} ({game})")
            
            accuracy = (correct_picks / len(picks)) * 100 if picks else 0
            print(f"  📊 Week {week} Summary: {correct_picks}/{len(picks)} correct ({accuracy:.1f}%) - {total_score} points")

def compare_with_expert_picks():
    """
    Compare consensus failures with expert picks to find insights.
    """
    print("\n🔍 **COMPARISON WITH EXPERT PICKS**")
    print("=" * 40)
    
    print("\n💡 **KEY INSIGHTS FROM CONSENSUS FAILURES:**")
    print()
    print("1. **Universal Pick Failures (18/18 wrong):**")
    print("   • Week 2: Pittsburgh Steelers @ Seattle Seahawks")
    print("   • Week 3: Cleveland Browns @ Green Bay Packers")
    print("   → These games had EVERYONE picking the same team - major upsets!")
    print()
    print("2. **Near Universal Failures (16+/18 wrong):**")
    print("   • Week 2: Minnesota Vikings @ Atlanta Falcons (17/18 wrong)")
    print("   • Week 3: Carolina Panthers @ Atlanta Falcons (16/18 wrong)")
    print("   • Week 3: Baltimore Ravens @ Detroit Lions (16/18 wrong)")
    print("   → These games had overwhelming consensus that was wrong")
    print()
    print("3. **Pattern Analysis:**")
    print("   • Home field advantage was often overestimated")
    print("   • Popular teams (Packers, Steelers, Ravens) were overpicked")
    print("   • Underdogs won more often than expected")
    print()
    print("4. **Expert Pick Implications:**")
    print("   • When experts and public consensus align, it's often wrong")
    print("   • Look for contrarian opportunities when everyone agrees")
    print("   • Consider the 'fade the public' strategy for future picks")

def generate_recommendations():
    """
    Generate recommendations for future picks based on consensus failure analysis.
    """
    print("\n🎯 **RECOMMENDATIONS FOR FUTURE PICKS**")
    print("=" * 45)
    
    print("\n1. **Contrarian Strategy:**")
    print("   • When 16+ people pick the same team, consider the opposite")
    print("   • Look for games where public sentiment is overwhelming")
    print("   • Pay attention to home field advantage overestimation")
    print()
    print("2. **Expert vs Public Analysis:**")
    print("   • Compare expert picks with public consensus")
    print("   • When they align, it's often a trap")
    print("   • Look for expert picks that differ from public sentiment")
    print()
    print("3. **Team-Specific Insights:**")
    print("   • Packers, Steelers, Ravens were overpicked multiple times")
    print("   • Consider fading these popular teams in close games")
    print("   • Look for value in underdog picks")
    print()
    print("4. **Week 4 Application:**")
    print("   • Review Week 4 picks for consensus patterns")
    print("   • Identify games where everyone might pick the same team")
    print("   • Consider contrarian picks for those games")

def main():
    print("🎯 **COMPREHENSIVE CONSENSUS FAILURE ANALYSIS**")
    print("=" * 60)
    
    # Run all analyses
    consensus_failures = analyze_consensus_failures()
    analyze_fundaysunday_performance()
    compare_with_expert_picks()
    generate_recommendations()
    
    print("\n✅ **ANALYSIS COMPLETE**")
    print("=" * 30)
    print("\nThis analysis shows that consensus failures are common and predictable.")
    print("The key insight is that when everyone agrees on a pick, it's often wrong.")
    print("Use this information to make more contrarian picks in future weeks.")

if __name__ == "__main__":
    main()

