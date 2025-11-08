#!/usr/bin/env python3
"""
Scrape CBS Sports expert picks for a given week - Version 3 with odds
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import argparse

def scrape_cbs_expert_picks_with_odds(week):
    """
    Scrape CBS Sports expert picks with betting odds for the specified week
    """
    url = f"https://www.cbssports.com/nfl/picks/experts/straight-up/{week}/"
    
    print(f"🔍 Scraping CBS Sports expert picks with odds for Week {week}...")
    print(f"📡 URL: {url}")
    
    try:
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the main table
        table = soup.find('table')
        if not table:
            print("❌ No table found")
            return []
        
        rows = table.find_all('tr')
        print(f"📊 Found {len(rows)} table rows")
        
        expert_picks = []
        expert_names = ['Pete Prisco', 'Cody Benjamin', 'Jared Dubin', 'Ryan Wilson', 'John Breech', 'Tyler Sullivan', 'Dave Richard']
        
        # Skip header rows (first 2 rows are expert names and records)
        for i, row in enumerate(rows[2:], start=3):
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 9:  # Should have game info + 7 expert columns
                try:
                    # Extract game information from first cell
                    game_cell = cells[0]
                    game_text = game_cell.get_text(strip=True)
                    
                    # Parse game info (e.g., "8:15 pmSF3-1LAR3-1Preview")
                    # Extract team abbreviations and records
                    team_matches = re.findall(r'([A-Z]{2,4})\d+-\d+', game_text)
                    if len(team_matches) >= 2:
                        away_team = team_matches[0]
                        home_team = team_matches[1]
                        
                        # Extract expert picks and odds from remaining cells (cells 1-7)
                        expert_picks_for_game = []
                        odds_data = {}
                        
                        for j, cell in enumerate(cells[1:8]):  # Skip first cell (game info)
                            if j < len(expert_names):
                                cell_text = cell.get_text(strip=True)
                                
                                # Look for team abbreviation and odds in the cell
                                # Pattern like "LAR-365Remove" or "KC-181Remove"
                                team_odds_match = re.search(r'^([A-Z]{2,4})([+-]\d{3,4})', cell_text)
                                if team_odds_match:
                                    picked_team = team_odds_match.group(1)
                                    odds = team_odds_match.group(2)
                                    
                                    expert_picks_for_game.append({
                                        'expert': expert_names[j],
                                        'pick': picked_team,
                                        'odds': odds
                                    })
                                    
                                    # Store odds for each team
                                    if picked_team not in odds_data:
                                        odds_data[picked_team] = odds
                        
                        if expert_picks_for_game:
                            expert_picks.append({
                                'game': f"{away_team} @ {home_team}",
                                'away_team': away_team,
                                'home_team': home_team,
                                'expert_picks': expert_picks_for_game,
                                'odds': odds_data
                            })
                            
                            print(f"  ✅ {away_team} @ {home_team}: {len(expert_picks_for_game)} expert picks")
                            print(f"     Odds: {odds_data}")
                                
                except Exception as e:
                    print(f"  ⚠️  Error parsing row {i}: {e}")
                    continue
        
        print(f"✅ Successfully scraped {len(expert_picks)} games with odds")
        
        return expert_picks
        
    except Exception as e:
        print(f"❌ Error scraping CBS Sports: {e}")
        return []

def save_expert_picks_to_json(expert_picks, week):
    """
    Save expert picks with odds to JSON file
    """
    output_file = f"data/expert-picks-week-{week}-with-odds.json"
    
    # Create data directory if it doesn't exist
    import os
    os.makedirs('data', exist_ok=True)
    
    # Prepare data for JSON
    json_data = {
        'week': week,
        'season': 2025,
        'scraped_at': datetime.now().isoformat(),
        'source': 'CBS Sports',
        'url': f"https://www.cbssports.com/nfl/picks/experts/straight-up/{week}/",
        'games': expert_picks
    }
    
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"💾 Saved expert picks with odds to: {output_file}")
    return output_file

def main():
    parser = argparse.ArgumentParser(description="Scrape CBS Sports expert picks with odds")
    parser.add_argument("--week", type=int, required=True, help="Week number")
    
    args = parser.parse_args()
    
    # Scrape expert picks with odds
    expert_picks = scrape_cbs_expert_picks_with_odds(args.week)
    
    if expert_picks:
        # Save to JSON
        output_file = save_expert_picks_to_json(expert_picks, args.week)
        
        print(f"\n✅ **SCRAPING COMPLETE**")
        print(f"📊 Found {len(expert_picks)} games")
        print(f"📄 Output: {output_file}")
        
        # Show sample of data with odds
        print(f"\n📋 **SAMPLE DATA WITH ODDS:**")
        for i, game in enumerate(expert_picks[:2]):  # Show first 2 games
            print(f"Game {i+1}: {game['game']}")
            print(f"  Odds: {game['odds']}")
            for pick in game['expert_picks']:
                print(f"  {pick['expert']}: {pick['pick']} ({pick['odds']})")
    else:
        print("❌ No expert picks found")

if __name__ == "__main__":
    main()









