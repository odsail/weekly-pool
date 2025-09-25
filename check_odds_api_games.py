#!/usr/bin/env python3
"""Check what games The Odds API is returning"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ODDS_API_KEY')

# Get current games from The Odds API
url = 'https://api.the-odds-api.com/v4/sports/americanfootball_nfl/events'
params = {
    'apiKey': api_key,
    'commenceTimeFrom': '2025-09-01T00:00:00Z',
    'commenceTimeTo': '2025-09-15T23:59:59Z'
}

response = requests.get(url, params=params, timeout=10)
events = response.json()

print(f'Found {len(events)} games from The Odds API:')
for i, event in enumerate(events[:10]):  # Show first 10
    print(f'{i+1}. {event["away_team"]} @ {event["home_team"]} - {event["commence_time"]}')

print('\nAll games:')
for i, event in enumerate(events):
    print(f'{i+1}. {event["away_team"]} @ {event["home_team"]} - {event["commence_time"]}')


