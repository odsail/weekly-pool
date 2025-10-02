#!/usr/bin/env python3
"""
Analyze Week 5 Expert Picks from CBS Sports
Based on the provided image data
"""

import os
from datetime import datetime

def analyze_week5_expert_picks():
    """
    Analyze Week 5 expert picks from CBS Sports image data.
    """
    print("📊 **WEEK 5 EXPERT PICKS ANALYSIS**")
    print("=" * 50)
    
    # Expert data from the image
    experts = [
        {"name": "Pete Prisco", "title": "Senior Writer", "overall": "49-14-1"},
        {"name": "Cody Benjamin", "title": "Writer", "overall": "41-22-1"},
        {"name": "Jared Dubin", "title": "Writer", "overall": "41-22-1"},
        {"name": "Ryan Wilson", "title": "NFL Draft analyst", "overall": "46-17-1"},
        {"name": "John Breech", "title": "Writer", "overall": "45-18-1"},
        {"name": "Tyler Sullivan", "title": "Writer", "overall": "41-22-1"},
        {"name": "Dave Richard", "title": "Senior Fantasy Writer", "overall": "42-21-1"}
    ]
    
    # Week 5 games and expert picks from the image
    week5_games = [
        {
            "game": "San Francisco 49ers @ Los Angeles Rams",
            "time": "THU 8:15 pm",
            "records": "SF 3-1 vs LAR 3-1",
            "expert_picks": ["LAR", "LAR", "LAR", "LAR", "LAR", "LAR", "LAR"],
            "consensus": "7/7 (100%) - LAR",
            "risk_level": "UNIVERSAL"
        },
        {
            "game": "Minnesota Vikings @ Cleveland Browns",
            "time": "SUN 9:30 am",
            "records": "MIN 2-2 vs CLE 1-3",
            "expert_picks": ["MIN", "MIN", "MIN", "MIN", "CLE", "MIN", "MIN"],
            "consensus": "6/7 (85.7%) - MIN",
            "risk_level": "STRONG"
        },
        {
            "game": "Dallas Cowboys @ New York Jets",
            "time": "SUN 1:00 pm FOX",
            "records": "DAL 1-2-1 vs NYJ 0-4",
            "expert_picks": ["DAL", "DAL", "DAL", "DAL", "DAL", "DAL", "DAL"],
            "consensus": "7/7 (100%) - DAL",
            "risk_level": "UNIVERSAL"
        },
        {
            "game": "Denver Broncos @ Philadelphia Eagles",
            "time": "SUN 1:00 pm CBS",
            "records": "DEN 2-2 vs PHI 4-0",
            "expert_picks": ["PHI", "PHI", "PHI", "PHI", "PHI", "PHI", "PHI"],
            "consensus": "7/7 (100%) - PHI",
            "risk_level": "UNIVERSAL"
        },
        {
            "game": "Houston Texans @ Baltimore Ravens",
            "time": "SUN 1:00 pm CBS",
            "records": "HOU 1-3 vs BAL 1-3",
            "expert_picks": ["HOU", "HOU", "HOU", "HOU", "BAL", "HOU", "HOU"],
            "consensus": "6/7 (85.7%) - HOU",
            "risk_level": "STRONG"
        },
        {
            "game": "Las Vegas Raiders @ Indianapolis Colts",
            "time": "SUN 1:00 pm FOX",
            "records": "LV 1-3 vs IND 3-1",
            "expert_picks": ["IND", "IND", "IND", "IND", "IND", "IND", "IND"],
            "consensus": "7/7 (100%) - IND",
            "risk_level": "UNIVERSAL"
        },
        {
            "game": "Miami Dolphins @ Carolina Panthers",
            "time": "SUN 1:00 pm FOX",
            "records": "MIA 1-3 vs CAR 1-3",
            "expert_picks": ["MIA", "MIA", "MIA", "MIA", "MIA", "MIA", "MIA"],
            "consensus": "7/7 (100%) - MIA",
            "risk_level": "UNIVERSAL"
        },
        {
            "game": "New York Giants @ New Orleans Saints",
            "time": "SUN 1:00 pm CBS",
            "records": "NYG 1-3 vs NO 0-4",
            "expert_picks": ["NO", "NYG", "NYG", "NO", "NYG", "NO", "NYG"],
            "consensus": "4/7 (57.1%) - NYG",
            "risk_level": "SPLIT"
        },
        {
            "game": "Tampa Bay Buccaneers @ Seattle Seahawks",
            "time": "SUN 4:05 pm CBS",
            "records": "TB 3-1 vs SEA 3-1",
            "expert_picks": ["TB", "SEA", "SEA", "SEA", "SEA", "SEA", "SEA"],
            "consensus": "6/7 (85.7%) - SEA",
            "risk_level": "STRONG"
        },
        {
            "game": "Tennessee Titans @ Arizona Cardinals",
            "time": "SUN 4:05 pm CBS",
            "records": "TEN 0-4 vs ARI 2-2",
            "expert_picks": ["ARI", "ARI", "ARI", "ARI", "ARI", "ARI", "ARI"],
            "consensus": "7/7 (100%) - ARI",
            "risk_level": "UNIVERSAL"
        },
        {
            "game": "Detroit Lions @ Cincinnati Bengals",
            "time": "SUN 4:25 pm FOX",
            "records": "DET 3-1 vs CIN 2-2",
            "expert_picks": ["DET", "DET", "DET", "DET", "DET", "DET", "DET"],
            "consensus": "7/7 (100%) - DET",
            "risk_level": "UNIVERSAL"
        },
        {
            "game": "Washington Commanders @ Los Angeles Chargers",
            "time": "SUN 4:25 pm FOX",
            "records": "WAS 2-2 vs LAC 3-1",
            "expert_picks": ["LAC", "WAS", "LAC", "LAC", "LAC", "LAC", "LAC"],
            "consensus": "6/7 (85.7%) - LAC",
            "risk_level": "STRONG"
        },
        {
            "game": "New England Patriots @ Buffalo Bills",
            "time": "SUN 8:20 pm NBC",
            "records": "NE 2-2 vs BUF 4-0",
            "expert_picks": ["BUF", "BUF", "BUF", "BUF", "BUF", "BUF", "BUF"],
            "consensus": "7/7 (100%) - BUF",
            "risk_level": "UNIVERSAL"
        },
        {
            "game": "Kansas City Chiefs @ Jacksonville Jaguars",
            "time": "MON 8:15 pm ABC",
            "records": "KC 2-2 vs JAX 3-1",
            "expert_picks": ["JAX", "KC", "KC", "KC", "KC", "KC", "KC"],
            "consensus": "6/7 (85.7%) - KC",
            "risk_level": "STRONG"
        }
    ]
    
    # Analyze consensus patterns
    universal_consensus = [game for game in week5_games if game["risk_level"] == "UNIVERSAL"]
    strong_consensus = [game for game in week5_games if game["risk_level"] == "STRONG"]
    split_decisions = [game for game in week5_games if game["risk_level"] == "SPLIT"]
    
    print(f"📊 **CONSENSUS ANALYSIS**")
    print(f"Universal Consensus (7/7): {len(universal_consensus)} games")
    print(f"Strong Consensus (6/7): {len(strong_consensus)} games")
    print(f"Split Decisions (4-5/7): {len(split_decisions)} games")
    
    print(f"\n🚨 **UNIVERSAL CONSENSUS GAMES** (7/7 experts)")
    print("-" * 50)
    for game in universal_consensus:
        print(f"• {game['game']}: {game['consensus']}")
    
    print(f"\n⚠️ **STRONG CONSENSUS GAMES** (6/7 experts)")
    print("-" * 50)
    for game in strong_consensus:
        print(f"• {game['game']}: {game['consensus']}")
    
    print(f"\n💡 **SPLIT DECISION GAMES** (4-5/7 experts)")
    print("-" * 50)
    for game in split_decisions:
        print(f"• {game['game']}: {game['consensus']}")
    
    # Special analysis for Vikings
    vikings_game = next((game for game in week5_games if "Minnesota Vikings" in game["game"]), None)
    if vikings_game:
        print(f"\n🌍 **VIKINGS INTERNATIONAL GAME ANALYSIS**")
        print("-" * 50)
        print(f"Game: {vikings_game['game']}")
        print(f"Consensus: {vikings_game['consensus']}")
        print(f"Vikings Advantage: Acclimated to timezone from Week 4 international game")
        print(f"Browns Disadvantage: First international game, adjusting to timezone")
        print(f"Recommendation: Consider Vikings as stronger pick despite 6/7 expert consensus")
    
    return week5_games, experts

def create_week5_consensus_picks(week5_games, experts):
    """
    Create Week 5 consensus picks based on expert analysis.
    """
    print(f"\n🎯 **CREATING WEEK 5 CONSENSUS PICKS**")
    print("=" * 50)
    
    # Create output directory
    os.makedirs('data/outputs/2025', exist_ok=True)
    
    # Generate consensus picks with confidence points
    consensus_picks = []
    
    # Universal consensus games get highest confidence (16-10 points)
    universal_games = [game for game in week5_games if game["risk_level"] == "UNIVERSAL"]
    for i, game in enumerate(universal_games):
        pick = game["expert_picks"][0]  # All experts picked the same team
        confidence = 16 - i
        consensus_picks.append({
            "confidence": confidence,
            "pick": pick,
            "game": game["game"],
            "consensus": game["consensus"],
            "risk_level": "UNIVERSAL"
        })
    
    # Strong consensus games get medium confidence (9-6 points)
    strong_games = [game for game in week5_games if game["risk_level"] == "STRONG"]
    for i, game in enumerate(strong_games):
        # Determine the consensus pick
        pick_counts = {}
        for pick in game["expert_picks"]:
            pick_counts[pick] = pick_counts.get(pick, 0) + 1
        consensus_pick = max(pick_counts, key=pick_counts.get)
        
        confidence = 9 - i
        consensus_picks.append({
            "confidence": confidence,
            "pick": consensus_pick,
            "game": game["game"],
            "consensus": game["consensus"],
            "risk_level": "STRONG"
        })
    
    # Split decision games get lowest confidence (5-1 points)
    split_games = [game for game in week5_games if game["risk_level"] == "SPLIT"]
    for i, game in enumerate(split_games):
        # Determine the consensus pick
        pick_counts = {}
        for pick in game["expert_picks"]:
            pick_counts[pick] = pick_counts.get(pick, 0) + 1
        consensus_pick = max(pick_counts, key=pick_counts.get)
        
        confidence = 5 - i
        consensus_picks.append({
            "confidence": confidence,
            "pick": consensus_pick,
            "game": game["game"],
            "consensus": game["consensus"],
            "risk_level": "SPLIT"
        })
    
    # Sort by confidence points
    consensus_picks.sort(key=lambda x: x["confidence"], reverse=True)
    
    return consensus_picks

def save_week5_consensus_picks(consensus_picks, experts):
    """
    Save Week 5 consensus picks to markdown file.
    """
    print(f"\n💾 **SAVING WEEK 5 CONSENSUS PICKS**")
    print("=" * 50)
    
    # Create markdown content
    markdown_content = f"""# Week 5 NFL Confidence Picks - Expert Consensus

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Command Used:** `python analyze_week5_expert_picks.py`  
**Strategy:** Expert consensus for straight-up winners  
**Data Source:** CBS Sports expert picks (7 experts)

## Methodology

This week's picks are based on CBS Sports expert straight-up winner consensus. The approach prioritizes current expert opinion and incorporates special factors like international games.

**IMPORTANT:** We are picking the **straight-up winner** of each game, NOT covering the point spread.

### Expert Consensus Calculation:
- **7/7 experts (100%)**: Win probability 0.85 (16-10 points)
- **6/7 experts (85.7%)**: Win probability 0.75-0.85 (9-6 points)
- **4-5/7 experts (57.1-71.4%)**: Win probability 0.55-0.65 (5-1 points)

## Week 5 Expert Consensus Picks

| Points | Pick | Consensus | Game | Risk Level |
|--------|------|-----------|------|------------|
"""
    
    for pick in consensus_picks:
        risk_emoji = "🚨" if pick['risk_level'] == 'UNIVERSAL' else "⚠️" if pick['risk_level'] == 'STRONG' else "💡"
        markdown_content += f"| {pick['confidence']} | {pick['pick']} | {pick['consensus']} | {pick['game']} | {risk_emoji} {pick['risk_level']} |\n"
    
    markdown_content += f"""
## Key Insights

### Universal Consensus Games (7/7 experts):
"""
    
    universal_picks = [pick for pick in consensus_picks if pick['risk_level'] == 'UNIVERSAL']
    for pick in universal_picks:
        markdown_content += f"- **{pick['game']}**: {pick['consensus']} - {pick['pick']}\n"
    
    markdown_content += f"""
### Strong Consensus Games (6/7 experts):
"""
    
    strong_picks = [pick for pick in consensus_picks if pick['risk_level'] == 'STRONG']
    for pick in strong_picks:
        markdown_content += f"- **{pick['game']}**: {pick['consensus']} - {pick['pick']}\n"
    
    markdown_content += f"""
### Split Decision Games (4-5/7 experts):
"""
    
    split_picks = [pick for pick in consensus_picks if pick['risk_level'] == 'SPLIT']
    for pick in split_picks:
        markdown_content += f"- **{pick['game']}**: {pick['consensus']} - {pick['pick']}\n"
    
    markdown_content += f"""
## Special Factors

### 🌍 International Game - Vikings Advantage:
- **Minnesota Vikings @ Cleveland Browns**: Vikings have acclimation advantage from Week 4 international game
- **Browns Disadvantage**: First international game, adjusting to timezone
- **Recommendation**: Consider Vikings as stronger pick despite 6/7 expert consensus

### 📊 Expert Performance:
"""
    
    for expert in experts:
        markdown_content += f"- **{expert['name']}** ({expert['title']}): {expert['overall']}\n"
    
    markdown_content += f"""
## Contrarian Opportunities

Based on historical consensus failure analysis, consider these contrarian opportunities:

### Universal Consensus Fades (Highest Risk/Reward):
"""
    
    for pick in universal_picks:
        markdown_content += f"- **{pick['game']}**: Fade {pick['pick']} (7/7 experts)\n"
    
    markdown_content += f"""
### Strong Consensus Fades (Medium Risk/Reward):
"""
    
    for pick in strong_picks:
        markdown_content += f"- **{pick['game']}**: Fade {pick['pick']} (6/7 experts)\n"
    
    markdown_content += f"""
## Notes

- **Monday Night Game**: Kansas City Chiefs @ Jacksonville Jaguars
- **Vikings International Advantage**: Consider stronger pick due to timezone acclimation
- **Universal Consensus Alert**: {len(universal_picks)} games have 7/7 expert consensus

---
*Generated using expert consensus methodology*
"""
    
    # Save to file
    output_file = 'data/outputs/2025/week-week5-expert-consensus.md'
    with open(output_file, 'w') as f:
        f.write(markdown_content)
    
    print(f"✅ Week 5 consensus picks saved: {output_file}")
    
    return output_file

def main():
    print("📊 **WEEK 5 EXPERT PICKS ANALYSIS**")
    print("=" * 50)
    
    # Analyze expert picks
    week5_games, experts = analyze_week5_expert_picks()
    
    # Create consensus picks
    consensus_picks = create_week5_consensus_picks(week5_games, experts)
    
    # Save to file
    output_file = save_week5_consensus_picks(consensus_picks, experts)
    
    print(f"\n✅ **WEEK 5 ANALYSIS COMPLETE**")
    print("=" * 40)
    print(f"📊 {len(week5_games)} games analyzed")
    print(f"🎯 {len(consensus_picks)} consensus picks created")
    print(f"🌍 Vikings international advantage identified")
    print(f"📄 Output saved: {output_file}")
    
    print(f"\n📋 **COMMAND USED:**")
    print("```bash")
    print("python analyze_week5_expert_picks.py")
    print("```")

if __name__ == "__main__":
    main()
