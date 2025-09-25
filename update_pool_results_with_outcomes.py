#!/usr/bin/env python3
"""
Update pool results with actual game outcomes based on screenshot color coding.
Green = Win, Red = Loss, Blank = Missed pick (16 point loss)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
from datetime import datetime

def update_pool_results_with_outcomes():
    """Update pool results with actual game outcomes from screenshots"""
    
    print("🎯 Updating Pool Results with Actual Outcomes")
    print("=" * 60)
    
    db_manager = DatabaseManager(version="v2")
    
    # Update each week with actual outcomes
    update_week1_outcomes(db_manager)
    update_week2_outcomes(db_manager)
    update_week3_outcomes(db_manager)
    
    print("\n✅ All pool results updated with actual outcomes!")

def update_week1_outcomes(db_manager):
    """Update Week 1 outcomes based on screenshot color coding"""
    
    print("\n📅 Updating Week 1 Outcomes...")
    
    # Week 1 game outcomes (from screenshot analysis) - using database format
    week1_outcomes = {
        "Philadelphia Eagles @ Dallas Cowboys": "Philadelphia Eagles",      # PHI won (all green)
        "Los Angeles Chargers @ Kansas City Chiefs": "Los Angeles Chargers",       # LAC won (LAC picks green, KC picks red)
        "Atlanta Falcons @ Tampa Bay Buccaneers": "Tampa Bay Buccaneers",        # TB won (TB picks green, ATL picks red)
        "New York Jets @ Pittsburgh Steelers": "Pittsburgh Steelers",      # PIT won (PIT picks green, NYJ picks red)
        "Indianapolis Colts @ Miami Dolphins": "Miami Dolphins",      # MIA won (MIA picks green, IND picks red)
        "Jacksonville Jaguars @ Carolina Panthers": "Jacksonville Jaguars",      # JAX won (JAX picks green, CAR picks red)
        "Washington Commanders @ New York Giants": "Washington Commanders",      # WAS won (WAS picks green, NYG picks red)
        "New Orleans Saints @ Arizona Cardinals": "Arizona Cardinals",       # ARI won (ARI picks green, NO picks red)
        "Cleveland Browns @ Cincinnati Bengals": "Cincinnati Bengals",      # CIN won (all CIN picks green)
        "New England Patriots @ Las Vegas Raiders": "Las Vegas Raiders",         # LV won (LV picks green, NE picks red)
        "Seattle Seahawks @ San Francisco 49ers": "San Francisco 49ers",        # SF won (SF picks green, SEA picks red)
        "Denver Broncos @ Tennessee Titans": "Denver Broncos",      # DEN won (all DEN picks green)
        "Green Bay Packers @ Detroit Lions": "Detroit Lions",       # DET won (DET picks green, GB picks red)
        "Los Angeles Rams @ Houston Texans": "Los Angeles Rams",      # LAR won (LAR picks green, HOU picks red)
        "Buffalo Bills @ Baltimore Ravens": "Buffalo Bills",      # BUF won (BUF picks green, BAL picks red)
        "Chicago Bears @ Minnesota Vikings": "Minnesota Vikings"       # MIN won (MIN picks green, CHI picks red)
    }
    
    update_week_outcomes(db_manager, 1, week1_outcomes)

def update_week2_outcomes(db_manager):
    """Update Week 2 outcomes based on screenshot color coding"""
    
    print("\n📅 Updating Week 2 Outcomes...")
    
    # Week 2 game outcomes (from screenshot analysis) - using database format
    week2_outcomes = {
        "Green Bay Packers @ Washington Commanders": "Green Bay Packers",        # GB won (GB picks green, WAS picks red)
        "Tennessee Titans @ Los Angeles Rams": "Los Angeles Rams",      # LAR won (LAR picks green, TEN picks red)
        "Pittsburgh Steelers @ Seattle Seahawks": "Pittsburgh Steelers",      # PIT won (PIT picks green, SEA picks red)
        "New York Jets @ Buffalo Bills": "Buffalo Bills",      # BUF won (BUF picks green, NYJ picks red)
        "Detroit Lions @ Chicago Bears": "Detroit Lions",      # DET won (DET picks green, CHI picks red)
        "Dallas Cowboys @ New York Giants": "Dallas Cowboys",      # DAL won (DAL picks green, NYG picks red)
        "Baltimore Ravens @ Cleveland Browns": "Baltimore Ravens",      # BAL won (BAL picks green, CLE picks red)
        "New Orleans Saints @ San Francisco 49ers": "San Francisco 49ers",         # SF won (SF picks green, NO picks red)
        "Miami Dolphins @ New England Patriots": "Miami Dolphins",       # MIA won (MIA picks green, NE picks red)
        "Cincinnati Bengals @ Jacksonville Jaguars": "Cincinnati Bengals",      # CIN won (CIN picks green, JAX picks red)
        "Arizona Cardinals @ Carolina Panthers": "Arizona Cardinals",      # ARI won (ARI picks green, CAR picks red)
        "Indianapolis Colts @ Denver Broncos": "Indianapolis Colts",      # IND won (IND picks green, DEN picks red)
        "Kansas City Chiefs @ Philadelphia Eagles": "Philadelphia Eagles",       # PHI won (PHI picks green, KC picks red)
        "Minnesota Vikings @ Atlanta Falcons": "Minnesota Vikings",      # MIN won (MIN picks green, ATL picks red)
        "Houston Texans @ Tampa Bay Buccaneers": "Tampa Bay Buccaneers",        # TB won (TB picks green, HOU picks red)
        "Las Vegas Raiders @ Los Angeles Chargers": "Los Angeles Chargers"        # LAC won (LAC picks green, LV picks red)
    }
    
    update_week_outcomes(db_manager, 2, week2_outcomes)

def update_week3_outcomes(db_manager):
    """Update Week 3 outcomes based on screenshot color coding"""
    
    print("\n📅 Updating Week 3 Outcomes...")
    
    # Week 3 game outcomes (from screenshot analysis) - using database format
    week3_outcomes = {
        "Buffalo Bills @ Miami Dolphins": "Buffalo Bills",      # BUF won (all BUF picks green)
        "Tennessee Titans @ Indianapolis Colts": "Indianapolis Colts",      # IND won (most IND picks green, some TEN picks red)
        "New England Patriots @ Pittsburgh Steelers": "Pittsburgh Steelers",       # PIT won (most PIT picks green, some NE picks red)
        "Tampa Bay Buccaneers @ New York Jets": "Tampa Bay Buccaneers",        # TB won (all TB picks green)
        "Washington Commanders @ Las Vegas Raiders": "Washington Commanders",       # WAS won (most WAS picks green, some LV picks red)
        "Philadelphia Eagles @ Los Angeles Rams": "Philadelphia Eagles",      # PHI won (most PHI picks green, some LAR picks red)
        "Carolina Panthers @ Atlanta Falcons": "Carolina Panthers",      # CAR won (many ATL picks red, some CAR picks green)
        "Minnesota Vikings @ Cincinnati Bengals": "Minnesota Vikings",      # MIN won (many MIN picks green, some CIN picks red)
        "Jacksonville Jaguars @ Houston Texans": "Jacksonville Jaguars",      # JAX won (many JAX picks green, some HOU picks red)
        "Cleveland Browns @ Green Bay Packers": "Cleveland Browns",       # CLE won (all GB picks red - universal incorrect pick)
        "Los Angeles Chargers @ Denver Broncos": "Los Angeles Chargers",      # LAC won (many LAC picks green, some DEN picks red)
        "Seattle Seahawks @ New Orleans Saints": "Seattle Seahawks",       # SEA won (all SEA picks green)
        "San Francisco 49ers @ Arizona Cardinals": "San Francisco 49ers",        # SF won (many SF picks green, some ARI picks red)
        "Chicago Bears @ Dallas Cowboys": "Chicago Bears",      # CHI won (many DAL picks red, some CHI picks green)
        "New York Giants @ Kansas City Chiefs": "Kansas City Chiefs",        # KC won (all KC picks green)
        "Baltimore Ravens @ Detroit Lions": "Detroit Lions"       # DET won (many BAL picks red, some DET picks green)
    }
    
    update_week_outcomes(db_manager, 3, week3_outcomes)

def update_week_outcomes(db_manager, week, game_outcomes):
    """Update outcomes for a specific week"""
    
    print(f"  🏈 Processing {len(game_outcomes)} games for Week {week}")
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get all picks for this week
        cursor.execute("""
            SELECT pr.id, pr.participant_name, pr.pick_team_id, pr.confidence_points,
                   t.name as pick_team, ht.name as home_team, at.name as away_team
            FROM pool_results pr
            JOIN teams t ON pr.pick_team_id = t.id
            JOIN games g ON pr.game_id = g.id
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            WHERE pr.season_year = 2025 AND pr.week = ?
        """, (week,))
        
        picks = cursor.fetchall()
        
        print(f"    📊 Processing {len(picks)} picks")
        
        # Update each pick
        for pick_id, participant, pick_team_id, confidence, pick_team, home_team, away_team in picks:
            # Determine if pick was correct
            game_key = f"{home_team} @ {away_team}"
            actual_winner = game_outcomes.get(game_key)
            
            if actual_winner:
                is_correct = (pick_team == actual_winner)
                
                # Update the pick with outcome
                cursor.execute("""
                    UPDATE pool_results 
                    SET is_correct = ?
                    WHERE id = ?
                """, (is_correct, pick_id))
                
                if is_correct:
                    print(f"      ✅ {participant}: {pick_team} ({confidence} pts) - CORRECT")
                else:
                    print(f"      ❌ {participant}: {pick_team} ({confidence} pts) - INCORRECT (actual: {actual_winner})")
            else:
                print(f"      ⚠️  {participant}: {pick_team} - Game not found: {game_key}")
        
        conn.commit()
        print(f"    💾 Updated {len(picks)} picks for Week {week}")

def generate_updated_performance_analysis(db_manager):
    """Generate updated performance analysis with actual outcomes"""
    
    print("\n📊 Generating Updated Performance Analysis...")
    
    # Analyze FundaySunday's actual performance
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pr.week, pr.confidence_points, pr.is_correct, t.name as pick_team,
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
        
        # Calculate performance
        weekly_performance = {}
        total_correct = 0
        total_picks = len(results)
        total_points = 0
        
        for week, confidence, is_correct, pick_team, home_team, away_team in results:
            if week not in weekly_performance:
                weekly_performance[week] = {'correct': 0, 'total': 0, 'points': 0}
            
            weekly_performance[week]['total'] += 1
            if is_correct:
                weekly_performance[week]['correct'] += 1
                weekly_performance[week]['points'] += confidence
                total_correct += 1
                total_points += confidence
        
        # Calculate accuracy rates
        for week in weekly_performance:
            week_data = weekly_performance[week]
            week_data['accuracy'] = week_data['correct'] / week_data['total']
        
        overall_accuracy = total_correct / total_picks if total_picks > 0 else 0
        
        print(f"\n🎯 FundaySunday's Actual Performance:")
        print(f"  📊 Overall: {total_correct}/{total_picks} correct ({overall_accuracy:.1%})")
        print(f"  🏆 Total Points: {total_points}")
        
        for week in sorted(weekly_performance.keys()):
            week_data = weekly_performance[week]
            print(f"  📅 Week {week}: {week_data['correct']}/{week_data['total']} correct ({week_data['accuracy']:.1%}) - {week_data['points']} points")
        
        return {
            'weekly_performance': weekly_performance,
            'overall_accuracy': overall_accuracy,
            'total_correct': total_correct,
            'total_picks': total_picks,
            'total_points': total_points
        }

if __name__ == "__main__":
    update_pool_results_with_outcomes()
    generate_updated_performance_analysis(DatabaseManager(version="v2"))
