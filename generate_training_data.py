#!/usr/bin/env python3
"""
Generate training data for ML model from historical games.
Creates synthetic picks based on historical game outcomes and betting odds.
"""

import pandas as pd
import numpy as np
from database_manager import DatabaseManager
from team_name_mapper import TeamNameMapper
import random

class TrainingDataGenerator:
    """Generates training data for ML model from historical games"""
    
    def __init__(self, version: str = "v2"):
        self.db_manager = DatabaseManager(version=version)
        self.team_mapper = TeamNameMapper()
    
    def generate_training_data(self, seasons: list = None):
        """Generate training data from historical games"""
        if seasons is None:
            seasons = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
        
        print(f"🔄 Generating training data for seasons: {seasons}")
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all games for the specified seasons
            placeholders = ','.join(['?' for _ in seasons])
            cursor.execute(f"""
                SELECT g.id, g.season_year, g.week, g.home_team_id, g.away_team_id,
                       g.home_score, g.away_score, g.margin, g.winner_team_id,
                       t1.name as home_team, t2.name as away_team
                FROM games g
                JOIN teams t1 ON g.home_team_id = t1.id
                JOIN teams t2 ON g.away_team_id = t2.id
                WHERE g.season_year IN ({placeholders})
                AND g.home_score IS NOT NULL AND g.away_score IS NOT NULL
                ORDER BY g.season_year, g.week
            """, seasons)
            
            games = cursor.fetchall()
            print(f"📊 Found {len(games)} games to process")
            
            training_picks = []
            
            for game in games:
                game_id, season, week, home_team_id, away_team_id, home_score, away_score, margin, winner_id, home_team, away_team = game
                
                # Skip playoff games for now (focus on regular season)
                if week > 18:
                    continue
                
                # Generate synthetic odds data (since we don't have real odds)
                synthetic_odds = self._generate_synthetic_odds(home_team, away_team, home_score, away_score)
                
                # Store synthetic odds in database
                self._store_synthetic_odds(game_id, synthetic_odds)
                
                # Generate multiple training examples for this game
                game_picks = self._generate_game_picks(
                    game_id, season, week, home_team_id, away_team_id,
                    home_team, away_team, home_score, away_score, margin, winner_id,
                    synthetic_odds
                )
                
                training_picks.extend(game_picks)
            
            print(f"📈 Generated {len(training_picks)} training picks")
            
            # Store training data in database
            self._store_training_picks(training_picks)
            
            return len(training_picks)
    
    def _generate_synthetic_odds(self, home_team: str, away_team: str, home_score: int, away_score: int) -> dict:
        """Generate synthetic betting odds based on game outcome"""
        # Calculate point differential
        point_diff = home_score - away_score
        
        # Generate synthetic moneyline odds based on point differential
        # Home team favored if they won by more points
        if point_diff > 0:
            # Home team won - they were likely favored
            home_ml = -150 - (point_diff * 10)  # More negative for bigger wins
            away_ml = 130 + (point_diff * 10)   # More positive for bigger losses
        else:
            # Away team won - they were likely favored
            away_ml = -150 - (abs(point_diff) * 10)
            home_ml = 130 + (abs(point_diff) * 10)
        
        # Add some randomness to make it more realistic
        home_ml += random.randint(-20, 20)
        away_ml += random.randint(-20, 20)
        
        # Calculate win probabilities
        home_prob = self._ml_to_prob(home_ml)
        away_prob = self._ml_to_prob(away_ml)
        
        # Normalize probabilities
        total_prob = home_prob + away_prob
        home_prob = home_prob / total_prob
        away_prob = away_prob / total_prob
        
        return {
            'home_ml': home_ml,
            'away_ml': away_ml,
            'home_win_prob': home_prob,
            'away_win_prob': away_prob,
            'total_points': home_score + away_score
        }
    
    def _ml_to_prob(self, ml: int) -> float:
        """Convert moneyline odds to probability"""
        if ml > 0:
            return 100 / (ml + 100)
        else:
            return abs(ml) / (abs(ml) + 100)
    
    def _generate_game_picks(self, game_id: int, season: int, week: int, 
                           home_team_id: int, away_team_id: int,
                           home_team: str, away_team: str, 
                           home_score: int, away_score: int, margin: int, winner_id: int,
                           odds: dict) -> list:
        """Generate multiple training picks for a single game"""
        picks = []
        
        # Generate picks with different confidence levels
        confidence_levels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        
        for conf_points in confidence_levels:
            # Determine which team to pick based on win probability
            if odds['home_win_prob'] > odds['away_win_prob']:
                pick_team_id = home_team_id
                pick_team = home_team
                win_prob = odds['home_win_prob']
            else:
                pick_team_id = away_team_id
                pick_team = away_team
                win_prob = odds['away_win_prob']
            
            # Determine if the pick was correct
            is_correct = (pick_team_id == winner_id)
            
            # Add some noise to make it more realistic
            # Sometimes pick the underdog based on confidence level
            if random.random() < 0.1:  # 10% chance to pick underdog
                if pick_team_id == home_team_id:
                    pick_team_id = away_team_id
                    pick_team = away_team
                    win_prob = odds['away_win_prob']
                else:
                    pick_team_id = home_team_id
                    pick_team = home_team
                    win_prob = odds['home_win_prob']
                
                is_correct = (pick_team_id == winner_id)
            
            pick = {
                'game_id': game_id,
                'season_year': season,
                'week': week,
                'pick_team_id': pick_team_id,
                'confidence_points': conf_points,
                'win_probability': win_prob,
                'total_points_prediction': odds['total_points'],
                'is_correct': is_correct
            }
            
            picks.append(pick)
        
        return picks
    
    def _store_training_picks(self, picks: list):
        """Store training picks in database"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            for pick in picks:
                cursor.execute("""
                    INSERT INTO picks 
                    (game_id, season_year, week, pick_team_id, confidence_points, 
                     win_probability, total_points_prediction, is_correct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pick['game_id'], pick['season_year'], pick['week'],
                    pick['pick_team_id'], pick['confidence_points'],
                    pick['win_probability'], pick['total_points_prediction'],
                    pick['is_correct']
                ))
            
            conn.commit()
            print(f"💾 Stored {len(picks)} training picks in database")
    
    def _store_synthetic_odds(self, game_id: int, odds: dict):
        """Store synthetic odds in database"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO odds 
                (game_id, bookmaker, home_ml, away_ml, total_points, 
                 home_win_prob, away_win_prob, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                game_id, 'synthetic', odds['home_ml'], odds['away_ml'], 
                odds['total_points'], odds['home_win_prob'], odds['away_win_prob'],
                '2024-01-01T00:00:00Z'  # Synthetic timestamp
            ))
            
            conn.commit()

def main():
    """Generate training data"""
    generator = TrainingDataGenerator()
    
    # Generate training data for recent seasons
    seasons = [2020, 2021, 2022, 2023, 2024]
    total_picks = generator.generate_training_data(seasons)
    
    print(f"✅ Generated {total_picks} training picks")
    print("💡 Ready to train ML model!")

if __name__ == "__main__":
    main()
