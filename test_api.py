#!/usr/bin/env python3
"""
Minimal test script to verify The Odds API setup with minimal credit usage.
This will cost only 10 credits to test the connection.
"""
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import fetch_odds

def test_api_connection():
    """Test API connection with minimal usage (10 credits)"""
    print("Testing The Odds API connection...")
    print("This will cost 10 credits (1 market × 1 region × 10 base cost)")
    
    try:
        # Test with minimal parameters - just 1 day ahead
        payload = fetch_odds(days=1, regions="us")
        
        events = payload.get("events", [])
        print(f"✅ Success! Found {len(events)} NFL games")
        
        if events:
            # Show first game as example
            first_game = events[0]
            print(f"📅 First game: {first_game.get('away_team')} @ {first_game.get('home_team')}")
            print(f"⏰ Commence time: {first_game.get('commence_time')}")
            
            # Show bookmakers available
            bookmakers = [bm.get('title') for bm in first_game.get('bookmakers', [])]
            print(f"🏦 Available bookmakers: {', '.join(bookmakers[:5])}{'...' if len(bookmakers) > 5 else ''}")
        
        print(f"\n📊 API Response Headers (check your credit usage):")
        print(f"   - Fetched at: {payload.get('fetched_at')}")
        print(f"   - Regions: {payload.get('params', {}).get('regions')}")
        print(f"   - Markets: {payload.get('params', {}).get('markets')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    load_dotenv()
    
    # Check if API key is set
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ Please set your ODDS_API_KEY in .env file")
        print("1. Copy .env.example to .env")
        print("2. Get your API key from: https://the-odds-api.com/")
        print("3. Edit .env and set ODDS_API_KEY=your_actual_key")
        sys.exit(1)
    
    success = test_api_connection()
    if success:
        print("\n🎉 API test successful! You can now run the main script.")
        print("💡 Tip: Use 'python src/main.py fetch' to save raw data and avoid repeated API calls")
    else:
        print("\n💥 API test failed. Check your API key and internet connection.")
