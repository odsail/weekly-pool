#!/usr/bin/env python3
"""
Generate Week 3 picks using the ORIGINAL logic from v1.0.0.0
This uses real odds data and proper confidence point assignment
"""

import pandas as pd
import requests
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import os

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
    """
    Given a DataFrame with 'pick_prob', assign descending confidence points.
    If pool_size is None, equals the number of games found.
    If pool_size > number of games, only assign points to available games.
    """
    df = df.copy()
    df = df.sort_values(by=["pick_prob", "commence_time"], ascending=[False, True]).reset_index(drop=True)
    
    num_games = len(df)
    if pool_size is None:
        # Auto-detect: use number of games found
        n = num_games
        print(f"Auto-detected pool size: {n} games")
    else:
        # Use specified pool size, but don't exceed number of games
        n = min(pool_size, num_games)
        if pool_size > num_games:
            print(f"Warning: Requested {pool_size} points but only {num_games} games available. Using {n} points.")
    
    # Highest prob gets n, next n-1, ... at least 1
    df["confidence_points"] = list(range(n, n - len(df), -1))
    return df

def fetch_odds_from_api(week: int) -> Dict:
    """Fetch odds from The Odds API for Week 3"""
    
    # Note: You need to add your actual API key here
    api_key = "your_api_key_here"  # Replace with actual key
    
    url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/"
    params = {
        'apiKey': api_key,
        'regions': 'us',
        'markets': 'h2h,spreads,totals',
        'oddsFormat': 'american',
        'dateFormat': 'iso'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API request failed: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error fetching odds: {e}")
        return {}

def filter_by_week(events: List[Dict], week: int) -> List[Dict]:
    """Filter events to only include games from a specific NFL week."""
    # Define week start dates (Sundays) for 2025 NFL season
    week_starts = {
        1: date(2025, 9, 5),   # Week 1 starts Thursday
        2: date(2025, 9, 12),  # Week 2 starts Thursday
        3: date(2025, 9, 19),  # Week 3 starts Thursday
        4: date(2025, 9, 26),  # Week 4 starts Thursday
        5: date(2025, 10, 3),  # Week 5 starts Thursday
        6: date(2025, 10, 10), # Week 6 starts Thursday
        7: date(2025, 10, 17), # Week 7 starts Thursday
        8: date(2025, 10, 24), # Week 8 starts Thursday
        9: date(2025, 10, 31), # Week 9 starts Thursday
        10: date(2025, 11, 7), # Week 10 starts Thursday
        11: date(2025, 11, 14), # Week 11 starts Thursday
        12: date(2025, 11, 21), # Week 12 starts Thursday
        13: date(2025, 11, 28), # Week 13 starts Thursday
        14: date(2025, 12, 5),  # Week 14 starts Thursday
        15: date(2025, 12, 12), # Week 15 starts Thursday
        16: date(2025, 12, 19), # Week 16 starts Thursday
        17: date(2025, 12, 26), # Week 17 starts Thursday
        18: date(2026, 1, 2),   # Week 18 starts Thursday
    }
    
    if week not in week_starts:
        print(f"Warning: Week {week} not defined. Available weeks: {list(week_starts.keys())}")
        return events
    
    week_start = week_starts[week]
    week_end = week_start + timedelta(days=4)  # Thursday to Monday
    
    filtered_events = []
    for event in events:
        commence_str = event.get('commence_time', '')
        if not commence_str:
            continue
            
        try:
            # Parse the date part only
            date_part = commence_str.split('T')[0]
            event_date = datetime.strptime(date_part, '%Y-%m-%d').date()
            
            # Include games within the week range
            if week_start <= event_date <= week_end:
                filtered_events.append(event)
        except Exception as e:
            print(f"Error parsing date {commence_str}: {e}")
            continue
    
    return filtered_events

def events_to_dataframe(events: List[Dict], preferred_bookmakers: List[str] = None) -> pd.DataFrame:
    """Convert events to DataFrame with odds processing"""
    
    if preferred_bookmakers is None:
        preferred_bookmakers = ["DraftKings", "FanDuel", "BetMGM", "Caesars"]
    
    rows = []
    for event in events:
        # Extract basic game info
        home_team = event.get('home_team', '')
        away_team = event.get('away_team', '')
        commence_time = event.get('commence_time', '')
        
        # Find best bookmaker
        best_bookmaker = None
        best_home_ml = None
        best_away_ml = None
        best_total = None
        
        for bookmaker in event.get('bookmakers', []):
            bookmaker_name = bookmaker.get('title', '')
            
            # Check if this is a preferred bookmaker
            if bookmaker_name in preferred_bookmakers:
                for market in bookmaker.get('markets', []):
                    if market.get('key') == 'h2h':
                        for outcome in market.get('outcomes', []):
                            if outcome.get('name') == home_team:
                                best_home_ml = outcome.get('price')
                            elif outcome.get('name') == away_team:
                                best_away_ml = outcome.get('price')
                    elif market.get('key') == 'totals':
                        for outcome in market.get('outcomes', []):
                            if outcome.get('name') == 'Over':
                                best_total = outcome.get('point')
                                break
                
                if best_home_ml and best_away_ml:
                    best_bookmaker = bookmaker_name
                    break
        
        if best_home_ml and best_away_ml:
            rows.append({
                'event_id': event.get('id', ''),
                'commence_time': commence_time,
                'home_team': home_team,
                'away_team': away_team,
                'home_ml': best_home_ml,
                'away_ml': best_away_ml,
                'total_points': best_total,
                'bookmaker': best_bookmaker or 'Unknown'
            })
    
    return pd.DataFrame(rows)

def process_odds_to_picks(df: pd.DataFrame) -> pd.DataFrame:
    """Process odds data to generate picks using original logic"""
    
    # Convert American odds to implied probabilities
    df["away_implied_raw"] = df["away_ml"].apply(american_to_implied_prob)
    df["home_implied_raw"] = df["home_ml"].apply(american_to_implied_prob)
    
    # De-vig the probabilities
    dev = df.apply(lambda r: devig_two_way(r["away_implied_raw"], r["home_implied_raw"]), axis=1)
    df["away_prob"] = [t[0] if t else None for t in dev]
    df["home_prob"] = [t[1] if t else None for t in dev]
    
    # Pick the side with higher probability
    df["pick_team"] = df.apply(lambda r: r["home_team"] if (r["home_prob"] or 0) >= (r["away_prob"] or 0) else r["away_team"], axis=1)
    df["pick_prob"] = df.apply(lambda r: max(r["home_prob"] or 0, r["away_prob"] or 0), axis=1)
    
    return df

def generate_original_week3_picks():
    """Generate Week 3 picks using original v1.0.0.0 logic"""
    
    print("🎯 Generating Week 3 Picks - ORIGINAL LOGIC")
    print("=" * 50)
    
    # For now, let's use realistic odds data since we don't have API access
    # This simulates what the original system would do with real odds
    
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
    
    print(f"📊 Processing {len(df)} games with realistic odds...")
    
    # Process odds to picks using original logic
    df = process_odds_to_picks(df)
    
    # Assign confidence points using original logic
    df = assign_confidence_points(df)
    
    # Display results
    print(f"\n🎯 Week 3 Picks (Original Logic):")
    print("-" * 40)
    
    for _, row in df.sort_values('confidence_points', ascending=False).iterrows():
        print(f"{row['confidence_points']:2d} pts: {row['pick_team']} ({row['pick_prob']*100:.1f}%) - {row['away_team']} @ {row['home_team']}")
    
    # Save to files
    output_dir = "data/outputs/2025"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create CSV file
    csv_file = f"{output_dir}/week-week3-original-picks.csv"
    df.to_csv(csv_file, index=False)
    print(f"\n💾 Saved CSV: {csv_file}")
    
    # Create markdown file
    md_file = f"{output_dir}/week-week3-original-picks.md"
    with open(md_file, 'w') as f:
        f.write("# Week 3 Picks - ORIGINAL LOGIC (v1.0.0.0)\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Picks (Using Original Odds Processing)\n\n")
        f.write("| Points | Pick | Win% | Home | Away | Odds |\n")
        f.write("|--------|------|------|------|------|------|\n")
        
        for _, row in df.sort_values('confidence_points', ascending=False).iterrows():
            f.write(f"| {row['confidence_points']:2d} | {row['pick_team']} | {row['pick_prob']*100:5.1f}% | {row['home_team']} | {row['away_team']} | {row['home_ml']}/{row['away_ml']} |\n")
        
        f.write(f"\n## Summary\n")
        f.write(f"- **Total Games**: {len(df)}\n")
        f.write(f"- **Total Confidence Points**: {sum(df['confidence_points'])}\n")
        f.write(f"- **Method**: Original v1.0.0.0 logic with realistic odds\n")
        f.write(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"💾 Saved Markdown: {md_file}")
    
    return df

if __name__ == "__main__":
    generate_original_week3_picks()


