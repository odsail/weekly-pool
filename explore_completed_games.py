#!/usr/bin/env python3
"""
Explore completed games to see what detailed statistics are available.
Completed games should have full statistics data.
"""
import requests
import json
from typing import Dict, List, Optional

def get_completed_games():
    """Get completed games from Week 1 to see detailed stats"""
    print("🔍 Looking for completed Week 1 games with detailed stats...")
    
    base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
    
    # Try to get Week 1 games (which should be completed)
    url = f"{base_url}/scoreboard"
    params = {
        "dates": "20250905-20250909",  # Week 1 date range
        "limit": 1000
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Found {len(data.get('events', []))} events")
        
        # Look for completed games
        completed_games = []
        for event in data.get("events", []):
            status = event.get("status", {})
            if status.get("type", {}).get("name") == "STATUS_FINAL":
                completed_games.append(event)
        
        print(f"🏁 Found {len(completed_games)} completed games")
        
        if completed_games:
            # Analyze the first completed game in detail
            game = completed_games[0]
            game_id = game["id"]
            game_name = game["name"]
            
            print(f"\n🎯 Analyzing completed game: {game_name}")
            print(f"   Game ID: {game_id}")
            
            # Try different ways to get detailed stats
            analyze_game_stats(game_id, game_name)
            
            # Also check if the event itself has detailed stats
            analyze_event_stats(game)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def analyze_game_stats(game_id: str, game_name: str):
    """Analyze detailed stats for a specific game"""
    base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
    
    # Try different endpoint patterns
    endpoints = [
        f"/summary/{game_id}",
        f"/game/{game_id}",
        f"/events/{game_id}",
        f"/boxscore/{game_id}",
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n📊 Testing: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Keys: {list(data.keys())}")
                
                # Look for detailed statistics
                if "boxscore" in data:
                    analyze_boxscore(data["boxscore"])
                
                if "competitions" in data:
                    for comp in data["competitions"]:
                        if "competitors" in comp:
                            analyze_competitors(comp["competitors"])
                
                if "drives" in data:
                    drives = data["drives"]
                    print(f"   🚗 Drives: {len(drives.get('previous', []))} previous")
                
                if "plays" in data:
                    plays = data["plays"]
                    print(f"   🎯 Plays: {len(plays.get('plays', []))} total")
                
                # Show sample of the data structure
                print(f"   📋 Sample data structure:")
                print(f"      {json.dumps(data, indent=2)[:500]}...")
                
            else:
                print(f"   ❌ Not found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def analyze_boxscore(boxscore: Dict):
    """Analyze boxscore data for detailed stats"""
    print(f"   📈 Boxscore analysis:")
    
    if "teams" in boxscore:
        for team in boxscore["teams"]:
            team_name = team.get("team", {}).get("displayName", "Unknown")
            print(f"      {team_name}:")
            
            if "statistics" in team:
                stats = team["statistics"]
                print(f"         Statistics categories: {len(stats)}")
                
                for stat in stats[:10]:  # Show first 10 stats
                    label = stat.get("label", "Unknown")
                    value = stat.get("displayValue", "N/A")
                    print(f"           - {label}: {value}")
            else:
                print(f"         No statistics found")

def analyze_competitors(competitors: List[Dict]):
    """Analyze competitor data for detailed stats"""
    print(f"   👥 Competitors analysis:")
    
    for competitor in competitors:
        team_name = competitor.get("team", {}).get("displayName", "Unknown")
        score = competitor.get("score", "N/A")
        print(f"      {team_name}: {score}")
        
        if "statistics" in competitor:
            stats = competitor["statistics"]
            print(f"         Statistics: {len(stats)} categories")
            
            for stat in stats[:5]:  # Show first 5 stats
                label = stat.get("label", "Unknown")
                value = stat.get("displayValue", "N/A")
                print(f"           - {label}: {value}")
        else:
            print(f"         No statistics found")
        
        if "leaders" in competitor:
            leaders = competitor["leaders"]
            print(f"         Leaders: {len(leaders)} categories")

def analyze_event_stats(event: Dict):
    """Analyze the event data itself for stats"""
    print(f"\n📊 Event-level statistics:")
    
    if "competitions" in event:
        for comp in event["competitions"]:
            if "competitors" in comp:
                for competitor in comp["competitors"]:
                    team_name = competitor.get("team", {}).get("displayName", "Unknown")
                    print(f"   {team_name}:")
                    
                    # Check for statistics in the event data
                    if "statistics" in competitor:
                        stats = competitor["statistics"]
                        print(f"      Statistics: {len(stats)} categories")
                        
                        for stat in stats:
                            label = stat.get("label", "Unknown")
                            value = stat.get("displayValue", "N/A")
                            print(f"        - {label}: {value}")
                    else:
                        print(f"      No statistics in event data")
                    
                    # Check for leaders
                    if "leaders" in competitor:
                        leaders = competitor["leaders"]
                        print(f"      Leaders: {len(leaders)} categories")
                        for leader in leaders:
                            print(f"        - {leader.get('displayName', 'Unknown')}")

def try_alternative_endpoints():
    """Try alternative ESPN endpoints for detailed stats"""
    print("\n" + "=" * 50)
    print("🔄 Trying alternative endpoints...")
    
    base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
    
    # Try the core API which might have more detailed stats
    core_url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl"
    
    endpoints = [
        f"{core_url}/events",
        f"{core_url}/seasons/2025/weeks/1/events",
        f"{base_url}/leaders",
        f"{base_url}/stats",
    ]
    
    for url in endpoints:
        print(f"\n📡 Testing: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Keys: {list(data.keys())}")
                
                # Show sample data
                if "items" in data:
                    print(f"   📋 Items: {len(data['items'])}")
                    if data["items"]:
                        print(f"   📋 Sample item keys: {list(data['items'][0].keys())}")
                
            else:
                print(f"   ❌ Not found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    get_completed_games()
    try_alternative_endpoints()
