#!/usr/bin/env python3
"""
Parse Week 1 pool results from the provided screenshots and store in database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
from team_name_mapper import TeamNameMapper

def parse_week1_pool_results():
    """Parse Week 1 pool results based on the screenshot data"""
    
    # Initialize database manager
    db_manager = DatabaseManager(version="v2")
    team_mapper = TeamNameMapper()
    
    # Week 1 games data (from our database)
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
    
    # Pool results based on the corrected screenshot analysis
    pool_results = [
        # FundaySunday (You) - 8th place, 117 points Week 1
        {
            "participant": "FundaySunday",
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
            ],
            "total_score": 117,
            "rank": 8
        },
        # Top performer - Raiderjim (127 points)
        {
            "participant": "Raiderjim",
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
            ],
            "total_score": 127,
            "rank": 1
        }
    ]
    
    # Store results in database
    for participant_data in pool_results:
        participant_name = participant_data["participant"]
        total_score = participant_data["total_score"]
        rank = participant_data["rank"]
        
        for pick_data in participant_data["picks"]:
            team_name = pick_data["team"]
            confidence = pick_data["confidence"]
            is_correct = pick_data["correct"]
            
            # Find the game for this pick
            game_id = None
            pick_team_id = None
            
            for game in week1_games:
                if team_name in [game["home"], game["away"]]:
                    game_id = game["game_id"]
                    # Get team ID
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
                print(f"Stored: {participant_name} - {team_name} ({confidence} pts) - {'✓' if is_correct else '✗'}")
            else:
                print(f"Error: Could not find game or team for {team_name}")
    
    print(f"\nStored {len(pool_results)} participants' Week 1 results")
    
    # Generate analysis
    print("\n=== Week 1 Pool Analysis ===")
    summary = db_manager.get_participant_weekly_summary(2025, 1)
    for participant in summary:
        print(f"{participant['participant_name']}: {participant['total_score']} pts, {participant['accuracy']}% accuracy")

if __name__ == "__main__":
    parse_week1_pool_results()

