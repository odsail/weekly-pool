#!/usr/bin/env python3
"""
Query Week 4 Results for Performance Analysis
"""

import pandas as pd
import sqlite3
from datetime import datetime
import os
from database_manager import DatabaseManager

# Initialize DatabaseManager
db_manager = DatabaseManager('data/nfl_pool_v2.db')

def query_week4_results():
    """
    Query Week 4 game results and analyze model performance.
    """
    print("📊 **WEEK 4 RESULTS ANALYSIS**")
    print("=" * 50)
    
    # Connect to database
    db_path = "data/nfl_pool_v2.db"
    conn = sqlite3.connect(db_path)
    
    # Get Week 4 games with results
    query = """
    SELECT 
        g.id as game_id,
        g.week,
        g.game_date,
        ht.name as home_team,
        at.name as away_team,
        g.home_score,
        g.away_score,
        g.is_completed,
        g.is_international,
        o.home_ml,
        o.away_ml,
        o.total_points
    FROM games g
    JOIN teams ht ON g.home_team_id = ht.id
    JOIN teams at ON g.away_team_id = at.id
    LEFT JOIN odds o ON g.id = o.game_id
    WHERE g.season_year = 2025 AND g.week = 4
    ORDER BY g.game_date
    """
    
    games_df = pd.read_sql_query(query, conn)
    print(f"📊 Found {len(games_df)} Week 4 games")
    
    # Display results
    print("\n🏈 **WEEK 4 GAME RESULTS**")
    print("-" * 50)
    
    for _, game in games_df.iterrows():
        if game['is_completed']:
            winner = game['home_team'] if game['home_score'] > game['away_score'] else game['away_team']
            print(f"✅ {game['away_team']} @ {game['home_team']}: {game['away_score']}-{game['home_score']} (Winner: {winner})")
        else:
            print(f"⏳ {game['away_team']} @ {game['home_team']}: Not completed")
    
    # Get your Week 4 picks
    picks_query = """
    SELECT 
        p.game_id,
        pt.name as pick_team,
        p.confidence_points as confidence,
        ht.name as home_team,
        at.name as away_team,
        g.home_score,
        g.away_score,
        g.is_completed
    FROM picks p
    JOIN games g ON p.game_id = g.id
    JOIN teams ht ON g.home_team_id = ht.id
    JOIN teams at ON g.away_team_id = at.id
    JOIN teams pt ON p.pick_team_id = pt.id
    WHERE g.season_year = 2025 AND g.week = 4
    ORDER BY p.confidence_points DESC
    """
    
    picks_df = pd.read_sql_query(picks_query, conn)
    print(f"\n📊 Found {len(picks_df)} Week 4 picks")
    
    # Analyze performance
    correct_picks = 0
    total_points = 0
    completed_games = 0
    
    print("\n🎯 **YOUR WEEK 4 PICKS PERFORMANCE**")
    print("-" * 50)
    
    for _, pick in picks_df.iterrows():
        if pick['is_completed']:
            completed_games += 1
            # Determine winner
            winner = pick['home_team'] if pick['home_score'] > pick['away_score'] else pick['away_team']
            is_correct = pick['pick_team'] == winner
            
            if is_correct:
                correct_picks += 1
                total_points += pick['confidence']
                status = "✅"
            else:
                status = "❌"
            
            print(f"{status} {pick['confidence']:2d} pts: {pick['pick_team']} vs {winner} ({pick['away_team']} @ {pick['home_team']})")
    
    if completed_games > 0:
        accuracy = (correct_picks / completed_games) * 100
        print(f"\n📈 **WEEK 4 PERFORMANCE SUMMARY**")
        print(f"Correct Picks: {correct_picks}/{completed_games}")
        print(f"Accuracy: {accuracy:.1f}%")
        print(f"Total Points: {total_points}")
    else:
        print("\n⏳ No completed games yet - results will be available after games finish")
    
    conn.close()
    
    return {
        'games': games_df,
        'picks': picks_df,
        'correct_picks': correct_picks,
        'total_games': completed_games,
        'accuracy': (correct_picks / completed_games * 100) if completed_games > 0 else 0,
        'total_points': total_points
    }

def main():
    print("📊 **WEEK 4 RESULTS QUERY**")
    print("=" * 50)
    
    results = query_week4_results()
    
    print(f"\n✅ **ANALYSIS COMPLETE**")
    print("=" * 40)
    print("📊 Week 4 results queried successfully")
    print("🎯 Performance analysis completed")
    
    print(f"\n📋 **COMMAND USED:**")
    print("```bash")
    print("python query_week4_results.py")
    print("```")

if __name__ == "__main__":
    main()
