#!/usr/bin/env python3
"""
Explore ESPN API to discover what detailed stats are available.
This will help us understand what rich data we can pull for analysis.
"""
import requests
import json
from typing import Dict, List, Optional

def explore_espn_endpoints():
    """Explore different ESPN API endpoints to see what data is available"""
    
    base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
    
    # Test different endpoints
    endpoints_to_test = [
        "/scoreboard",  # Basic scoreboard
        "/teams",       # Team information
        "/standings",   # League standings
        "/leaders",     # Statistical leaders
        "/players",     # Player stats
    ]
    
    print("🔍 Exploring ESPN API endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 Testing: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Response keys: {list(data.keys())}")
            
            # Show sample structure
            if endpoint == "/scoreboard" and "events" in data:
                if data["events"]:
                    event = data["events"][0]
                    print(f"🎮 Sample event keys: {list(event.keys())}")
                    
                    # Look for detailed stats in competitions
                    if "competitions" in event:
                        comp = event["competitions"][0]
                        print(f"🏈 Competition keys: {list(comp.keys())}")
                        
                        if "competitors" in comp:
                            competitor = comp["competitors"][0]
                            print(f"👥 Competitor keys: {list(competitor.keys())}")
                            
                            # Look for statistics
                            if "statistics" in competitor:
                                stats = competitor["statistics"]
                                print(f"📈 Statistics available: {len(stats)} categories")
                                for stat in stats[:5]:  # Show first 5
                                    print(f"   - {stat.get('label', 'Unknown')}: {stat.get('displayValue', 'N/A')}")
            
            elif endpoint == "/leaders":
                if "leaders" in data:
                    print(f"🏆 Leaders categories: {len(data['leaders'])}")
                    for leader in data["leaders"][:3]:
                        print(f"   - {leader.get('displayName', 'Unknown')}")
            
            elif endpoint == "/teams":
                if "sports" in data:
                    teams = data["sports"][0]["leagues"][0]["teams"]
                    print(f"🏈 Teams found: {len(teams)}")
                    if teams:
                        team = teams[0]["team"]
                        print(f"   Sample team: {team.get('displayName')} (ID: {team.get('id')})")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def explore_game_details():
    """Explore detailed game information for a specific game"""
    print("\n" + "=" * 50)
    print("🎮 Exploring detailed game information...")
    
    # Get a specific game ID from the scoreboard
    base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
    
    try:
        # Get current scoreboard
        scoreboard_url = f"{base_url}/scoreboard"
        response = requests.get(scoreboard_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("events"):
            game_id = data["events"][0]["id"]
            print(f"🎯 Analyzing game ID: {game_id}")
            
            # Try different game detail endpoints
            detail_endpoints = [
                f"/summary",  # Game summary
                f"/boxscore", # Box score
                f"/playbyplay", # Play by play
                f"/stats",    # Game stats
            ]
            
            for endpoint in detail_endpoints:
                url = f"{base_url}/summary/{game_id}"
                print(f"\n📊 Testing: {endpoint}")
                
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    print(f"✅ Status: {response.status_code}")
                    print(f"📋 Response keys: {list(data.keys())}")
                    
                    # Look for detailed stats
                    if "boxscore" in data:
                        boxscore = data["boxscore"]
                        print(f"📈 Boxscore keys: {list(boxscore.keys())}")
                        
                        if "teams" in boxscore:
                            for team in boxscore["teams"]:
                                team_name = team.get("team", {}).get("displayName", "Unknown")
                                print(f"   {team_name} stats available")
                                
                                if "statistics" in team:
                                    stats = team["statistics"]
                                    print(f"     Statistics categories: {len(stats)}")
                                    for stat in stats[:5]:
                                        print(f"       - {stat.get('label', 'Unknown')}: {stat.get('displayValue', 'N/A')}")
                    
                    if "drives" in data:
                        drives = data["drives"]
                        print(f"🚗 Drives data: {len(drives.get('previous', []))} previous drives")
                    
                    if "plays" in data:
                        plays = data["plays"]
                        print(f"🎯 Plays data: {len(plays.get('plays', []))} plays")
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
    except Exception as e:
        print(f"❌ Error getting game details: {e}")

def explore_team_stats():
    """Explore team-specific statistics"""
    print("\n" + "=" * 50)
    print("🏈 Exploring team statistics...")
    
    base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
    
    try:
        # Get teams
        teams_url = f"{base_url}/teams"
        response = requests.get(teams_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "sports" in data and data["sports"]:
            teams = data["sports"][0]["leagues"][0]["teams"]
            
            # Pick a team to analyze
            if teams:
                team = teams[0]["team"]
                team_id = team["id"]
                team_name = team["displayName"]
                
                print(f"🎯 Analyzing team: {team_name} (ID: {team_id})")
                
                # Try team-specific endpoints
                team_endpoints = [
                    f"/teams/{team_id}/stats",      # Team stats
                    f"/teams/{team_id}/roster",     # Roster
                    f"/teams/{team_id}/schedule",   # Schedule
                    f"/teams/{team_id}/injuries",   # Injuries
                ]
                
                for endpoint in team_endpoints:
                    url = f"{base_url}{endpoint}"
                    print(f"\n📊 Testing: {endpoint}")
                    
                    try:
                        response = requests.get(url, timeout=10)
                        response.raise_for_status()
                        data = response.json()
                        
                        print(f"✅ Status: {response.status_code}")
                        print(f"📋 Response keys: {list(data.keys())}")
                        
                        # Look for specific data
                        if "stats" in data:
                            stats = data["stats"]
                            print(f"📈 Stats categories: {len(stats)}")
                            for stat in stats[:5]:
                                print(f"   - {stat.get('label', 'Unknown')}: {stat.get('displayValue', 'N/A')}")
                        
                        if "athletes" in data:
                            athletes = data["athletes"]
                            print(f"👥 Athletes: {len(athletes)}")
                        
                        if "events" in data:
                            events = data["events"]
                            print(f"🎮 Events: {len(events)}")
                        
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        
    except Exception as e:
        print(f"❌ Error exploring team stats: {e}")

if __name__ == "__main__":
    explore_espn_endpoints()
    explore_game_details()
    explore_team_stats()
