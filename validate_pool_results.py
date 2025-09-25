#!/usr/bin/env python3
"""
Validate pool results stored in database and generate spot-check reports.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
from datetime import datetime

def validate_pool_results():
    """Validate pool results and generate reports"""
    
    print("🔍 Validating Pool Results")
    print("=" * 50)
    
    db_manager = DatabaseManager(version="v2")
    
    # Generate validation reports
    generate_weekly_summaries(db_manager)
    generate_participant_summaries(db_manager)
    generate_spot_check_reports(db_manager)
    
    print("\n✅ Validation complete!")

def generate_weekly_summaries(db_manager):
    """Generate weekly summary reports"""
    
    print("\n📊 Generating Weekly Summaries...")
    
    for week in [1, 2, 3]:
        print(f"\n  📅 Week {week} Summary:")
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    participant_name,
                    COUNT(*) as total_picks,
                    SUM(confidence_points) as total_points
                FROM pool_results 
                WHERE season_year = 2025 AND week = ?
                GROUP BY participant_name
                ORDER BY total_points DESC
            """, (week,))
            
            results = cursor.fetchall()
            
            print(f"    👥 {len(results)} participants")
            print(f"    🏆 Top 5:")
            
            for i, (participant, total_picks, total_points) in enumerate(results[:5]):
                print(f"      {i+1}. {participant}: {total_points} pts ({total_picks} picks)")

def generate_participant_summaries(db_manager):
    """Generate participant summary reports"""
    
    print("\n👥 Generating Participant Summaries...")
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                participant_name,
                COUNT(*) as total_picks,
                SUM(confidence_points) as total_points,
                AVG(confidence_points) as avg_confidence
            FROM pool_results 
            WHERE season_year = 2025
            GROUP BY participant_name
            ORDER BY total_points DESC
        """)
        
        results = cursor.fetchall()
        
        print(f"  📊 {len(results)} participants across all weeks")
        print(f"  🏆 Top 10 Overall:")
        
        for i, (participant, total_picks, total_points, avg_confidence) in enumerate(results[:10]):
            print(f"    {i+1}. {participant}: {total_points} pts ({total_picks} picks, {avg_confidence:.1f} avg)")

def generate_spot_check_reports(db_manager):
    """Generate spot-check reports for validation"""
    
    print("\n🔍 Generating Spot-Check Reports...")
    
    # Check FundaySunday's picks for validation
    print("\n  👤 FundaySunday Spot Check:")
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pr.week, pr.confidence_points, t.name as pick_team,
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
        
        # Group by week
        week_data = {}
        for week, confidence, pick_team, home_team, away_team in results:
            if week not in week_data:
                week_data[week] = []
            week_data[week].append((confidence, pick_team, home_team, away_team))
        
        for week in sorted(week_data.keys()):
            print(f"\n    Week {week}:")
            for confidence, pick_team, home_team, away_team in week_data[week]:
                print(f"      {confidence} pts: {pick_team} ({away_team} @ {home_team})")
    
    # Check a few other participants
    print("\n  👥 Other Participants Spot Check:")
    
    other_participants = ['Sean', 'Poipu Pauly', 'Big Chuck']
    
    for participant in other_participants:
        print(f"\n    {participant} - Week 1 picks:")
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pr.confidence_points, t.name as pick_team,
                       ht.name as home_team, at.name as away_team
                FROM pool_results pr
                JOIN teams t ON pr.pick_team_id = t.id
                JOIN games g ON pr.game_id = g.id
                JOIN teams ht ON g.home_team_id = ht.id
                JOIN teams at ON g.away_team_id = at.id
                WHERE pr.season_year = 2025 AND pr.week = 1 AND pr.participant_name = ?
                ORDER BY pr.confidence_points DESC
                LIMIT 5
            """, (participant,))
            
            results = cursor.fetchall()
            
            for confidence, pick_team, home_team, away_team in results:
                print(f"      {confidence} pts: {pick_team} ({away_team} @ {home_team})")

def generate_validation_report_file(db_manager):
    """Generate a comprehensive validation report file"""
    
    print("\n📝 Generating Validation Report File...")
    
    filename = "data/outputs/2025/pool-results-validation-report.md"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, "w") as f:
        f.write("# Pool Results Validation Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary\n\n")
        f.write("This report validates the pool results data stored in the database.\n\n")
        
        # Weekly summaries
        f.write("## Weekly Summaries\n\n")
        
        for week in [1, 2, 3]:
            f.write(f"### Week {week}\n\n")
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        participant_name,
                        COUNT(*) as total_picks,
                        SUM(confidence_points) as total_points
                    FROM pool_results 
                    WHERE season_year = 2025 AND week = ?
                    GROUP BY participant_name
                    ORDER BY total_points DESC
                """, (week,))
                
                results = cursor.fetchall()
                
                f.write(f"**Participants:** {len(results)}\n\n")
                f.write("| Rank | Participant | Total Points | Total Picks |\n")
                f.write("|------|-------------|--------------|-------------|\n")
                
                for i, (participant, total_picks, total_points) in enumerate(results):
                    f.write(f"| {i+1} | {participant} | {total_points} | {total_picks} |\n")
                
                f.write("\n")
        
        # Overall standings
        f.write("## Overall Standings\n\n")
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    participant_name,
                    COUNT(*) as total_picks,
                    SUM(confidence_points) as total_points,
                    AVG(confidence_points) as avg_confidence
                FROM pool_results 
                WHERE season_year = 2025
                GROUP BY participant_name
                ORDER BY total_points DESC
            """)
            
            results = cursor.fetchall()
            
            f.write("| Rank | Participant | Total Points | Total Picks | Avg Confidence |\n")
            f.write("|------|-------------|--------------|-------------|----------------|\n")
            
            for i, (participant, total_picks, total_points, avg_confidence) in enumerate(results):
                f.write(f"| {i+1} | {participant} | {total_points} | {total_picks} | {avg_confidence:.1f} |\n")
        
        f.write("\n## Data Quality Checks\n\n")
        
        # Check for missing data
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as total_records
                FROM pool_results 
                WHERE season_year = 2025
            """)
            
            total_records = cursor.fetchone()[0]
            f.write(f"- **Total Records:** {total_records}\n")
            
            # Check for participants with incomplete picks
            cursor.execute("""
                SELECT participant_name, week, COUNT(*) as pick_count
                FROM pool_results 
                WHERE season_year = 2025
                GROUP BY participant_name, week
                HAVING pick_count < 16
                ORDER BY participant_name, week
            """)
            
            incomplete_picks = cursor.fetchall()
            
            if incomplete_picks:
                f.write(f"- **Incomplete Picks:** {len(incomplete_picks)} participants\n")
                f.write("  - Participants with fewer than 16 picks per week:\n")
                for participant, week, count in incomplete_picks:
                    f.write(f"    - {participant} (Week {week}): {count} picks\n")
            else:
                f.write("- **Incomplete Picks:** None (all participants have 16 picks per week)\n")
    
    print(f"  ✅ Validation report saved to: {filename}")

if __name__ == "__main__":
    validate_pool_results()
    generate_validation_report_file(DatabaseManager(version="v2"))

