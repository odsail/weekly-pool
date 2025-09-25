#!/usr/bin/env python3
"""
Generate improved synthetic training data using actual game margins and realistic confidence levels.
"""

import random
import math
from typing import List, Dict, Tuple
from database_manager import DatabaseManager
import pandas as pd

class ImprovedTrainingDataGenerator:
    """Generate realistic synthetic training data based on actual game outcomes"""
    
    def __init__(self):
        self.db_manager = DatabaseManager(version="v2")
    
    def generate_improved_training_data(self, start_year: int = 2020, end_year: int = 2024) -> int:
        """Generate improved training data using game margins and realistic confidence"""
        
        print(f"🔄 Generating improved training data for seasons: [{start_year}, {end_year}]")
        
        # Clear existing training data
        self._clear_existing_data()
        
        # Get all games with results
        all_games = self._get_games_with_results(start_year, end_year)
        print(f"📊 Found {len(all_games)} games with results")
        
        training_picks = []
        
        for game in all_games:
            # Skip playoff games for now (focus on regular season)
            if game['week'] > 18:
                continue
            
            # Generate realistic synthetic odds based on actual game outcome
            synthetic_odds = self._generate_realistic_odds(game)
            
            # Store synthetic odds
            self._store_synthetic_odds(game['id'], synthetic_odds)
            
            # Generate multiple realistic training examples
            game_picks = self._generate_realistic_picks(game, synthetic_odds)
            training_picks.extend(game_picks)
        
        # Store all picks
        self._store_training_picks(training_picks)
        
        print(f"📈 Generated {len(training_picks)} improved training picks")
        print(f"💾 Stored {len(training_picks)} training picks in database")
        
        return len(training_picks)
    
    def _clear_existing_data(self):
        """Clear existing training data"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM picks')
            cursor.execute('DELETE FROM odds')
            conn.commit()
    
    def _get_games_with_results(self, start_year: int, end_year: int) -> List[Dict]:
        """Get games with actual results"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.id, g.season_year, g.week, g.home_team_id, g.away_team_id,
                       t1.name as home_team, t2.name as away_team,
                       g.home_score, g.away_score
                FROM games g
                JOIN teams t1 ON g.home_team_id = t1.id
                JOIN teams t2 ON g.away_team_id = t2.id
                WHERE g.season_year BETWEEN ? AND ?
                AND g.home_score IS NOT NULL 
                AND g.away_score IS NOT NULL
                ORDER BY g.season_year, g.week
            """, (start_year, end_year))
            
            # Convert to list of dictionaries
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def _generate_realistic_odds(self, game: Dict) -> Dict:
        """Generate realistic odds based on actual game outcome and margin"""
        
        home_score = game['home_score']
        away_score = game['away_score']
        margin = abs(home_score - away_score)
        
        # Determine winner and margin
        if home_score > away_score:
            winner = 'home'
            margin = home_score - away_score
        else:
            winner = 'away'
            margin = away_score - home_score
        
        # Generate realistic ML odds based on margin
        # Larger margins = more lopsided odds
        if margin >= 21:  # Blowout
            favorite_ml = random.randint(-400, -200)
            underdog_ml = random.randint(300, 500)
        elif margin >= 14:  # Big win
            favorite_ml = random.randint(-300, -150)
            underdog_ml = random.randint(200, 350)
        elif margin >= 7:  # Comfortable win
            favorite_ml = random.randint(-200, -110)
            underdog_ml = random.randint(110, 200)
        else:  # Close game
            favorite_ml = random.randint(-120, -105)
            underdog_ml = random.randint(105, 120)
        
        # Assign odds to home/away based on winner
        if winner == 'home':
            home_ml = favorite_ml
            away_ml = underdog_ml
        else:
            home_ml = underdog_ml
            away_ml = favorite_ml
        
        # Generate total points (realistic range)
        total_points = home_score + away_score
        total_odds = random.randint(40, 60)  # Total around 45-55 points
        
        # Convert ML to win probabilities
        home_win_prob = self._ml_to_probability(home_ml)
        away_win_prob = self._ml_to_probability(away_ml)
        
        return {
            'home_ml': home_ml,
            'away_ml': away_ml,
            'total_points': total_odds,
            'home_win_prob': home_win_prob,
            'away_win_prob': away_win_prob
        }
    
    def _ml_to_probability(self, ml: int) -> float:
        """Convert ML odds to win probability"""
        if ml > 0:
            return 100 / (ml + 100)
        else:
            return abs(ml) / (abs(ml) + 100)
    
    def _generate_realistic_picks(self, game: Dict, odds: Dict) -> List[Dict]:
        """Generate realistic picks based on game outcome and odds"""
        
        picks = []
        home_score = game['home_score']
        away_score = game['away_score']
        margin = abs(home_score - away_score)
        
        # Determine actual winner
        if home_score > away_score:
            winner_team_id = game['home_team_id']
            winner_team = game['home_team']
            loser_team_id = game['away_team_id']
            loser_team = game['away_team']
        else:
            winner_team_id = game['away_team_id']
            winner_team = game['away_team']
            loser_team_id = game['home_team_id']
            loser_team = game['home_team']
        
        # Generate multiple realistic scenarios
        scenarios = self._generate_pick_scenarios(game, odds, margin, winner_team_id, loser_team_id)
        
        for scenario in scenarios:
            pick = {
                'game_id': game['id'],
                'season_year': game['season_year'],
                'week': game['week'],
                'pick_team_id': scenario['pick_team_id'],
                'confidence_points': scenario['confidence_points'],
                'win_probability': scenario['win_probability'],
                'total_points_prediction': odds['total_points'],
                'is_correct': scenario['is_correct']
            }
            picks.append(pick)
        
        return picks
    
    def _generate_pick_scenarios(self, game: Dict, odds: Dict, margin: int, 
                                winner_team_id: int, loser_team_id: int) -> List[Dict]:
        """Generate realistic pick scenarios"""
        
        scenarios = []
        
        # Scenario 1: Pick the winner (most common)
        winner_confidence = self._calculate_confidence_from_margin(margin, is_winner=True)
        scenarios.append({
            'pick_team_id': winner_team_id,
            'confidence_points': winner_confidence,
            'win_probability': odds['home_win_prob'] if winner_team_id == game['home_team_id'] else odds['away_win_prob'],
            'is_correct': True
        })
        
        # Scenario 2: Pick the loser (upset pick - less common)
        if random.random() < 0.15:  # 15% chance of upset pick
            loser_confidence = self._calculate_confidence_from_margin(margin, is_winner=False)
            scenarios.append({
                'pick_team_id': loser_team_id,
                'confidence_points': loser_confidence,
                'win_probability': odds['home_win_prob'] if loser_team_id == game['home_team_id'] else odds['away_win_prob'],
                'is_correct': False
            })
        
        # Scenario 3: Pick winner with different confidence (variance)
        if random.random() < 0.3:  # 30% chance of additional variance
            variance_confidence = self._calculate_confidence_from_margin(margin, is_winner=True, add_variance=True)
            scenarios.append({
                'pick_team_id': winner_team_id,
                'confidence_points': variance_confidence,
                'win_probability': odds['home_win_prob'] if winner_team_id == game['home_team_id'] else odds['away_win_prob'],
                'is_correct': True
            })
        
        return scenarios
    
    def _calculate_confidence_from_margin(self, margin: int, is_winner: bool, add_variance: bool = False) -> int:
        """Calculate confidence points based on game margin"""
        
        # Base confidence on margin
        if margin >= 21:  # Blowout
            base_confidence = 16 if is_winner else 1
        elif margin >= 14:  # Big win
            base_confidence = 14 if is_winner else 2
        elif margin >= 7:  # Comfortable win
            base_confidence = 12 if is_winner else 4
        else:  # Close game
            base_confidence = 8 if is_winner else 6
        
        # Add variance if requested
        if add_variance:
            variance = random.randint(-2, 2)
            base_confidence += variance
        
        # Ensure within valid range
        return max(1, min(16, base_confidence))
    
    def _store_synthetic_odds(self, game_id: int, odds: Dict):
        """Store synthetic odds in database"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO odds 
                (game_id, bookmaker, home_ml, away_ml, total_points, 
                 home_win_prob, away_win_prob, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                game_id, 'improved_synthetic', odds['home_ml'], odds['away_ml'], 
                odds['total_points'], odds['home_win_prob'], odds['away_win_prob'],
                '2024-01-01T00:00:00Z'
            ))
            
            conn.commit()
    
    def _store_training_picks(self, picks: List[Dict]):
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

def main():
    """Generate improved training data"""
    generator = ImprovedTrainingDataGenerator()
    
    # Generate training data for recent seasons
    count = generator.generate_improved_training_data(2020, 2024)
    
    print(f"✅ Generated {count} improved training picks")
    print(f"💡 Ready to retrain ML model with realistic data!")

if __name__ == "__main__":
    main()
