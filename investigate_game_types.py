#!/usr/bin/env python3
"""
Investigate ESPN API game structure to distinguish preseason vs regular season games.
"""

import requests
import json

def investigate_game_structure():
    """Investigate game structure to find preseason vs regular season indicators"""
    
    base_url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl'
    
    # Get a sample game from different time periods
    test_dates = [
        ('20240801', 'Preseason'),
        ('20240825', 'Possible Week 1'),
        ('20240908', 'Known Week 1'),
    ]
    
    for date, label in test_dates:
        print(f'\n{label} ({date}):')
        
        url = f'{base_url}/scoreboard'
        params = {'dates': date}
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                
                if events:
                    # Get the first event and examine its full structure
                    event = events[0]
                    print(f'  Sample game: {event.get("name", "Unknown")}')
                    
                    # Check all top-level fields
                    print('  Top-level fields:')
                    for key in event.keys():
                        value = event[key]
                        if isinstance(value, (str, int, bool)):
                            print(f'    {key}: {value}')
                        elif isinstance(value, list) and len(value) > 0:
                            print(f'    {key}: [list with {len(value)} items]')
                        elif isinstance(value, dict):
                            print(f'    {key}: [dict with keys: {list(value.keys())}]')
                    
                    # Check competitions structure in detail
                    competitions = event.get('competitions', [])
                    if competitions:
                        comp = competitions[0]
                        print('\n  Competition structure:')
                        for key in comp.keys():
                            value = comp[key]
                            if isinstance(value, (str, int, bool)):
                                print(f'    {key}: {value}')
                            elif isinstance(value, dict):
                                print(f'    {key}: [dict with keys: {list(value.keys())}]')
                            else:
                                print(f'    {key}: {type(value).__name__}')
                    break
        except Exception as e:
            print(f'  Error: {e}')

def analyze_season_patterns():
    """Analyze patterns to identify when regular season starts"""
    
    print('\n🔍 Analyzing season patterns to identify regular season start...')
    
    base_url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl'
    
    # Check a range of dates in August/September 2024
    dates_to_check = []
    for day in range(1, 32):  # August 1-31
        dates_to_check.append(f'202408{day:02d}')
    for day in range(1, 16):  # September 1-15
        dates_to_check.append(f'202409{day:02d}')
    
    game_counts = []
    
    for date in dates_to_check:
        url = f'{base_url}/scoreboard'
        params = {'dates': date}
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                
                if events:
                    # Count NFL games (not other sports)
                    nfl_games = 0
                    for event in events:
                        name = event.get('name', '')
                        # Simple check for NFL games
                        if any(team in name for team in ['Chiefs', 'Patriots', 'Cowboys', 'Packers', 'Steelers']):
                            nfl_games += 1
                    
                    if nfl_games > 0:
                        game_counts.append((date, nfl_games))
                        print(f'  {date}: {nfl_games} NFL games')
        except Exception as e:
            continue
    
    # Find the pattern
    print('\n📊 Game count pattern:')
    for date, count in game_counts:
        print(f'  {date}: {count} games')
    
    # Identify when regular season likely starts (sudden jump in game count)
    if len(game_counts) > 1:
        for i in range(1, len(game_counts)):
            prev_count = game_counts[i-1][1]
            curr_count = game_counts[i][1]
            if curr_count > prev_count * 2:  # Significant jump
                print(f'\n🎯 Regular season likely starts around {game_counts[i][0]} (jump from {prev_count} to {curr_count} games)')

if __name__ == '__main__':
    investigate_game_structure()
    analyze_season_patterns()






