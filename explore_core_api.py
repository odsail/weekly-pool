#!/usr/bin/env python3
"""
Explore the ESPN Core API to find detailed game statistics.
This API seems to have more detailed data than the site API.
"""
import requests
import json
from typing import Dict, List, Optional

def explore_core_api():
    """Explore the ESPN Core API for detailed stats"""
    print("🔍 Exploring ESPN Core API for detailed statistics...")
    
    base_url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl"
    
    # Get events from core API
    events_url = f"{base_url}/events"
    
    try:
        response = requests.get(events_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Found {data.get('count', 0)} events")
        
        if data.get("items"):
            # Get the first event to explore
            first_event_ref = data["items"][0]["$ref"]
            print(f"🎯 Exploring first event: {first_event_ref}")
            
            # Fetch the detailed event data
            event_response = requests.get(first_event_ref, timeout=10)
            event_response.raise_for_status()
            event_data = event_response.json()
            
            print(f"📊 Event data keys: {list(event_data.keys())}")
            
            # Look for statistics
            if "competitions" in event_data:
                analyze_core_competitions(event_data["competitions"])
            
            # Look for other useful data
            if "drives" in event_data:
                drives = event_data["drives"]
                print(f"🚗 Drives: {drives.get('$ref', 'No ref')}")
                if "$ref" in drives:
                    fetch_drives_data(drives["$ref"])
            
            if "plays" in event_data:
                plays = event_data["plays"]
                print(f"🎯 Plays: {plays.get('$ref', 'No ref')}")
                if "$ref" in plays:
                    fetch_plays_data(plays["$ref"])
            
            # Show sample of full event data
            print(f"\n📋 Sample event data structure:")
            print(json.dumps(event_data, indent=2)[:1000] + "...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def analyze_core_competitions(competitions: List[Dict]):
    """Analyze competitions data from core API"""
    print(f"\n🏈 Analyzing {len(competitions)} competitions...")
    
    for i, comp in enumerate(competitions):
        print(f"\n   Competition {i+1}:")
        print(f"   Keys: {list(comp.keys())}")
        
        if "competitors" in comp:
            competitors = comp["competitors"]
            print(f"   Competitors: {len(competitors)}")
            
            for j, competitor in enumerate(competitors):
                print(f"\n      Competitor {j+1}:")
                print(f"      Keys: {list(competitor.keys())}")
                
                # Look for statistics reference
                if "statistics" in competitor:
                    stats_ref = competitor["statistics"]
                    print(f"      Statistics: {stats_ref.get('$ref', 'No ref')}")
                    
                    if "$ref" in stats_ref:
                        fetch_statistics_data(stats_ref["$ref"])
                
                # Look for team reference
                if "team" in competitor:
                    team_ref = competitor["team"]
                    print(f"      Team: {team_ref.get('$ref', 'No ref')}")
                
                # Look for score
                if "score" in competitor:
                    score = competitor["score"]
                    print(f"      Score: {score}")

def fetch_statistics_data(stats_url: str):
    """Fetch detailed statistics data"""
    print(f"         📈 Fetching statistics from: {stats_url}")
    
    try:
        response = requests.get(stats_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"         ✅ Statistics data keys: {list(data.keys())}")
        
        if "items" in data:
            items = data["items"]
            print(f"         📊 Statistics items: {len(items)}")
            
            for item in items[:5]:  # Show first 5 stats
                print(f"            - {item.get('label', 'Unknown')}: {item.get('displayValue', 'N/A')}")
        
    except Exception as e:
        print(f"         ❌ Error fetching statistics: {e}")

def fetch_drives_data(drives_url: str):
    """Fetch drives data"""
    print(f"🚗 Fetching drives from: {drives_url}")
    
    try:
        response = requests.get(drives_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Drives data keys: {list(data.keys())}")
        
        if "items" in data:
            items = data["items"]
            print(f"📊 Drives: {len(items)}")
            
            # Show sample drive
            if items:
                drive = items[0]
                print(f"   Sample drive keys: {list(drive.keys())}")
                print(f"   Sample drive: {json.dumps(drive, indent=2)[:300]}...")
        
    except Exception as e:
        print(f"❌ Error fetching drives: {e}")

def fetch_plays_data(plays_url: str):
    """Fetch plays data"""
    print(f"🎯 Fetching plays from: {plays_url}")
    
    try:
        response = requests.get(plays_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Plays data keys: {list(data.keys())}")
        
        if "items" in data:
            items = data["items"]
            print(f"📊 Plays: {len(items)}")
            
            # Show sample play
            if items:
                play = items[0]
                print(f"   Sample play keys: {list(play.keys())}")
                print(f"   Sample play: {json.dumps(play, indent=2)[:300]}...")
        
    except Exception as e:
        print(f"❌ Error fetching plays: {e}")

def try_team_stats():
    """Try to get team statistics from core API"""
    print("\n" + "=" * 50)
    print("🏈 Trying to get team statistics...")
    
    base_url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl"
    
    # Try to get teams
    teams_url = f"{base_url}/teams"
    
    try:
        response = requests.get(teams_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Found {data.get('count', 0)} teams")
        
        if data.get("items"):
            # Get first team
            first_team_ref = data["items"][0]["$ref"]
            print(f"🎯 Exploring first team: {first_team_ref}")
            
            # Fetch team data
            team_response = requests.get(first_team_ref, timeout=10)
            team_response.raise_for_status()
            team_data = team_response.json()
            
            print(f"📊 Team data keys: {list(team_data.keys())}")
            
            # Look for statistics
            if "statistics" in team_data:
                stats_ref = team_data["statistics"]
                print(f"📈 Team statistics: {stats_ref.get('$ref', 'No ref')}")
                
                if "$ref" in stats_ref:
                    fetch_statistics_data(stats_ref["$ref"])
            
            # Look for roster
            if "roster" in team_data:
                roster_ref = team_data["roster"]
                print(f"👥 Team roster: {roster_ref.get('$ref', 'No ref')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    explore_core_api()
    try_team_stats()
