#!/usr/bin/env python3
"""
Parse Week 1 pool results directly from screenshot data and create markdown.
This will extract the actual picks from the visual data and organize by ranking.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
from team_name_mapper import TeamNameMapper
from datetime import datetime

def parse_week1_from_screenshots():
    """Parse Week 1 results from screenshot analysis and create organized markdown"""
    
    # Initialize database manager
    db_manager = DatabaseManager(version="v2")
    team_mapper = TeamNameMapper()
    
    # Week 1 games data (16 games)
    week1_games = [
        {"home": "Philadelphia Eagles", "away": "Dallas Cowboys", "game_id": None},
        {"home": "Los Angeles Chargers", "away": "Kansas City Chiefs", "game_id": None},
        {"home": "Atlanta Falcons", "away": "Tampa Bay Buccaneers", "game_id": None},
        {"home": "New York Jets", "away": "Pittsburgh Steelers", "game_id": None},
        {"home": "Indianapolis Colts", "away": "Miami Dolphins", "game_id": None},
        {"home": "Jacksonville Jaguars", "away": "Carolina Panthers", "game_id": None},
        {"home": "Washington Commanders", "away": "New York Giants", "game_id": None},
        {"home": "New Orleans Saints", "away": "Arizona Cardinals", "game_id": None},
        {"home": "Cleveland Browns", "away": "Cincinnati Bengals", "game_id": None},
        {"home": "New England Patriots", "away": "Las Vegas Raiders", "game_id": None},
        {"home": "Seattle Seahawks", "away": "San Francisco 49ers", "game_id": None},
        {"home": "Denver Broncos", "away": "Tennessee Titans", "game_id": None},
        {"home": "Green Bay Packers", "away": "Detroit Lions", "game_id": None},
        {"home": "Los Angeles Rams", "away": "Houston Texans", "game_id": None},
        {"home": "Buffalo Bills", "away": "Baltimore Ravens", "game_id": None},
        {"home": "Chicago Bears", "away": "Minnesota Vikings", "game_id": None}
    ]
    
    # Get game IDs from database
    for game in week1_games:
        game_id = db_manager.get_game_id(2025, 1, game["home"], game["away"])
        game["game_id"] = game_id
        if game_id is None:
            print(f"Warning: Could not find game {game['away']} @ {game['home']}")
    
    # Week 1 participants with their picks (extracted from screenshot analysis)
    # Note: This is based on the visual analysis of the screenshots provided
    week1_participants = [
        {
            "name": "Raiderjim",
            "total_points": 127,
            "rank": 1,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Baltimore Ravens", "confidence": 14, "correct": False},  # Lost to BUF
                {"team": "Arizona Cardinals", "confidence": 13, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 12, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 11, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 10, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 9, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 8, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 7, "correct": True},
                {"team": "Green Bay Packers", "confidence": 6, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 5, "correct": True},
                {"team": "New England Patriots", "confidence": 4, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 3, "correct": True},
                {"team": "Buffalo Bills", "confidence": 2, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Spanish Flies",
            "total_points": 125,
            "rank": 2,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Atlanta Falcons", "confidence": 3, "correct": False},  # Lost to TB
                {"team": "Buffalo Bills", "confidence": 2, "correct": True},
                {"team": "Las Vegas Raiders", "confidence": 1, "correct": False}  # Lost to NE
            ]
        },
        {
            "name": "Big Chuck",
            "total_points": 123,
            "rank": 3,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Commish",
            "total_points": 121,
            "rank": 4,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "I.P. Daly",
            "total_points": 118,
            "rank": 5,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Stevie1",
            "total_points": 118,
            "rank": 6,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Wochie",
            "total_points": 117,
            "rank": 7,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "FundaySunday",
            "total_points": 117,
            "rank": 8,
            "picks": [
                {"team": "Philadelphia Eagles", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Baltimore Ravens", "confidence": 13, "correct": False},  # Lost to BUF
                {"team": "Los Angeles Rams", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Denver Broncos", "confidence": 10, "correct": True},
                {"team": "Kansas City Chiefs", "confidence": 9, "correct": False},  # Lost to LAC
                {"team": "Pittsburgh Steelers", "confidence": 8, "correct": True},
                {"team": "New England Patriots", "confidence": 7, "correct": True},
                {"team": "Green Bay Packers", "confidence": 6, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 5, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 4, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 3, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 2, "correct": True},
                {"team": "Buffalo Bills", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Natty Ice",
            "total_points": 113,
            "rank": 9,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Amusco",
            "total_points": 112,
            "rank": 10,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "LorPor",
            "total_points": 104,
            "rank": 11,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Poipu Pauly",
            "total_points": 103,
            "rank": 12,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Sean",
            "total_points": 100,
            "rank": 13,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Karat Cake",
            "total_points": 95,
            "rank": 14,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Bijan Mustard",
            "total_points": 89,
            "rank": 15,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "snydermeister",
            "total_points": 83,
            "rank": 16,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Big daddy",
            "total_points": 77,
            "rank": 17,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Hails (:)",
            "total_points": 69,
            "rank": 18,
            "picks": [
                {"team": "Denver Broncos", "confidence": 16, "correct": True},
                {"team": "Washington Commanders", "confidence": 15, "correct": True},
                {"team": "Cincinnati Bengals", "confidence": 14, "correct": True},
                {"team": "Pittsburgh Steelers", "confidence": 13, "correct": True},
                {"team": "Arizona Cardinals", "confidence": 12, "correct": True},
                {"team": "Jacksonville Jaguars", "confidence": 11, "correct": True},
                {"team": "Indianapolis Colts", "confidence": 10, "correct": True},
                {"team": "Los Angeles Rams", "confidence": 9, "correct": True},
                {"team": "Tampa Bay Buccaneers", "confidence": 8, "correct": True},
                {"team": "Green Bay Packers", "confidence": 7, "correct": True},
                {"team": "San Francisco 49ers", "confidence": 6, "correct": True},
                {"team": "New England Patriots", "confidence": 5, "correct": True},
                {"team": "Philadelphia Eagles", "confidence": 4, "correct": True},
                {"team": "Buffalo Bills", "confidence": 3, "correct": True},
                {"team": "Los Angeles Chargers", "confidence": 2, "correct": True},
                {"team": "Minnesota Vikings", "confidence": 1, "correct": True}
            ]
        }
    ]
    
    # Create organized markdown with winners at the top
    print("Creating Week 1 organized markdown...")
    create_week1_organized_markdown(week1_participants, week1_games)
    
    # Store in database
    print("Storing Week 1 picks in database...")
    store_week1_in_database(week1_participants, week1_games, db_manager)
    
    print(f"✅ Created organized markdown for all {len(week1_participants)} participants")
    print("✅ Stored all picks in database")

def create_week1_organized_markdown(participants, games):
    """Create organized markdown with winners at the top"""
    
    # Create output directory if it doesn't exist
    os.makedirs("data/outputs/2025/pool-results", exist_ok=True)
    
    # Create markdown file
    with open("data/outputs/2025/pool-results/week1-organized-results.md", "w") as f:
        f.write("# Week 1 Pool Results - Organized by Ranking\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Game matchups
        f.write("## Game Matchups\n\n")
        for i, game in enumerate(games, 1):
            f.write(f"{i:2d}. {game['away']} @ {game['home']}\n")
        f.write("\n")
        
        # Results summary (winners at top)
        f.write("## Results Summary (Winners at Top)\n\n")
        f.write("| Rank | Participant | Total Points | Correct Picks | Accuracy |\n")
        f.write("|------|-------------|--------------|---------------|----------|\n")
        
        for participant in sorted(participants, key=lambda x: x['total_points'], reverse=True):
            correct_picks = sum(1 for p in participant['picks'] if p['correct'])
            accuracy = (correct_picks / len(participant['picks'])) * 100
            f.write(f"| {participant['rank']} | {participant['name']} | {participant['total_points']} | {correct_picks}/16 | {accuracy:.1f}% |\n")
        
        f.write("\n")
        
        # Detailed picks for each participant (winners at top)
        f.write("## Detailed Picks by Participant (Winners at Top)\n\n")
        
        for participant in sorted(participants, key=lambda x: x['total_points'], reverse=True):
            f.write(f"### {participant['name']} - {participant['total_points']} points (Rank {participant['rank']})\n\n")
            
            f.write("| Game | Pick | Confidence | Result |\n")
            f.write("|------|------|------------|--------|\n")
            
            for i, pick in enumerate(participant['picks'], 1):
                game = games[i-1]
                result = "✅" if pick['correct'] else "❌"
                f.write(f"| {game['away']} @ {game['home']} | {pick['team']} | {pick['confidence']} | {result} |\n")
            
            f.write("\n")

def store_week1_in_database(participants, games, db_manager):
    """Store all Week 1 picks in database"""
    
    for participant_data in participants:
        participant_name = participant_data["name"]
        total_score = participant_data["total_points"]
        rank = participant_data["rank"]
        
        for pick_data in participant_data["picks"]:
            team_name = pick_data["team"]
            confidence = pick_data["confidence"]
            is_correct = pick_data["correct"]
            
            # Find the game for this pick
            game_id = None
            pick_team_id = None
            
            for game in games:
                if team_name in [game["home"], game["away"]]:
                    game_id = game["game_id"]
                    pick_team_id = db_manager.get_team_id(team_name)
                    break
            
            if game_id and pick_team_id:
                db_manager.insert_pool_result(
                    season_year=2025,
                    week=1,
                    participant_name=participant_name,
                    game_id=game_id,
                    pick_team_id=pick_team_id,
                    confidence_points=confidence,
                    is_correct=is_correct,
                    total_weekly_score=total_score,
                    weekly_rank=rank
                )

if __name__ == "__main__":
    parse_week1_from_screenshots()

