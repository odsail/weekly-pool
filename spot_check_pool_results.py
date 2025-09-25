#!/usr/bin/env python3
"""
Spot check pool results to verify data accuracy.
Use this to check specific games, participants, or weeks.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager

def spot_check_pool_results():
    """Interactive spot checking of pool results"""
    
    db_manager = DatabaseManager(version="v2")
    
    print("🔍 Pool Results Spot Checker")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Check specific game")
        print("2. Check specific participant")
        print("3. Check week summary")
        print("4. Check your picks (FundaySunday)")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            check_specific_game(db_manager)
        elif choice == "2":
            check_specific_participant(db_manager)
        elif choice == "3":
            check_week_summary(db_manager)
        elif choice == "4":
            check_fundaysunday_picks(db_manager)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def check_specific_game(db_manager):
    """Check picks for a specific game"""
    
    print("\n🔍 Check Specific Game")
    print("-" * 30)
    
    season = input("Season year (2025): ").strip() or "2025"
    week = input("Week (1-3): ").strip()
    team = input("Team name (e.g., 'Buffalo Bills'): ").strip()
    
    if not week or not team:
        print("Week and team are required!")
        return
    
    try:
        week = int(week)
        season = int(season)
    except ValueError:
        print("Invalid week or season!")
        return
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pr.participant_name, t.name as pick_team, pr.confidence_points, pr.is_correct,
                   ht.name as home_team, at.name as away_team
            FROM pool_results pr
            JOIN teams t ON pr.pick_team_id = t.id
            JOIN games g ON pr.game_id = g.id
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            WHERE pr.season_year = ? AND pr.week = ?
            AND (ht.name LIKE ? OR at.name LIKE ?)
            ORDER BY pr.confidence_points DESC
        """, (season, week, f"%{team}%", f"%{team}%"))
        
        results = cursor.fetchall()
        
        if results:
            home_team, away_team = results[0][4], results[0][5]
            print(f"\nGame: {away_team} @ {home_team}")
            print(f"Found {len(results)} picks:")
            print("-" * 50)
            
            for participant, pick_team, confidence, is_correct, _, _ in results:
                status = "✅" if is_correct else "❌"
                print(f"{participant:15} | {pick_team:20} | {confidence:2d} pts | {status}")
        else:
            print(f"No picks found for {team} in Week {week}")

def check_specific_participant(db_manager):
    """Check picks for a specific participant"""
    
    print("\n🔍 Check Specific Participant")
    print("-" * 30)
    
    season = input("Season year (2025): ").strip() or "2025"
    week = input("Week (1-3): ").strip()
    participant = input("Participant name: ").strip()
    
    if not week or not participant:
        print("Week and participant are required!")
        return
    
    try:
        week = int(week)
        season = int(season)
    except ValueError:
        print("Invalid week or season!")
        return
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.name as pick_team, pr.confidence_points, pr.is_correct,
                   ht.name as home_team, at.name as away_team
            FROM pool_results pr
            JOIN teams t ON pr.pick_team_id = t.id
            JOIN games g ON pr.game_id = g.id
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            WHERE pr.season_year = ? AND pr.week = ? AND pr.participant_name = ?
            ORDER BY pr.confidence_points DESC
        """, (season, week, participant))
        
        results = cursor.fetchall()
        
        if results:
            print(f"\n{participant} - Week {week} Picks:")
            print("-" * 50)
            
            for pick_team, confidence, is_correct, home_team, away_team in results:
                status = "✅" if is_correct else "❌"
                print(f"{away_team} @ {home_team}")
                print(f"  Pick: {pick_team} ({confidence} pts) {status}")
                print()
        else:
            print(f"No picks found for {participant} in Week {week}")

def check_week_summary(db_manager):
    """Check week summary"""
    
    print("\n🔍 Check Week Summary")
    print("-" * 30)
    
    season = input("Season year (2025): ").strip() or "2025"
    week = input("Week (1-3): ").strip()
    
    if not week:
        print("Week is required!")
        return
    
    try:
        week = int(week)
        season = int(season)
    except ValueError:
        print("Invalid week or season!")
        return
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                participant_name,
                COUNT(*) as total_picks,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
                ROUND(SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as accuracy,
                SUM(CASE WHEN is_correct = 1 THEN confidence_points ELSE 0 END) as total_score,
                AVG(total_weekly_score) as avg_weekly_score,
                AVG(weekly_rank) as avg_rank
            FROM pool_results 
            WHERE season_year = ? AND week = ?
            GROUP BY participant_name
            ORDER BY total_score DESC
        """, (season, week))
        
        results = cursor.fetchall()
        
        if results:
            print(f"\nWeek {week} Summary:")
            print("-" * 80)
            print(f"{'Participant':<15} | {'Score':<5} | {'Correct':<8} | {'Accuracy':<8} | {'Rank':<4}")
            print("-" * 80)
            
            for participant, total_picks, correct_picks, accuracy, total_score, avg_weekly_score, avg_rank in results:
                print(f"{participant:<15} | {total_score:<5} | {correct_picks}/{total_picks:<6} | {accuracy:<7}% | {avg_rank:<4.0f}")
        else:
            print(f"No results found for Week {week}")

def check_fundaysunday_picks(db_manager):
    """Check FundaySunday's picks across all weeks"""
    
    print("\n🔍 FundaySunday's Picks")
    print("-" * 30)
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pr.week, t.name as pick_team, pr.confidence_points, pr.is_correct,
                   ht.name as home_team, at.name as away_team
            FROM pool_results pr
            JOIN teams t ON pr.pick_team_id = t.id
            JOIN games g ON pr.game_id = g.id
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            WHERE pr.season_year = 2025 AND pr.participant_name = 'FundaySunday'
            ORDER BY pr.week, pr.confidence_points DESC
        """)
        
        results = cursor.fetchall()
        
        if results:
            current_week = None
            for week, pick_team, confidence, is_correct, home_team, away_team in results:
                if week != current_week:
                    current_week = week
                    print(f"\nWeek {week} Picks:")
                    print("-" * 50)
                
                status = "✅" if is_correct else "❌"
                print(f"{away_team} @ {home_team}")
                print(f"  Pick: {pick_team} ({confidence} pts) {status}")
                print()
        else:
            print("No picks found for FundaySunday")

if __name__ == "__main__":
    spot_check_pool_results()

