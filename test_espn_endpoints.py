#!/usr/bin/env python3
"""
Test specific ESPN API endpoints to see what data is actually available.
Based on the pseudo-r/Public-ESPN-API documentation.
"""
import requests
import json
from typing import Dict, List, Optional

def test_specific_endpoints():
    """Test specific ESPN endpoints to see what works"""
    
    print("🧪 Testing specific ESPN API endpoints...")
    
    # Get a real game ID first
    game_id = get_sample_game_id()
    if not game_id:
        print("❌ Could not get sample game ID")
        return
    
    print(f"🎯 Using game ID: {game_id}")
    
    # Test different endpoint patterns
    endpoints_to_test = [
        # Core API endpoints
        f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{game_id}",
        f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{game_id}/competitions",
        f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{game_id}/competitions/{game_id}",
        f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{game_id}/competitions/{game_id}/statistics",
        f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{game_id}/competitions/{game_id}/predictor",
        
        # Site API endpoints
        f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary/{game_id}",
        f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
        
        # Team endpoints
        "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams",
        "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams/21",  # Eagles
        "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams/21/statistics",
        "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams/21/injuries",
    ]
    
    for url in endpoints_to_test:
        print(f"\n📡 Testing: {url}")
        test_endpoint(url)

def get_sample_game_id() -> Optional[str]:
    """Get a sample game ID from the scoreboard"""
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        events = data.get("events", [])
        if events:
            return events[0].get("id")
        
    except Exception as e:
        print(f"❌ Error getting sample game ID: {e}")
    
    return None

def test_endpoint(url: str):
    """Test a specific endpoint"""
    try:
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Keys: {list(data.keys())}")
            
            # Show sample data structure
            if isinstance(data, dict):
                if "items" in data:
                    print(f"   📊 Items: {len(data['items'])}")
                    if data["items"]:
                        print(f"   📋 Sample item keys: {list(data['items'][0].keys())}")
                elif "events" in data:
                    print(f"   🎮 Events: {len(data['events'])}")
                    if data["events"]:
                        print(f"   📋 Sample event keys: {list(data['events'][0].keys())}")
                elif "competitions" in data:
                    print(f"   🏈 Competitions: {len(data['competitions'])}")
                    if data["competitions"]:
                        print(f"   📋 Sample competition keys: {list(data['competitions'][0].keys())}")
                
                # Show a small sample of the data
                print(f"   📄 Sample data: {json.dumps(data, indent=2)[:300]}...")
            
        elif response.status_code == 404:
            print(f"   ❌ Not found")
        elif response.status_code == 400:
            print(f"   ❌ Bad request")
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def test_team_data():
    """Test team-specific data endpoints"""
    print("\n" + "=" * 50)
    print("🏈 Testing team data endpoints...")
    
    # Test getting team list
    url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Found {data.get('count', 0)} teams")
        
        if data.get("items"):
            # Get first team
            first_team = data["items"][0]
            team_ref = first_team.get("$ref")
            
            if team_ref:
                print(f"🎯 Testing team details: {team_ref}")
                test_endpoint(team_ref)
                
                # Try team statistics
                team_id = team_ref.split("/")[-1]
                stats_url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams/{team_id}/statistics"
                print(f"📊 Testing team stats: {stats_url}")
                test_endpoint(stats_url)
                
                # Try team injuries
                injuries_url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams/{team_id}/injuries"
                print(f"🏥 Testing team injuries: {injuries_url}")
                test_endpoint(injuries_url)
        
    except Exception as e:
        print(f"❌ Error testing team data: {e}")

def test_week_specific_data():
    """Test week-specific data endpoints"""
    print("\n" + "=" * 50)
    print("📅 Testing week-specific data...")
    
    # Try to get Week 1 events
    week_urls = [
        "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2025/weeks/1/events",
        "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2025/types/1/weeks/1/events",
        "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=20250905-20250909",
    ]
    
    for url in week_urls:
        print(f"\n📡 Testing week endpoint: {url}")
        test_endpoint(url)

if __name__ == "__main__":
    test_specific_endpoints()
    test_team_data()
    test_week_specific_data()
