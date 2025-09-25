#!/usr/bin/env python3
"""Check original picks dates"""

import pandas as pd
from datetime import datetime

# Check original picks dates
original_df = pd.read_csv('data/outputs/2025/week-week1-picks.csv')
print('Original picks dates:')
for i, time_str in enumerate(original_df['commence_time'].head()):
    try:
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        print(f'{i+1}. {time_str} -> {dt.strftime("%Y-%m-%d %H:%M")}')
    except:
        print(f'{i+1}. {time_str} -> Error parsing')

print(f'\nTotal original picks: {len(original_df)}')
print('\nAll original games:')
for _, row in original_df.iterrows():
    print(f'{row["away_team"]} @ {row["home_team"]}')


