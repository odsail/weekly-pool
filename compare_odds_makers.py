#!/usr/bin/env python3
"""
Compare our corrected picks with actual odds makers' picks
"""

import pandas as pd
from database_manager import DatabaseManager

def compare_with_odds_makers():
    """Compare our corrected picks with DraftKings and expert consensus"""
    
    print("🎯 Week 3 Picks Comparison: Our Model vs Odds Makers")
    print("=" * 60)
    
    # Get our corrected picks from database
    db = DatabaseManager(version="v2")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.game_id,
                pt.name as pick_team,
                p.confidence_points,
                p.win_probability,
                ht.name as home_team,
                at.name as away_team
            FROM picks p
            JOIN games g ON p.game_id = g.id
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            JOIN teams pt ON p.pick_team_id = pt.id
            WHERE g.season_year = 2025 AND g.week = 3
            ORDER BY p.confidence_points DESC
        """)
        our_picks = cursor.fetchall()
    
    # DraftKings/Expert consensus data from web search
    odds_makers_data = [
        # (away_team, home_team, expert_pick, draftkings_spread, our_pick, our_conf)
        ("Miami Dolphins", "Buffalo Bills", "Buffalo Bills", "Bills -12.5", "Buffalo Bills", 16),
        ("Indianapolis Colts", "Tennessee Titans", "Indianapolis Colts", "Colts -1.5", "Tennessee Titans", 9),
        ("Pittsburgh Steelers", "New England Patriots", "Pittsburgh Steelers", "Steelers -1.5", "New England Patriots", 11),
        ("New York Jets", "Tampa Bay Buccaneers", "Tampa Bay Buccaneers", "Buccaneers -7.5", "Tampa Bay Buccaneers", 7),
        ("Las Vegas Raiders", "Washington Commanders", "Washington Commanders", "Commanders -3.5", "Washington Commanders", 6),
        ("Los Angeles Rams", "Philadelphia Eagles", "Philadelphia Eagles", "Eagles -3.5", "Philadelphia Eagles", 12),
        ("Atlanta Falcons", "Carolina Panthers", "Atlanta Falcons", "Falcons -5.5", "Carolina Panthers", 5),
        ("Cincinnati Bengals", "Minnesota Vikings", "Minnesota Vikings", "Vikings -3.5", "Minnesota Vikings", 10),
        ("Houston Texans", "Jacksonville Jaguars", "Jacksonville Jaguars", "Jaguars -1.5", "Jacksonville Jaguars", 4),
        ("Green Bay Packers", "Cleveland Browns", "Green Bay Packers", "Packers -9.5", "Cleveland Browns", 8),
        ("Denver Broncos", "Los Angeles Chargers", "Los Angeles Chargers", "Chargers -2.5", "Los Angeles Chargers", 3),
        ("New Orleans Saints", "Seattle Seahawks", "Seattle Seahawks", "Seahawks -3.5", "Seattle Seahawks", 2),
        ("Arizona Cardinals", "San Francisco 49ers", "San Francisco 49ers", "49ers -3.5", "San Francisco 49ers", 13),
        ("Dallas Cowboys", "Chicago Bears", "Chicago Bears", "Bears -1.5", "Dallas Cowboys", 1),
        ("Kansas City Chiefs", "New York Giants", "Kansas City Chiefs", "Chiefs -1.5", "Kansas City Chiefs", 14),
        ("Detroit Lions", "Baltimore Ravens", "Baltimore Ravens", "Ravens -3.5", "Baltimore Ravens", 15)
    ]
    
    print("📊 Game-by-Game Comparison:")
    print("-" * 60)
    
    agreements = 0
    disagreements = 0
    total_games = len(odds_makers_data)
    
    for away, home, expert_pick, dk_spread, our_pick, our_conf in odds_makers_data:
        agreement = "✅" if expert_pick == our_pick else "❌"
        if expert_pick == our_pick:
            agreements += 1
        else:
            disagreements += 1
        
        print(f"{away} @ {home}")
        print(f"  Expert Pick: {expert_pick}")
        print(f"  DraftKings: {dk_spread}")
        print(f"  Our Pick: {our_pick} (Conf: {our_conf})")
        print(f"  Agreement: {agreement}")
        print()
    
    # Summary statistics
    agreement_rate = (agreements / total_games) * 100
    
    print("📈 Summary Statistics:")
    print("-" * 30)
    print(f"Total Games: {total_games}")
    print(f"Agreements: {agreements}")
    print(f"Disagreements: {disagreements}")
    print(f"Agreement Rate: {agreement_rate:.1f}%")
    
    # Key disagreements analysis
    print(f"\n🔍 Key Disagreements:")
    print("-" * 25)
    
    key_disagreements = [
        ("Indianapolis Colts @ Tennessee Titans", "Expert: Colts", "Our: Titans (Conf: 9)"),
        ("Pittsburgh Steelers @ New England Patriots", "Expert: Steelers", "Our: Patriots (Conf: 11)"),
        ("Atlanta Falcons @ Carolina Panthers", "Expert: Falcons", "Our: Panthers (Conf: 5)"),
        ("Green Bay Packers @ Cleveland Browns", "Expert: Packers", "Our: Browns (Conf: 8)"),
        ("Dallas Cowboys @ Chicago Bears", "Expert: Bears", "Our: Cowboys (Conf: 1)")
    ]
    
    for game, expert, our in key_disagreements:
        print(f"• {game}")
        print(f"  {expert} vs {our}")
        print()
    
    # Confidence analysis
    print(f"🎯 Confidence Analysis:")
    print("-" * 25)
    
    high_confidence_agreements = 0
    high_confidence_total = 0
    
    for away, home, expert_pick, dk_spread, our_pick, our_conf in odds_makers_data:
        if our_conf >= 10:  # High confidence (10+ points)
            high_confidence_total += 1
            if expert_pick == our_pick:
                high_confidence_agreements += 1
    
    if high_confidence_total > 0:
        high_conf_rate = (high_confidence_agreements / high_confidence_total) * 100
        print(f"High Confidence Picks (10+ pts): {high_confidence_agreements}/{high_confidence_total} ({high_conf_rate:.1f}%)")
    
    # Save comparison to file
    output_dir = "data/outputs/2025"
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    comparison_file = f"{output_dir}/week3-odds-makers-comparison.md"
    with open(comparison_file, 'w') as f:
        f.write("# Week 3 Picks: Our Model vs Odds Makers\n\n")
        f.write(f"**Analysis Date:** 2025-09-18\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Total Games**: {total_games}\n")
        f.write(f"- **Agreements**: {agreements}\n")
        f.write(f"- **Disagreements**: {disagreements}\n")
        f.write(f"- **Agreement Rate**: {agreement_rate:.1f}%\n\n")
        
        f.write("## Game-by-Game Comparison\n\n")
        f.write("| Game | Expert Pick | DraftKings | Our Pick | Our Conf | Agreement |\n")
        f.write("|------|-------------|------------|----------|----------|----------|\n")
        
        for away, home, expert_pick, dk_spread, our_pick, our_conf in odds_makers_data:
            agreement = "✅" if expert_pick == our_pick else "❌"
            f.write(f"| {away} @ {home} | {expert_pick} | {dk_spread} | {our_pick} | {our_conf} | {agreement} |\n")
        
        f.write(f"\n## Key Disagreements\n\n")
        for game, expert, our in key_disagreements:
            f.write(f"- **{game}**: {expert} vs {our}\n")
    
    print(f"\n💾 Saved comparison to: {comparison_file}")
    
    return {
        'total_games': total_games,
        'agreements': agreements,
        'disagreements': disagreements,
        'agreement_rate': agreement_rate
    }

if __name__ == "__main__":
    results = compare_with_odds_makers()
    print(f"\n🎯 Comparison Complete!")
    print(f"Agreement Rate: {results['agreement_rate']:.1f}%")
