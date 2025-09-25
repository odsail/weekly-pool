#!/usr/bin/env python3
"""
Database manager for NFL confidence pool data.
Handles SQLite database operations for picks, analysis, and team data.
"""
import sqlite3
import json
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os
from team_name_mapper import TeamNameMapper

class DatabaseManager:
    """Manages SQLite database operations for NFL confidence pool"""
    
    def __init__(self, db_path: str = "data/nfl_pool.db", version: str = None):
        if version:
            # Use versioned database path
            if version == "v2":
                self.db_path = "data/nfl_pool_v2.db"
            elif version == "v1":
                self.db_path = "data/nfl_pool_v1.db"
            else:
                self.db_path = db_path
        else:
            self.db_path = db_path
        self.team_mapper = TeamNameMapper()
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Read and execute schema
            schema_path = os.path.join(os.path.dirname(__file__), "database_schema.sql")
            with open(schema_path, 'r') as f:
                schema = f.read()
            
            # Execute schema (SQLite doesn't support multiple statements in one execute)
            for statement in schema.split(';'):
                statement = statement.strip()
                if statement:
                    try:
                        conn.execute(statement)
                    except sqlite3.OperationalError as e:
                        if "already exists" in str(e):
                            continue  # Table already exists, skip
                        else:
                            raise e
            
            conn.commit()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    # Team operations
    def upsert_team(self, name: str, abbreviation: str, conference: str, division: str) -> int:
        """Insert or update team, return team ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO teams (name, abbreviation, conference, division)
                VALUES (?, ?, ?, ?)
            """, (name, abbreviation, conference, division))
            conn.commit()
            return cursor.lastrowid
    
    def get_team_id(self, name: str) -> Optional[int]:
        """Get team ID by name"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM teams WHERE name = ?", (name,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def _ensure_team_exists(self, team_name: str) -> int:
        """Ensure team exists in database, create if not"""
        team_id = self.get_team_id(team_name)
        if team_id:
            return team_id
        
        # Get team info from mapper
        team_info = self.team_mapper.get_team_info(team_name)
        if not team_info:
            raise ValueError(f"Unknown team: {team_name}")
        
        # Create team
        return self.upsert_team(
            team_name,
            team_info['abbreviation'],
            team_info['conference'],
            team_info['division']
        )
    
    # Game operations
    def upsert_game(self, season_year: int, week: int, home_team: str, away_team: str, 
                   game_date: str, home_score: Optional[int] = None, 
                   away_score: Optional[int] = None) -> int:
        """Insert or update game, return game ID"""
        # Map team names to current standardized names
        mapped_home_team = self.team_mapper.map_team_name(home_team)
        mapped_away_team = self.team_mapper.map_team_name(away_team)
        
        # Skip invalid games (Pro Bowl, etc.)
        if not mapped_home_team or not mapped_away_team:
            raise ValueError(f"Invalid game: {home_team} vs {away_team} (Pro Bowl or invalid teams)")
        
        # Ensure teams exist in database
        home_team_id = self._ensure_team_exists(mapped_home_team)
        away_team_id = self._ensure_team_exists(mapped_away_team)
        
        total_points = None
        margin = None
        winner_team_id = None
        is_completed = False
        
        if home_score is not None and away_score is not None:
            total_points = home_score + away_score
            margin = abs(home_score - away_score)
            winner_team_id = home_team_id if home_score > away_score else away_team_id
            is_completed = True
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO games 
                (season_year, week, home_team_id, away_team_id, game_date, 
                 home_score, away_score, total_points, margin, winner_team_id, is_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (season_year, week, home_team_id, away_team_id, game_date,
                  home_score, away_score, total_points, margin, winner_team_id, is_completed))
            conn.commit()
            return cursor.lastrowid
    
    def get_game_id(self, season_year: int, week: int, home_team: str, away_team: str) -> Optional[int]:
        """Get game ID by season, week, and teams"""
        home_team_id = self.get_team_id(home_team)
        away_team_id = self.get_team_id(away_team)
        
        if not home_team_id or not away_team_id:
            return None
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM games 
                WHERE season_year = ? AND week = ? 
                AND home_team_id = ? AND away_team_id = ?
            """, (season_year, week, home_team_id, away_team_id))
            result = cursor.fetchone()
            return result[0] if result else None
    
    # Odds operations
    def insert_odds(self, game_id: int, bookmaker: str, home_ml: Optional[int], 
                   away_ml: Optional[int], total_points: Optional[float],
                   home_win_prob: Optional[float], away_win_prob: Optional[float]) -> int:
        """Insert odds data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO odds 
                (game_id, bookmaker, home_ml, away_ml, total_points, 
                 home_win_prob, away_win_prob, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (game_id, bookmaker, home_ml, away_ml, total_points,
                  home_win_prob, away_win_prob, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid
    
    # Picks operations
    def insert_pick(self, game_id: int, season_year: int, week: int, 
                   pick_team: str, confidence_points: int, win_probability: float,
                   total_points_prediction: Optional[int] = None) -> int:
        """Insert a pick"""
        pick_team_id = self.get_team_id(pick_team)
        if not pick_team_id:
            raise ValueError(f"Team not found: {pick_team}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO picks 
                (game_id, season_year, week, pick_team_id, confidence_points, 
                 win_probability, total_points_prediction)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (game_id, season_year, week, pick_team_id, confidence_points,
                  win_probability, total_points_prediction))
            conn.commit()
            return cursor.lastrowid
    
    def update_pick_result(self, pick_id: int, is_correct: bool):
        """Update pick with result"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE picks SET is_correct = ? WHERE id = ?
            """, (is_correct, pick_id))
            conn.commit()
    
    # Analysis operations
    def insert_analysis_result(self, season_year: int, week: int, 
                             overall_accuracy: float, correct_picks: int, 
                             total_picks: int, avg_total_points_error: float,
                             blowouts_count: int, close_games_count: int, 
                             avg_margin: float) -> int:
        """Insert analysis results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO analysis_results 
                (season_year, week, overall_accuracy, correct_picks, total_picks,
                 avg_total_points_error, blowouts_count, close_games_count, 
                 avg_margin, analysis_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (season_year, week, overall_accuracy, correct_picks, total_picks,
                  avg_total_points_error, blowouts_count, close_games_count,
                  avg_margin, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid
    
    # Query operations for ML
    def get_team_performance_history(self, team: str, weeks_back: int = 4) -> pd.DataFrame:
        """Get team performance history for ML features"""
        team_id = self.get_team_id(team)
        if not team_id:
            return pd.DataFrame()
        
        with self.get_connection() as conn:
            query = """
                SELECT tp.season_year, tp.week, tp.wins, tp.losses, tp.points_scored,
                       tp.points_allowed, tp.point_differential, tp.win_percentage
                FROM team_performance tp
                WHERE tp.team_id = ?
                ORDER BY tp.season_year DESC, tp.week DESC
                LIMIT ?
            """
            return pd.read_sql_query(query, conn, params=(team_id, weeks_back))
    
    def get_confidence_accuracy_history(self, weeks_back: int = 8) -> pd.DataFrame:
        """Get confidence point accuracy history for ML features"""
        with self.get_connection() as conn:
            query = """
                SELECT ca.confidence_points, ca.accuracy, ar.season_year, ar.week
                FROM confidence_accuracy ca
                JOIN analysis_results ar ON ca.analysis_id = ar.id
                ORDER BY ar.season_year DESC, ar.week DESC
                LIMIT ?
            """
            return pd.read_sql_query(query, conn, params=(weeks_back * 16,))  # ~16 games per week
    
    def get_game_features(self, season_year: int, week: int) -> pd.DataFrame:
        """Get comprehensive game features for ML model"""
        with self.get_connection() as conn:
            query = """
                SELECT 
                    g.id as game_id,
                    ht.name as home_team,
                    at.name as away_team,
                    g.game_date,
                    o.home_ml,
                    o.away_ml,
                    o.total_points as predicted_total,
                    o.home_win_prob,
                    o.away_win_prob,
                    p.pick_team_id,
                    p.confidence_points,
                    p.win_probability,
                    p.total_points_prediction,
                    p.is_correct,
                    g.home_score,
                    g.away_score,
                    g.total_points as actual_total,
                    g.margin,
                    g.winner_team_id
                FROM games g
                JOIN teams ht ON g.home_team_id = ht.id
                JOIN teams at ON g.away_team_id = at.id
                LEFT JOIN odds o ON g.id = o.game_id
                LEFT JOIN picks p ON g.id = p.game_id
                WHERE g.season_year = ? AND g.week = ?
                ORDER BY p.confidence_points DESC
            """
            return pd.read_sql_query(query, conn, params=(season_year, week))
    
    def get_all_picks_for_ml(self) -> pd.DataFrame:
        """Get all picks data for ML training"""
        with self.get_connection() as conn:
            query = """
                SELECT 
                    p.id,
                    p.season_year,
                    p.week,
                    p.confidence_points,
                    p.win_probability,
                    p.total_points_prediction,
                    p.is_correct,
                    ht.name as home_team,
                    at.name as away_team,
                    pt.name as pick_team,
                    o.home_ml,
                    o.away_ml,
                    o.total_points as odds_total,
                    g.home_score,
                    g.away_score,
                    g.total_points as actual_total,
                    g.margin
                FROM picks p
                JOIN games g ON p.game_id = g.id
                JOIN teams ht ON g.home_team_id = ht.id
                JOIN teams at ON g.away_team_id = at.id
                JOIN teams pt ON p.pick_team_id = pt.id
                LEFT JOIN odds o ON g.id = o.game_id
                WHERE p.is_correct IS NOT NULL
                ORDER BY p.season_year, p.week, p.confidence_points DESC
            """
            return pd.read_sql_query(query, conn)
    
    # Migration helpers
    def migrate_csv_data(self, csv_path: str, season_year: int, week: int):
        """Migrate CSV picks data to database"""
        df = pd.read_csv(csv_path)
        
        for _, row in df.iterrows():
            # Extract team names from separate columns
            home_team = row['home_team']
            away_team = row['away_team']
            
            # Get or create game
            game_id = self.get_game_id(season_year, week, home_team, away_team)
            if not game_id:
                # Create game (without scores since this is picks data)
                game_id = self.upsert_game(season_year, week, home_team, away_team, 
                                         row.get('commence_time', ''))
            
            # Insert pick
            self.insert_pick(game_id, season_year, week, row['pick_team'], 
                           row['confidence_points'], row['pick_prob'],
                           row.get('total_points'))
    
    def migrate_analysis_data(self, analysis_file: str, season_year: int, week: int):
        """Migrate JSON analysis data to database"""
        with open(analysis_file, 'r') as f:
            analysis = json.load(f)
        
        # Insert main analysis result
        analysis_id = self.insert_analysis_result(
            season_year, week,
            analysis['overall_accuracy'],
            analysis['correct_picks'],
            analysis['total_picks'],
            analysis.get('avg_error', 0.0),  # Use avg_error field
            analysis['dominance_analysis']['blowouts'],
            analysis['dominance_analysis']['close_games'],
            analysis['dominance_analysis']['average_margin']
        )
        
        # Insert confidence accuracy data
        for conf_points, data in analysis['confidence_accuracy'].items():
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO confidence_accuracy 
                    (analysis_id, confidence_points, correct_picks, total_picks, accuracy)
                    VALUES (?, ?, ?, ?, ?)
                """, (analysis_id, int(conf_points), data['correct'], 
                      data['total'], data['accuracy']))
                conn.commit()
    
    # Expert picks operations
    def insert_expert_pick(self, game_id: int, expert_name: str, pick_team: str, 
                          spread: float = None, result: str = None, confidence: int = 10) -> int:
        """Insert expert pick into database"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO expert_picks 
                (game_id, expert_name, pick_team, spread, result, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (game_id, expert_name, pick_team, spread, result, confidence))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_expert_picks_for_game(self, game_id: int) -> pd.DataFrame:
        """Get all expert picks for a specific game"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT expert_name, pick_team, spread, result, confidence
                FROM expert_picks
                WHERE game_id = ?
                ORDER BY expert_name
            """, (game_id,))
            
            columns = [description[0] for description in cursor.description]
            return pd.DataFrame([dict(zip(columns, row)) for row in cursor.fetchall()])
    
    def get_expert_consensus(self, game_id: int) -> dict:
        """Get expert consensus for a game"""
        
        expert_picks = self.get_expert_picks_for_game(game_id)
        
        if expert_picks.empty:
            return {"consensus_team": None, "consensus_percentage": 0.0, "total_experts": 0}
        
        # Count picks for each team
        pick_counts = expert_picks['pick_team'].value_counts()
        total_experts = len(expert_picks)
        
        if len(pick_counts) > 0:
            consensus_team = pick_counts.index[0]
            consensus_percentage = pick_counts.iloc[0] / total_experts
        else:
            consensus_team = None
            consensus_percentage = 0.0
        
        return {
            "consensus_team": consensus_team,
            "consensus_percentage": consensus_percentage,
            "total_experts": total_experts,
            "pick_breakdown": pick_counts.to_dict()
        }
    
    # Pool results operations
    def insert_pool_result(self, season_year: int, week: int, participant_name: str, 
                          game_id: int, pick_team_id: int, confidence_points: int, 
                          is_correct: bool, total_weekly_score: int = None, 
                          weekly_rank: int = None) -> int:
        """Insert a pool result record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO pool_results 
                (season_year, week, participant_name, game_id, pick_team_id, 
                 confidence_points, is_correct, total_weekly_score, weekly_rank)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (season_year, week, participant_name, game_id, pick_team_id, 
                  confidence_points, is_correct, total_weekly_score, weekly_rank))
            return cursor.lastrowid
    
    def get_pool_results_for_week(self, season_year: int, week: int) -> List[Dict]:
        """Get all pool results for a specific week"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pr.*, t.name as pick_team_name, ht.name as home_team, at.name as away_team
                FROM pool_results pr
                JOIN teams t ON pr.pick_team_id = t.id
                JOIN games g ON pr.game_id = g.id
                JOIN teams ht ON g.home_team_id = ht.id
                JOIN teams at ON g.away_team_id = at.id
                WHERE pr.season_year = ? AND pr.week = ?
                ORDER BY pr.participant_name, pr.confidence_points DESC
            """, (season_year, week))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_participant_weekly_summary(self, season_year: int, week: int) -> List[Dict]:
        """Get weekly summary for all participants"""
        with self.get_connection() as conn:
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
            """, (season_year, week))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_top_performers_analysis(self, season_year: int, week: int, top_n: int = 5) -> Dict:
        """Analyze top performers' pick patterns"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    pr.participant_name,
                    pr.pick_team_id,
                    t.name as pick_team,
                    pr.confidence_points,
                    pr.is_correct,
                    ht.name as home_team,
                    at.name as away_team
                FROM pool_results pr
                JOIN teams t ON pr.pick_team_id = t.id
                JOIN games g ON pr.game_id = g.id
                JOIN teams ht ON g.home_team_id = ht.id
                JOIN teams at ON g.away_team_id = at.id
                WHERE pr.season_year = ? AND pr.week = ?
                AND pr.participant_name IN (
                    SELECT participant_name 
                    FROM pool_results 
                    WHERE season_year = ? AND week = ?
                    GROUP BY participant_name
                    ORDER BY SUM(CASE WHEN is_correct = 1 THEN confidence_points ELSE 0 END) DESC
                    LIMIT ?
                )
                ORDER BY pr.participant_name, pr.confidence_points DESC
            """, (season_year, week, season_year, week, top_n))
            
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Group by participant
            participants = {}
            for result in results:
                participant = result['participant_name']
                if participant not in participants:
                    participants[participant] = []
                participants[participant].append(result)
            
            return participants
