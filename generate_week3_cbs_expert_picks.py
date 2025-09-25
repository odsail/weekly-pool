#!/usr/bin/env python3
"""
Generate Week 3 picks incorporating CBS Sports expert consensus
This combines our original odds logic with expert picks for better accuracy
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

def american_to_implied_prob(odds: int) -> float:
    """Convert American odds to implied probability (0..1), without removing vig."""
    if odds is None:
        return None
    try:
        odds = int(odds)
    except (ValueError, TypeError):
        return None
    if odds > 0:
        return 100.0 / (odds + 100.0)
    else:
        return -odds / (-odds + 100.0)

def devig_two_way(p1: float, p2: float) -> Tuple[Optional[float], Optional[float]]:
    """Normalize two implied probs to sum to 1 (simple de-vig)."""
    if p1 is None or p2 is None:
        return None, None
    s = p1 + p2
    if s <= 0:
        return None, None
    return p1 / s, p2 / s

def assign_confidence_points(df: pd.DataFrame, pool_size: Optional[int] = None) -> pd.DataFrame:
    """Assign confidence points based on combined odds + expert consensus"""
    df = df.copy()
    df = df.sort_values(by=["combined_confidence", "commence_time"], ascending=[False, True]).reset_index(drop=True)
    
    num_games = len(df)
    if pool_size is None:
        n = num_games
        print(f"Auto-detected pool size: {n} games")
    else:
        n = min(pool_size, num_games)
        if pool_size > num_games:
            print(f"Warning: Requested {pool_size} points but only {num_games} games available. Using {n} points.")
    
    df["confidence_points"] = list(range(n, n - len(df), -1))
    return df

def get_cbs_expert_consensus():
    """Get CBS Sports expert picks for Week 3"""
    
    # CBS Sports expert picks (from the images provided)
    expert_picks = {
        # Game: (away_team, home_team, expert_consensus_pick, consensus_strength, spread_pick)
        "MIA @ BUF": ("Miami Dolphins", "Buffalo Bills", "Buffalo Bills", 7, "BUF -12.5"),
        "CAR @ ATL": ("Carolina Panthers", "Atlanta Falcons", "Atlanta Falcons", 5, "ATL -5.5"), 
        "CIN @ MIN": ("Cincinnati Bengals", "Minnesota Vikings", "Minnesota Vikings", 5, "MIN -3"),
        "GB @ CLE": ("Green Bay Packers", "Cleveland Browns", "Green Bay Packers", 6, "GB -8.5"),
        "HOU @ JAX": ("Houston Texans", "Jacksonville Jaguars", "Jacksonville Jaguars", 4, "JAX -1.5"),
        "IND @ TEN": ("Indianapolis Colts", "Tennessee Titans", "Indianapolis Colts", 5, "IND -3.5"),
        "LAR @ PHI": ("Los Angeles Rams", "Philadelphia Eagles", "Philadelphia Eagles", 5, "PHI -3.5"),
        "LV @ WAS": ("Las Vegas Raiders", "Washington Commanders", "Washington Commanders", 5, "WAS -3.5"),
        "NYJ @ TB": ("New York Jets", "Tampa Bay Buccaneers", "Tampa Bay Buccaneers", 6, "TB -7"),
        "PIT @ NE": ("Pittsburgh Steelers", "New England Patriots", "Pittsburgh Steelers", 5, "PIT -1.5"),
        "DEN @ LAC": ("Denver Broncos", "Los Angeles Chargers", "Los Angeles Chargers", 7, "LAC -2.5"),
        "NO @ SEA": ("New Orleans Saints", "Seattle Seahawks", "Seattle Seahawks", 5, "SEA -7.5"),
        "ARI @ SF": ("Arizona Cardinals", "San Francisco 49ers", "San Francisco 49ers", 6, "SF -1.5"),
        "DAL @ CHI": ("Dallas Cowboys", "Chicago Bears", "Dallas Cowboys", 5, "DAL +1.5"),
        "KC @ NYG": ("Kansas City Chiefs", "New York Giants", "Kansas City Chiefs", 4, "KC -6"),
        "DET @ BAL": ("Detroit Lions", "Baltimore Ravens", "Baltimore Ravens", 4, "BAL -5.5")
    }
    
    return expert_picks

def calculate_expert_boost(consensus_strength: int, total_experts: int = 7) -> float:
    """Calculate confidence boost based on expert consensus strength"""
    # Convert consensus strength to a multiplier (1.0 to 1.3)
    consensus_ratio = consensus_strength / total_experts
    return 1.0 + (consensus_ratio * 0.3)

def generate_cbs_expert_week3_picks():
    """Generate Week 3 picks incorporating CBS Sports expert consensus"""
    
    print("🎯 Generating Week 3 Picks - CBS EXPERT ENHANCED")
    print("=" * 50)
    
    # Get expert picks
    expert_picks = get_cbs_expert_consensus()
    
    # Realistic odds data (same as original)
    realistic_odds_data = [
        # (away_team, home_team, away_ml, home_ml, total_points, commence_time)
        ("Miami Dolphins", "Buffalo Bills", 450, -600, 46, "2025-09-19T17:00:00Z"),
        ("Green Bay Packers", "Cleveland Browns", 180, -220, 42, "2025-09-21T17:00:00Z"),
        ("Indianapolis Colts", "Tennessee Titans", 110, -130, 44, "2025-09-21T17:00:00Z"),
        ("Cincinnati Bengals", "Minnesota Vikings", 120, -140, 45, "2025-09-21T17:00:00Z"),
        ("Pittsburgh Steelers", "New England Patriots", 105, -125, 43, "2025-09-21T17:00:00Z"),
        ("Los Angeles Rams", "Philadelphia Eagles", 130, -150, 47, "2025-09-21T17:00:00Z"),
        ("New York Jets", "Tampa Bay Buccaneers", 200, -250, 44, "2025-09-21T17:00:00Z"),
        ("Las Vegas Raiders", "Washington Commanders", 140, -165, 43, "2025-09-21T17:00:00Z"),
        ("Atlanta Falcons", "Carolina Panthers", 110, -130, 42, "2025-09-21T17:00:00Z"),
        ("Houston Texans", "Jacksonville Jaguars", 105, -125, 46, "2025-09-21T17:00:00Z"),
        ("Denver Broncos", "Los Angeles Chargers", 120, -140, 45, "2025-09-21T17:00:00Z"),
        ("New Orleans Saints", "Seattle Seahawks", 130, -150, 44, "2025-09-21T17:00:00Z"),
        ("Arizona Cardinals", "San Francisco 49ers", 180, -220, 46, "2025-09-21T17:00:00Z"),
        ("Dallas Cowboys", "Chicago Bears", 110, -130, 43, "2025-09-21T17:00:00Z"),
        ("Kansas City Chiefs", "New York Giants", 160, -190, 48, "2025-09-22T17:00:00Z"),
        ("Detroit Lions", "Baltimore Ravens", 150, -175, 45, "2025-09-23T17:00:00Z")
    ]
    
    # Convert to DataFrame
    df = pd.DataFrame(realistic_odds_data, columns=[
        'away_team', 'home_team', 'away_ml', 'home_ml', 'total_points', 'commence_time'
    ])
    
    # Add event_id and bookmaker
    df['event_id'] = [f"event_{i}" for i in range(len(df))]
    df['bookmaker'] = 'DraftKings'
    
    print(f"📊 Processing {len(df)} games with CBS expert enhancement...")
    
    # Process odds to get base probabilities
    df["away_implied_raw"] = df["away_ml"].apply(american_to_implied_prob)
    df["home_implied_raw"] = df["home_ml"].apply(american_to_implied_prob)
    
    dev = df.apply(lambda r: devig_two_way(r["away_implied_raw"], r["home_implied_raw"]), axis=1)
    df["away_prob"] = [t[0] if t else None for t in dev]
    df["home_prob"] = [t[1] if t else None for t in dev]
    
    # Apply expert consensus enhancement
    expert_enhanced_picks = []
    expert_consensus_strength = []
    expert_pick_method = []
    
    for _, row in df.iterrows():
        # Create game key for expert lookup
        game_key = f"{row['away_team']} @ {row['home_team']}"
        
        # Find matching expert pick
        expert_data = None
        for key, data in expert_picks.items():
            if (data[0] == row['away_team'] and data[1] == row['home_team']) or \
               (data[0] == row['home_team'] and data[1] == row['away_team']):
                expert_data = data
                break
        
        if expert_data:
            expert_pick = expert_data[2]
            consensus_strength = expert_data[3]
            spread_pick = expert_data[4]
            
            # Determine if expert agrees with odds-based pick
            odds_pick = row['home_team'] if (row['home_prob'] or 0) >= (row['away_prob'] or 0) else row['away_team']
            
            if expert_pick == odds_pick:
                # Expert agrees with odds - boost confidence
                expert_boost = calculate_expert_boost(consensus_strength)
                final_pick = expert_pick
                method = f"odds+expert ({consensus_strength}/7)"
            else:
                # Expert disagrees - use expert pick with moderate confidence
                expert_boost = 1.0 + (consensus_strength / 7 * 0.2)  # Smaller boost for disagreement
                final_pick = expert_pick
                method = f"expert override ({consensus_strength}/7)"
            
            # Calculate final confidence
            base_prob = row['home_prob'] if final_pick == row['home_team'] else row['away_prob']
            final_confidence = (base_prob or 0.5) * expert_boost
            
        else:
            # No expert data - use original odds
            final_pick = row['home_team'] if (row['home_prob'] or 0) >= (row['away_prob'] or 0) else row['away_team']
            final_confidence = max(row['home_prob'] or 0, row['away_prob'] or 0)
            method = "odds only"
            consensus_strength = 0
        
        expert_enhanced_picks.append(final_pick)
        expert_consensus_strength.append(consensus_strength)
        expert_pick_method.append(method)
    
    # Add enhanced data to DataFrame
    df["pick_team"] = expert_enhanced_picks
    df["expert_consensus_strength"] = expert_consensus_strength
    df["pick_method"] = expert_pick_method
    df["combined_confidence"] = df.apply(lambda r: max(r["home_prob"] or 0, r["away_prob"] or 0) * 
                                       (1.0 + (r["expert_consensus_strength"] / 7 * 0.3)), axis=1)
    
    # Assign confidence points
    df = assign_confidence_points(df)
    
    # Display results
    print(f"\n🎯 Week 3 Picks (CBS Expert Enhanced):")
    print("-" * 50)
    
    for _, row in df.sort_values('confidence_points', ascending=False).iterrows():
        print(f"{row['confidence_points']:2d} pts: {row['pick_team']} ({row['combined_confidence']*100:.1f}%) - {row['pick_method']}")
        print(f"     {row['away_team']} @ {row['home_team']}")
    
    # Save to files
    output_dir = "data/outputs/2025"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create CSV file
    csv_file = f"{output_dir}/week-week3-cbs-expert-picks.csv"
    df.to_csv(csv_file, index=False)
    print(f"\n💾 Saved CSV: {csv_file}")
    
    # Create markdown file
    md_file = f"{output_dir}/week-week3-cbs-expert-picks.md"
    with open(md_file, 'w') as f:
        f.write("# Week 3 Picks - CBS EXPERT ENHANCED\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Picks (Combining Odds + CBS Expert Consensus)\n\n")
        f.write("| Points | Pick | Confidence | Method | Home | Away | Odds |\n")
        f.write("|--------|------|------------|--------|------|------|------|\n")
        
        for _, row in df.sort_values('confidence_points', ascending=False).iterrows():
            f.write(f"| {row['confidence_points']:2d} | {row['pick_team']} | {row['combined_confidence']*100:5.1f}% | {row['pick_method']} | {row['home_team']} | {row['away_team']} | {row['home_ml']}/{row['away_ml']} |\n")
        
        f.write(f"\n## Expert Consensus Summary\n")
        expert_agreements = len([m for m in df['pick_method'] if 'odds+expert' in m])
        expert_overrides = len([m for m in df['pick_method'] if 'expert override' in m])
        odds_only = len([m for m in df['pick_method'] if 'odds only' in m])
        
        f.write(f"- **Expert Agreements**: {expert_agreements} games\n")
        f.write(f"- **Expert Overrides**: {expert_overrides} games\n")
        f.write(f"- **Odds Only**: {odds_only} games\n")
        f.write(f"- **Total Games**: {len(df)}\n")
        f.write(f"- **Total Confidence Points**: {sum(df['confidence_points'])}\n")
        f.write(f"- **Method**: CBS Expert Consensus + Original Odds Logic\n")
        f.write(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"💾 Saved Markdown: {md_file}")
    
    return df

if __name__ == "__main__":
    import os
    generate_cbs_expert_week3_picks()


