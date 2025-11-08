#!/usr/bin/env python3
"""
Expert Picks Analyzer - Reusable component for analyzing CBS Sports expert picks
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

class ExpertPicksAnalyzer:
    """
    Analyzes expert picks from CBS Sports and generates consensus data
    """
    
    def __init__(self, week: int):
        self.week = week
        self.expert_picks_file = f"data/expert-picks-week-{week}.json"
        self.consensus_data = None
        
    def load_expert_picks(self) -> Dict:
        """
        Load expert picks from JSON file
        """
        if not os.path.exists(self.expert_picks_file):
            raise FileNotFoundError(f"Expert picks file not found: {self.expert_picks_file}")
        
        with open(self.expert_picks_file, 'r') as f:
            return json.load(f)
    
    def calculate_consensus(self, expert_picks_data: Dict) -> List[Dict]:
        """
        Calculate consensus for each game
        """
        games = expert_picks_data.get('games', [])
        consensus_data = []
        
        for game in games:
            expert_picks = game.get('expert_picks', [])
            
            # Count picks for each team
            team_counts = {}
            for pick in expert_picks:
                team = pick['pick']
                if team not in team_counts:
                    team_counts[team] = 0
                team_counts[team] += 1
            
            # Find consensus team
            if team_counts:
                consensus_team = max(team_counts, key=team_counts.get)
                consensus_count = team_counts[consensus_team]
                total_experts = len(expert_picks)
                consensus_percentage = (consensus_count / total_experts) * 100
                
                # Calculate win probability based on consensus strength
                win_probability = self._calculate_win_probability(consensus_percentage)
                
                consensus_data.append({
                    'game': game['game'],
                    'away_team': game['away_team'],
                    'home_team': game['home_team'],
                    'consensus_team': consensus_team,
                    'consensus_count': consensus_count,
                    'total_experts': total_experts,
                    'consensus_percentage': consensus_percentage,
                    'win_probability': win_probability,
                    'team_counts': team_counts,
                    'expert_picks': expert_picks
                })
        
        return consensus_data
    
    def _calculate_win_probability(self, consensus_percentage: float) -> float:
        """
        Calculate win probability based on consensus percentage
        """
        if consensus_percentage >= 85.7:  # 6/7 or 7/7 experts
            return 0.75 + (consensus_percentage - 85.7) * 0.01
        elif consensus_percentage >= 71.4:  # 5/7 experts
            return 0.65 + (consensus_percentage - 71.4) * 0.01
        elif consensus_percentage >= 57.1:  # 4/7 experts
            return 0.55 + (consensus_percentage - 57.1) * 0.01
        else:  # Split decision
            return 0.50 + (consensus_percentage - 50) * 0.01
    
    def identify_contrarian_opportunities(self, consensus_data: List[Dict]) -> Dict:
        """
        Identify contrarian opportunities based on consensus strength
        """
        universal_consensus = []  # 7/7 or 6/7 experts
        strong_consensus = []     # 5/7 experts
        split_decisions = []      # 4/7 or less experts
        
        for game in consensus_data:
            consensus_pct = game['consensus_percentage']
            
            if consensus_pct >= 85.7:
                universal_consensus.append(game)
            elif consensus_pct >= 71.4:
                strong_consensus.append(game)
            else:
                split_decisions.append(game)
        
        return {
            'universal_consensus': universal_consensus,
            'strong_consensus': strong_consensus,
            'split_decisions': split_decisions
        }
    
    def analyze_consensus_patterns(self, consensus_data: List[Dict]) -> Dict:
        """
        Analyze consensus patterns for insights
        """
        total_games = len(consensus_data)
        universal_count = len([g for g in consensus_data if g['consensus_percentage'] >= 85.7])
        strong_count = len([g for g in consensus_data if g['consensus_percentage'] >= 71.4])
        split_count = total_games - universal_count - strong_count
        
        return {
            'total_games': total_games,
            'universal_consensus_games': universal_count,
            'strong_consensus_games': strong_count,
            'split_decision_games': split_count,
            'universal_consensus_rate': (universal_count / total_games) * 100 if total_games > 0 else 0
        }
    
    def generate_analysis(self) -> Dict:
        """
        Generate complete analysis of expert picks
        """
        print(f"📊 Analyzing Week {self.week} expert picks...")
        
        # Load expert picks
        expert_picks_data = self.load_expert_picks()
        
        # Calculate consensus
        consensus_data = self.calculate_consensus(expert_picks_data)
        
        # Identify contrarian opportunities
        contrarian_opportunities = self.identify_contrarian_opportunities(consensus_data)
        
        # Analyze patterns
        patterns = self.analyze_consensus_patterns(consensus_data)
        
        # Store consensus data
        self.consensus_data = consensus_data
        
        analysis = {
            'week': self.week,
            'season': expert_picks_data.get('season', 2025),
            'analyzed_at': datetime.now().isoformat(),
            'source': expert_picks_data.get('source', 'CBS Sports'),
            'consensus_data': consensus_data,
            'contrarian_opportunities': contrarian_opportunities,
            'patterns': patterns,
            'expert_picks_data': expert_picks_data
        }
        
        print(f"✅ Analysis complete: {patterns['total_games']} games analyzed")
        print(f"   Universal consensus: {patterns['universal_consensus_games']} games")
        print(f"   Strong consensus: {patterns['strong_consensus_games']} games")
        print(f"   Split decisions: {patterns['split_decision_games']} games")
        
        return analysis
    
    def save_analysis(self, analysis: Dict) -> str:
        """
        Save analysis to JSON file
        """
        output_file = f"data/analysis/week-{self.week}-expert-analysis.json"
        
        # Create analysis directory if it doesn't exist
        os.makedirs('data/analysis', exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"💾 Saved analysis to: {output_file}")
        return output_file

def main():
    """
    Test the ExpertPicksAnalyzer
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze expert picks")
    parser.add_argument("--week", type=int, required=True, help="Week number")
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = ExpertPicksAnalyzer(args.week)
    
    # Generate analysis
    analysis = analyzer.generate_analysis()
    
    # Save analysis
    output_file = analyzer.save_analysis(analysis)
    
    print(f"\n✅ **ANALYSIS COMPLETE**")
    print(f"📄 Output: {output_file}")

if __name__ == "__main__":
    main()









