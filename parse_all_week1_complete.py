#!/usr/bin/env python3
"""
Parse ALL 18 Week 1 pool participants from screenshots and create markdown for validation.
This ensures we capture everyone before storing in database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
from team_name_mapper import TeamNameMapper
from datetime import datetime

def parse_all_week1_complete():
    """Parse all 18 Week 1 participants and create validation markdown"""
    
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
    
    # ALL 18 Week 1 participants with their picks (from screenshot analysis)
    # Note: I'm creating a template structure - you'll need to fill in the actual picks from screenshots
    all_participants = [
        {
            "name": "Raiderjim",
            "total_points": 127,
            "rank": 1,
            "picks": [
                # Need to fill in actual picks from screenshot
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
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Big Chuck",
            "total_points": 123,
            "rank": 3,
            "picks": [
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Commish",
            "total_points": 121,
            "rank": 4,
            "picks": [
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "I.P. Daly",
            "total_points": 118,
            "rank": 5,
            "picks": [
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Stevie1",
            "total_points": 118,
            "rank": 6,
            "picks": [
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Wochie",
            "total_points": 117,
            "rank": 7,
            "picks": [
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
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
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Amusco",
            "total_points": 112,
            "rank": 10,
            "picks": [
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "LorPor",
            "total_points": 104,
            "rank": 11,
            "picks": [
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Poipu Pauly",
            "total_points": 103,
            "rank": 12,
            "picks": [
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Sean",
            "total_points": 100,
            "rank": 13,
            "picks": [
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Karat Cake",
            "total_points": 95,
            "rank": 14,
            "picks": [
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Bijan Mustard",
            "total_points": 89,
            "rank": 15,
            "picks": [
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "snydermeister",
            "total_points": 83,
            "rank": 16,
            "picks": [
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Big daddy",
            "total_points": 77,
            "rank": 17,
            "picks": [
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        },
        {
            "name": "Hails (:)",
            "total_points": 69,
            "rank": 18,
            "picks": [
                # Need to fill in actual picks from screenshot
                {"team": "TBD", "confidence": 16, "correct": True},
                {"team": "TBD", "confidence": 15, "correct": True},
                {"team": "TBD", "confidence": 14, "correct": True},
                {"team": "TBD", "confidence": 13, "correct": True},
                {"team": "TBD", "confidence": 12, "correct": True},
                {"team": "TBD", "confidence": 11, "correct": True},
                {"team": "TBD", "confidence": 10, "correct": True},
                {"team": "TBD", "confidence": 9, "correct": True},
                {"team": "TBD", "confidence": 8, "correct": True},
                {"team": "TBD", "confidence": 7, "correct": True},
                {"team": "TBD", "confidence": 6, "correct": True},
                {"team": "TBD", "confidence": 5, "correct": True},
                {"team": "TBD", "confidence": 4, "correct": True},
                {"team": "TBD", "confidence": 3, "correct": True},
                {"team": "TBD", "confidence": 2, "correct": True},
                {"team": "TBD", "confidence": 1, "correct": True}
            ]
        }
    ]
    
    # Create markdown documentation for validation
    print("Creating Week 1 validation markdown...")
    create_week1_validation_markdown(all_participants, week1_games)
    
    print(f"✅ Created validation markdown for all {len(all_participants)} participants")
    print("📋 Review the markdown file and fill in the actual picks from screenshots")
    print("💾 Once validated, we can store in database")

def create_week1_validation_markdown(participants, games):
    """Create comprehensive validation markdown for Week 1"""
    
    # Create output directory if it doesn't exist
    os.makedirs("data/outputs/2025/pool-results", exist_ok=True)
    
    # Create markdown file
    with open("data/outputs/2025/pool-results/week1-validation-template.md", "w") as f:
        f.write("# Week 1 Pool Results - Validation Template\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Instructions\n\n")
        f.write("1. Fill in the actual picks from the Week 1 screenshots\n")
        f.write("2. Replace 'TBD' with the actual team names\n")
        f.write("3. Verify confidence points match the screenshots\n")
        f.write("4. Confirm correct/incorrect status based on actual results\n")
        f.write("5. Once validated, we'll store in database\n\n")
        
        # Game matchups
        f.write("## Game Matchups\n\n")
        for i, game in enumerate(games, 1):
            f.write(f"{i:2d}. {game['away']} @ {game['home']}\n")
        f.write("\n")
        
        # Results summary
        f.write("## Results Summary\n\n")
        f.write("| Rank | Participant | Total Points | Status |\n")
        f.write("|------|-------------|--------------|--------|\n")
        
        for participant in sorted(participants, key=lambda x: x['total_points'], reverse=True):
            f.write(f"| {participant['rank']} | {participant['name']} | {participant['total_points']} | ⏳ Pending |\n")
        
        f.write("\n")
        
        # Detailed picks template for each participant
        f.write("## Detailed Picks Template\n\n")
        f.write("**Copy this template for each participant and fill in the actual picks:**\n\n")
        
        f.write("```markdown\n")
        f.write("### [Participant Name] - [Total Points] points (Rank [X])\n\n")
        f.write("| Game | Pick | Confidence | Result |\n")
        f.write("|------|------|------------|--------|\n")
        
        for i, game in enumerate(games, 1):
            f.write(f"| {game['away']} @ {game['home']} | [TEAM_NAME] | [X] | [✅/❌] |\n")
        
        f.write("```\n\n")
        
        # Individual participant sections
        f.write("## Participant Data Entry\n\n")
        
        for participant in sorted(participants, key=lambda x: x['total_points'], reverse=True):
            f.write(f"### {participant['name']} - {participant['total_points']} points (Rank {participant['rank']})\n\n")
            
            f.write("| Game | Pick | Confidence | Result |\n")
            f.write("|------|------|------------|--------|\n")
            
            for i, pick in enumerate(participant['picks'], 1):
                game = games[i-1]
                team_name = pick['team'] if pick['team'] != 'TBD' else '[FILL_IN]'
                result = "✅" if pick['correct'] else "❌" if pick['team'] != 'TBD' else '[FILL_IN]'
                f.write(f"| {game['away']} @ {game['home']} | {team_name} | {pick['confidence']} | {result} |\n")
            
            f.write("\n")

if __name__ == "__main__":
    parse_all_week1_complete()

