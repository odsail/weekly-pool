#!/usr/bin/env python3
"""
Enhanced Expert Picks Analyzer - Incorporates betting odds for better analysis
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

class EnhancedExpertPicksAnalyzer:
    """
    Analyzes expert picks from CBS Sports with betting odds integration
    """
    
    def __init__(self, week: int):
        self.week = week
        self.expert_picks_file = f"data/expert-picks-week-{week}-with-odds.json"
        self.consensus_data = None
        
    def load_expert_picks(self) -> Dict:
        """
        Load expert picks with odds from JSON file
        """
        if not os.path.exists(self.expert_picks_file):
            raise FileNotFoundError(f"Expert picks file not found: {self.expert_picks_file}")
        
        with open(self.expert_picks_file, 'r') as f:
            return json.load(f)
    
    def convert_odds_to_probability(self, odds: str) -> float:
        """
        Convert betting odds to win probability
        """
        try:
            odds_int = int(odds)
            
            if odds_int > 0:  # Underdog (positive odds)
                # For +150: probability = 100 / (150 + 100) = 0.4
                probability = 100 / (odds_int + 100)
            else:  # Favorite (negative odds)
                # For -150: probability = 150 / (150 + 100) = 0.6
                probability = abs(odds_int) / (abs(odds_int) + 100)
            
            return probability
        except:
            return 0.5  # Default to 50% if parsing fails
    
    def calculate_enhanced_consensus(self, expert_picks_data: Dict) -> List[Dict]:
        """
        Calculate consensus incorporating betting odds
        """
        games = expert_picks_data.get('games', [])
        consensus_data = []
        
        for game in games:
            expert_picks = game.get('expert_picks', [])
            odds = game.get('odds', {})
            
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
                
                # Calculate expert-based win probability
                expert_win_prob = self._calculate_win_probability(consensus_percentage)
                
                # Get betting odds probability for consensus team
                consensus_odds = odds.get(consensus_team, None)
                betting_win_prob = 0.5  # Default
                if consensus_odds:
                    betting_win_prob = self.convert_odds_to_probability(consensus_odds)
                
                # Combine expert and betting probabilities (weighted average)
                # Give more weight to betting odds as they're often more accurate
                combined_win_prob = (expert_win_prob * 0.3) + (betting_win_prob * 0.7)
                
                # Determine if expert consensus aligns with betting market
                market_alignment = "aligned"
                if consensus_odds:
                    if consensus_odds.startswith('+') and consensus_percentage > 70:
                        market_alignment = "experts_favor_underdog"
                    elif consensus_odds.startswith('-') and consensus_percentage < 60:
                        market_alignment = "experts_split_on_favorite"
                
                consensus_data.append({
                    'game': game['game'],
                    'away_team': game['away_team'],
                    'home_team': game['home_team'],
                    'consensus_team': consensus_team,
                    'consensus_count': consensus_count,
                    'total_experts': total_experts,
                    'consensus_percentage': consensus_percentage,
                    'expert_win_probability': expert_win_prob,
                    'betting_win_probability': betting_win_prob,
                    'combined_win_probability': combined_win_prob,
                    'consensus_odds': consensus_odds,
                    'all_odds': odds,
                    'market_alignment': market_alignment,
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
    
    def identify_enhanced_contrarian_opportunities(self, consensus_data: List[Dict]) -> Dict:
        """
        Identify contrarian opportunities using both expert consensus and betting odds
        """
        # Categories based on combined analysis
        high_confidence_fades = []  # Strong expert + betting consensus
        market_misalignment = []    # Expert consensus vs betting odds disagreement
        split_opportunities = []    # Both experts and market split
        
        for game in consensus_data:
            expert_pct = game['consensus_percentage']
            betting_prob = game['betting_win_probability']
            alignment = game['market_alignment']
            
            if expert_pct >= 85.7 and betting_prob >= 0.7:
                # Both experts and market strongly favor one team
                high_confidence_fades.append(game)
            elif alignment != "aligned":
                # Expert consensus doesn't match betting market
                market_misalignment.append(game)
            elif expert_pct < 70 and betting_prob < 0.7:
                # Both experts and market are split
                split_opportunities.append(game)
        
        return {
            'high_confidence_fades': high_confidence_fades,
            'market_misalignment': market_misalignment,
            'split_opportunities': split_opportunities
        }
    
    def analyze_odds_patterns(self, consensus_data: List[Dict]) -> Dict:
        """
        Analyze betting odds patterns
        """
        total_games = len(consensus_data)
        strong_favorites = len([g for g in consensus_data if g['betting_win_probability'] >= 0.7])
        moderate_favorites = len([g for g in consensus_data if 0.6 <= g['betting_win_probability'] < 0.7])
        close_games = len([g for g in consensus_data if 0.4 <= g['betting_win_probability'] < 0.6])
        strong_underdogs = len([g for g in consensus_data if g['betting_win_probability'] < 0.4])
        
        # Find games with biggest expert vs market disagreement
        disagreements = []
        for game in consensus_data:
            expert_prob = game['expert_win_probability']
            betting_prob = game['betting_win_probability']
            disagreement = abs(expert_prob - betting_prob)
            
            if disagreement > 0.15:  # 15% or more disagreement
                disagreements.append({
                    'game': game['game'],
                    'expert_prob': expert_prob,
                    'betting_prob': betting_prob,
                    'disagreement': disagreement,
                    'alignment': game['market_alignment']
                })
        
        return {
            'total_games': total_games,
            'strong_favorites': strong_favorites,
            'moderate_favorites': moderate_favorites,
            'close_games': close_games,
            'strong_underdogs': strong_underdogs,
            'expert_market_disagreements': disagreements
        }
    
    def generate_enhanced_analysis(self) -> Dict:
        """
        Generate complete analysis incorporating betting odds
        """
        print(f"📊 Analyzing Week {self.week} expert picks with betting odds...")
        
        # Load expert picks
        expert_picks_data = self.load_expert_picks()
        
        # Calculate enhanced consensus
        consensus_data = self.calculate_enhanced_consensus(expert_picks_data)
        
        # Identify enhanced contrarian opportunities
        contrarian_opportunities = self.identify_enhanced_contrarian_opportunities(consensus_data)
        
        # Analyze odds patterns
        odds_patterns = self.analyze_odds_patterns(consensus_data)
        
        # Store consensus data
        self.consensus_data = consensus_data
        
        analysis = {
            'week': self.week,
            'season': expert_picks_data.get('season', 2025),
            'analyzed_at': datetime.now().isoformat(),
            'source': expert_picks_data.get('source', 'CBS Sports'),
            'consensus_data': consensus_data,
            'contrarian_opportunities': contrarian_opportunities,
            'odds_patterns': odds_patterns,
            'expert_picks_data': expert_picks_data
        }
        
        print(f"✅ Enhanced analysis complete: {odds_patterns['total_games']} games analyzed")
        print(f"   Strong favorites: {odds_patterns['strong_favorites']} games")
        print(f"   Close games: {odds_patterns['close_games']} games")
        print(f"   Expert-market disagreements: {len(odds_patterns['expert_market_disagreements'])} games")
        
        return analysis
    
    def save_analysis(self, analysis: Dict) -> str:
        """
        Save enhanced analysis to JSON file
        """
        output_file = f"data/analysis/week-{self.week}-enhanced-analysis.json"
        
        # Create analysis directory if it doesn't exist
        os.makedirs('data/analysis', exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"💾 Saved enhanced analysis to: {output_file}")
        return output_file

def main():
    """
    Test the EnhancedExpertPicksAnalyzer
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze expert picks with betting odds")
    parser.add_argument("--week", type=int, required=True, help="Week number")
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = EnhancedExpertPicksAnalyzer(args.week)
    
    # Generate analysis
    analysis = analyzer.generate_enhanced_analysis()
    
    # Save analysis
    output_file = analyzer.save_analysis(analysis)
    
    print(f"\n✅ **ENHANCED ANALYSIS COMPLETE**")
    print(f"📄 Output: {output_file}")

if __name__ == "__main__":
    main()









