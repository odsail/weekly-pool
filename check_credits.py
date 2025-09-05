#!/usr/bin/env python3
"""
Check remaining credits for The Odds API.
This makes a minimal API call to get the response headers with credit information.
"""
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_credits():
    """Check remaining API credits by making a minimal call"""
    load_dotenv()
    api_key = os.getenv("ODDS_API_KEY")
    
    if not api_key:
        print("❌ No API key found in .env file")
        return
    
    try:
        import requests
        
        # Make a minimal API call to get headers
        # Using the sports endpoint (no cost) to check credits
        url = "https://api.the-odds-api.com/v4/sports"
        params = {"apiKey": api_key}
        
        print("🔍 Checking API credits...")
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        
        # Extract credit information from headers
        remaining = resp.headers.get('x-requests-remaining')
        used = resp.headers.get('x-requests-used')
        last_cost = resp.headers.get('x-requests-last')
        
        print("\n📊 API Credit Status:")
        print("=" * 30)
        
        if remaining is not None:
            print(f"Credits Remaining: {remaining}")
        else:
            print("Credits Remaining: Not available")
            
        if used is not None:
            print(f"Credits Used: {used}")
        else:
            print("Credits Used: Not available")
            
        if last_cost is not None:
            print(f"Last Call Cost: {last_cost}")
        else:
            print("Last Call Cost: Not available")
        
        # Calculate usage percentage if we have the data
        if remaining and used:
            try:
                remaining_int = int(remaining)
                used_int = int(used)
                total = remaining_int + used_int
                if total > 0:
                    usage_pct = (used_int / total) * 100
                    print(f"Usage: {usage_pct:.1f}% ({used_int}/{total})")
            except ValueError:
                pass
        
        print("\n💡 Note: This check used 0 credits (sports endpoint is free)")
        
    except Exception as e:
        print(f"❌ Error checking credits: {e}")

if __name__ == "__main__":
    check_credits()
