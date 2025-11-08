#!/usr/bin/env python3
"""
Test CBS Sports scraper to understand the HTML structure
"""

import requests
from bs4 import BeautifulSoup
import re

def test_cbs_structure():
    """
    Test the CBS Sports page structure
    """
    url = "https://www.cbssports.com/nfl/picks/experts/straight-up/5/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 Analyzing CBS Sports page structure...")
        
        # Look for tables
        tables = soup.find_all('table')
        print(f"📊 Found {len(tables)} tables")
        
        # Look for specific patterns from the web search results
        # The data shows team logos and picks like "team logoDET3-1team logoCIN2-2"
        
        # Search for team logo patterns
        team_logos = soup.find_all(text=re.compile(r'team logo'))
        print(f"🏈 Found {len(team_logos)} team logo references")
        
        # Look for specific team abbreviations
        team_abbrevs = soup.find_all(text=re.compile(r'\b[A-Z]{2,4}\b'))
        unique_teams = set()
        for text in team_abbrevs:
            if re.match(r'^[A-Z]{2,4}$', text.strip()):
                unique_teams.add(text.strip())
        
        print(f"🏈 Found team abbreviations: {sorted(unique_teams)}")
        
        # Look for the main content area
        main_content = soup.find('main') or soup.find('div', class_=re.compile(r'content|main'))
        if main_content:
            print("✅ Found main content area")
            
            # Look for rows with game data
            rows = main_content.find_all('tr')
            print(f"📋 Found {len(rows)} table rows")
            
            # Examine first few rows
            for i, row in enumerate(rows[:3]):
                cells = row.find_all(['td', 'th'])
                if len(cells) > 5:  # Likely a game row
                    print(f"\nRow {i+1}: {len(cells)} cells")
                    for j, cell in enumerate(cells[:5]):  # First 5 cells
                        text = cell.get_text(strip=True)
                        if text:
                            print(f"  Cell {j+1}: {text[:50]}...")
        
        # Look for specific game patterns
        game_patterns = soup.find_all(text=re.compile(r'SUN|MON|THU|SAT'))
        print(f"\n📅 Found {len(game_patterns)} time/day patterns")
        
        # Look for odds patterns (like -424, +151)
        odds_patterns = soup.find_all(text=re.compile(r'[+-]\d{3,4}'))
        print(f"💰 Found {len(odds_patterns)} odds patterns")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_cbs_structure()









