#!/usr/bin/env python3
"""
Test script for historical data collection.
Tests ESPN API access and data collection for a small sample.
"""
import requests
import json
from datetime import datetime
from database_manager import DatabaseManager

def test_espn_api_access():
    """Test ESPN API access for historical data"""
    print("🧪 Testing ESPN API access...")
    
    base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
    
    # Test current data
    try:
        response = requests.get(f"{base_url}/scoreboard")
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            print(f"✅ Current data: {len(events)} games")
        else:
            print(f"❌ Current data failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Current data error: {e}")
        return False
    
    # Test historical data
    test_dates = ['20231231', '20231224', '20231217']  # Recent 2023 dates
    
    for date in test_dates:
        try:
            response = requests.get(f"{base_url}/scoreboard", params={'dates': date})
            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                print(f"✅ Historical {date}: {len(events)} games")
                
                # Show sample game data
                if events:
                    sample_game = events[0]
                    print(f"   Sample: {sample_game.get('name', 'Unknown')}")
                    print(f"   Date: {sample_game.get('date', 'Unknown')}")
                    print(f"   Status: {sample_game.get('status', {}).get('type', {}).get('name', 'Unknown')}")
                    
                    # Check if game has scores
                    competitors = sample_game.get('competitions', [{}])[0].get('competitors', [])
                    if len(competitors) >= 2:
                        home_score = competitors[0].get('score', 'N/A')
                        away_score = competitors[1].get('score', 'N/A')
                        print(f"   Score: {away_score} @ {home_score}")
                    
            else:
                print(f"❌ Historical {date} failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Historical {date} error: {e}")
    
    return True

def test_database_schema():
    """Test database schema for historical data"""
    print("\n🗄️ Testing database schema...")
    
    try:
        db = DatabaseManager(version="v2")
        
        # Test teams table
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM teams")
            team_count = cursor.fetchone()[0]
            print(f"✅ Teams table: {team_count} teams")
            
            # Test games table structure
            cursor.execute("PRAGMA table_info(games)")
            columns = cursor.fetchall()
            print(f"✅ Games table: {len(columns)} columns")
            
            # Check for new columns
            column_names = [col[1] for col in columns]
            new_columns = ['is_international', 'international_location', 'true_home_team_id', 'stadium_type']
            for col in new_columns:
                if col in column_names:
                    print(f"✅ Column '{col}' exists")
                else:
                    print(f"❌ Column '{col}' missing")
            
            # Test home field advantage table
            cursor.execute("SELECT COUNT(*) FROM home_field_advantage")
            hfa_count = cursor.fetchone()[0]
            print(f"✅ Home field advantage table: {hfa_count} records")
            
            # Test international games table
            cursor.execute("SELECT COUNT(*) FROM international_games")
            intl_count = cursor.fetchone()[0]
            print(f"✅ International games table: {intl_count} records")
            
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False
    
    return True

def test_small_data_collection():
    """Test collecting a small sample of historical data"""
    print("\n📊 Testing small data collection...")
    
    try:
        from historical_data_collector import HistoricalDataCollector
        
        collector = HistoricalDataCollector()
        # Use v2 database
        collector.db_manager = DatabaseManager(version="v2")
        
        # Test collecting one week of data
        print("Testing Week 17, 2023...")
        games = collector._get_week_games(2023, 17)
        print(f"✅ Found {len(games)} games for Week 17, 2023")
        
        if games:
            # Process first game as test
            sample_game = games[0]
            print(f"   Processing sample game: {sample_game.get('name', 'Unknown')}")
            
            # Test game processing
            collector._process_game(sample_game, 2023, 17)
            print("✅ Game processing successful")
        
    except Exception as e:
        print(f"❌ Data collection test error: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Historical Data Collection Tests")
    print("=" * 50)
    
    # Test 1: ESPN API Access
    api_success = test_espn_api_access()
    
    # Test 2: Database Schema
    db_success = test_database_schema()
    
    # Test 3: Small Data Collection
    collection_success = test_small_data_collection()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"   ESPN API Access: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"   Database Schema: {'✅ PASS' if db_success else '❌ FAIL'}")
    print(f"   Data Collection: {'✅ PASS' if collection_success else '❌ FAIL'}")
    
    if api_success and db_success and collection_success:
        print("\n🎉 All tests passed! Ready for historical data collection.")
        print("💡 Run: python historical_data_collector.py")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
