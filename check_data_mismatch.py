#!/usr/bin/env python3
"""Check data mismatch between original picks and live data"""

import pandas as pd
from database_manager import DatabaseManager

# Check what we have in the database
db = DatabaseManager(version='v2')
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t1.name as home_team, t2.name as away_team, g.home_score, g.away_score
        FROM games g
        JOIN teams t1 ON g.home_team_id = t1.id
        JOIN teams t2 ON g.away_team_id = t2.id
        WHERE g.season_year = 2025 AND g.week = 1
        ORDER BY g.game_date
        LIMIT 5
    ''')
    db_games = cursor.fetchall()

print('Database Week 1 games:')
for game in db_games:
    print(f'{game[1]} @ {game[0]} - {game[3]}-{game[2]}')

# Check original picks
original_df = pd.read_csv('data/outputs/2025/week-week1-picks.csv')
print('\nOriginal picks (first 5):')
for _, row in original_df.head().iterrows():
    print(f'{row["away_team"]} @ {row["home_team"]}')

# Check if any match
print('\nChecking for matches...')
matches = 0
for _, orig_row in original_df.iterrows():
    for db_game in db_games:
        if (orig_row['home_team'] == db_game[0] and 
            orig_row['away_team'] == db_game[1]):
            matches += 1
            print(f'MATCH: {orig_row["away_team"]} @ {orig_row["home_team"]}')

print(f'\nTotal matches found: {matches}')


