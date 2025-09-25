#!/usr/bin/env python3
"""Check Week 1 data to understand the mismatch"""

import pandas as pd
from datetime import datetime

# Load original picks
original_df = pd.read_csv('data/outputs/2025/week-week1-picks.csv')
print('Original picks sample:')
print(original_df[['away_team', 'home_team', 'commence_time']].head())

# Check the commence_time to see what week this actually was
print('\nCommence times:')
for time_str in original_df['commence_time'].head():
    try:
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        print(f'{time_str} -> {dt.strftime("%Y-%m-%d %H:%M")}')
    except:
        print(f'{time_str} -> Error parsing')

# Check what games we have
print('\nAll games in original picks:')
for _, row in original_df.iterrows():
    print(f'{row["away_team"]} @ {row["home_team"]}')


