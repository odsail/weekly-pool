#!/usr/bin/env python3
"""
Enhanced Weekly Picks Generator - Incorporates betting odds for better picks
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from enhanced_expert_picks_analyzer import EnhancedExpertPicksAnalyzer

class EnhancedWeeklyPicksGenerator:
    """
    Generates weekly picks using expert consensus and betting odds
    """
    
    def __init__(self, week: int):
        self.week = week
        self.analyzer = EnhancedExpertPicksAnalyzer(week)
        self.analysis = None
        
    def load_analysis(self) -> Dict:
        """
        Load or generate enhanced expert picks analysis
        """
        if self.analysis is None:
            self.analysis = self.analyzer.generate_enhanced_analysis()
        return self.analysis
    
    def generate_odds_enhanced_picks(self) -> List[Dict]:
        """
        Generate picks using betting odds as primary factor with expert consensus as secondary
        """
        analysis = self.load_analysis()
        consensus_data = analysis['consensus_data']
        
        # Sort by combined win probability (betting odds weighted more heavily)
        consensus_data.sort(key=lambda x: x['combined_win_probability'], reverse=True)
        
        # Assign confidence points (16 to 1)
        picks = []
        for i, game_data in enumerate(consensus_data):
            confidence = 16 - i
            
            picks.append({
                'confidence': confidence,
                'pick': game_data['consensus_team'],
                'expert_win_prob': game_data['expert_win_probability'],
                'betting_win_prob': game_data['betting_win_probability'],
                'combined_win_prob': game_data['combined_win_probability'],
                'home_team': game_data['home_team'],
                'away_team': game_data['away_team'],
                'consensus_count': game_data['consensus_count'],
                'total_experts': game_data['total_experts'],
                'consensus_percentage': game_data['consensus_percentage'],
                'consensus_odds': game_data['consensus_odds'],
                'market_alignment': game_data['market_alignment'],
                'game': game_data['game']
            })
        
        return picks
    
    def generate_market_misalignment_picks(self) -> List[Dict]:
        """
        Generate picks focusing on games where expert consensus disagrees with betting market
        """
        analysis = self.load_analysis()
        misalignment_games = analysis['contrarian_opportunities']['market_misalignment']
        
        # Sort by disagreement magnitude
        misalignment_games.sort(key=lambda x: abs(x['expert_win_probability'] - x['betting_win_probability']), reverse=True)
        
        picks = []
        for i, game_data in enumerate(misalignment_games):
            confidence = 16 - i
            
            # Pick the team that betting market favors (often more accurate)
            betting_team = None
            for team, odds in game_data['all_odds'].items():
                if odds.startswith('-'):
                    betting_team = team
                    break
            
            if betting_team:
                picks.append({
                    'confidence': confidence,
                    'pick': betting_team,
                    'expert_win_prob': game_data['expert_win_probability'],
                    'betting_win_prob': game_data['betting_win_probability'],
                    'combined_win_prob': game_data['combined_win_probability'],
                    'home_team': game_data['home_team'],
                    'away_team': game_data['away_team'],
                    'consensus_count': game_data['consensus_count'],
                    'total_experts': game_data['total_experts'],
                    'consensus_percentage': game_data['consensus_percentage'],
                    'consensus_odds': game_data['consensus_odds'],
                    'market_alignment': game_data['market_alignment'],
                    'game': game_data['game'],
                    'strategy': 'market_misalignment'
                })
        
        return picks
    
    def generate_high_confidence_fades(self) -> List[Dict]:
        """
        Generate contrarian picks fading games with both strong expert and betting consensus
        """
        analysis = self.load_analysis()
        high_confidence_fades = analysis['contrarian_opportunities']['high_confidence_fades']
        
        # Sort by combined confidence (highest first for lowest confidence points)
        high_confidence_fades.sort(key=lambda x: x['combined_win_probability'], reverse=True)
        
        picks = []
        for i, game_data in enumerate(high_confidence_fades):
            confidence = i + 1  # Lowest confidence points to highest consensus fades
            
            # Pick the underdog (non-consensus team)
            consensus_team = game_data['consensus_team']
            if consensus_team == game_data['home_team']:
                contrarian_pick = game_data['away_team']
            else:
                contrarian_pick = game_data['home_team']
            
            picks.append({
                'confidence': confidence,
                'pick': contrarian_pick,
                'expert_win_prob': 1.0 - game_data['expert_win_probability'],
                'betting_win_prob': 1.0 - game_data['betting_win_probability'],
                'combined_win_prob': 1.0 - game_data['combined_win_probability'],
                'home_team': game_data['home_team'],
                'away_team': game_data['away_team'],
                'consensus_count': game_data['consensus_count'],
                'total_experts': game_data['total_experts'],
                'consensus_percentage': game_data['consensus_percentage'],
                'consensus_odds': game_data['consensus_odds'],
                'market_alignment': game_data['market_alignment'],
                'game': game_data['game'],
                'fade_team': consensus_team,
                'strategy': 'high_confidence_fade'
            })
        
        return picks
    
    def save_enhanced_picks_to_markdown(self, picks: List[Dict], strategy: str) -> str:
        """
        Save enhanced picks to markdown file with odds information
        """
        analysis = self.load_analysis()
        odds_patterns = analysis['odds_patterns']
        
        # Create output directory
        os.makedirs('data/outputs/2025', exist_ok=True)
        
        # Generate markdown content
        markdown_content = f"""# Week {self.week} NFL Confidence Picks - {strategy.title()}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Command Used:** `python enhanced_weekly_picks_generator.py --week {self.week} --strategy {strategy}`  
**Strategy:** {strategy.title()} (Enhanced with Betting Odds)  
**Data Source:** CBS Sports expert picks + Betting odds

## Methodology

This week's picks incorporate **betting odds** as a primary factor, combined with expert consensus. Betting odds represent market consensus and are often more predictive than expert opinion alone.

**IMPORTANT:** We are picking the **straight-up winner** of each game, NOT covering the point spread.

### Enhanced Analysis:
- **Expert Consensus**: CBS Sports expert picks (6 experts)
- **Betting Odds**: Market consensus from sportsbooks
- **Combined Probability**: 70% betting odds + 30% expert consensus
- **Market Alignment**: Identifies games where experts disagree with betting market

### Betting Odds Interpretation:
- **Negative odds (-150)**: Favorite, higher win probability
- **Positive odds (+150)**: Underdog, lower win probability
- **Larger negative numbers**: Stronger favorites (e.g., -365 = 78.5% win probability)

## Week {self.week} Enhanced Picks

| Points | Pick | Expert% | Betting% | Combined% | Odds | Market | Game |
|--------|------|---------|----------|-----------|------|--------|------|
"""
        
        for pick in picks:
            market_status = "✅ Aligned" if pick['market_alignment'] == "aligned" else "⚠️ Misaligned"
            odds_display = pick['consensus_odds'] if pick['consensus_odds'] else "N/A"
            
            markdown_content += f"| {pick['confidence']} | {pick['pick']} | {pick['expert_win_prob']:.1%} | {pick['betting_win_prob']:.1%} | {pick['combined_win_prob']:.1%} | {odds_display} | {market_status} | {pick['game']} |\n"
        
        # Add insights section
        markdown_content += f"""
## Key Insights

### Betting Market Analysis:
- **Strong Favorites**: {odds_patterns['strong_favorites']} games (≥70% betting probability)
- **Close Games**: {odds_patterns['close_games']} games (40-60% betting probability)
- **Expert-Market Disagreements**: {len(odds_patterns['expert_market_disagreements'])} games

### Strategy Notes:
"""
        
        if strategy == 'odds_enhanced':
            markdown_content += """
- **Primary Factor**: Betting odds (70% weight)
- **Secondary Factor**: Expert consensus (30% weight)
- **Target**: Games where market and experts agree
- **Confidence**: Highest points to strongest combined probability
"""
        elif strategy == 'market_misalignment':
            markdown_content += """
- **Focus**: Games where experts disagree with betting market
- **Strategy**: Side with betting market (often more accurate)
- **Target**: Expert consensus vs market consensus disagreements
- **Risk**: Medium - betting market is usually right
"""
        elif strategy == 'high_confidence_fades':
            markdown_content += """
- **Focus**: Fading games with both strong expert and betting consensus
- **Strategy**: Pick underdogs when both experts and market strongly favor favorite
- **Target**: High consensus games (both expert and betting)
- **Risk**: High - going against both experts and market
"""
        
        # Add expert-market disagreement details
        if odds_patterns['expert_market_disagreements']:
            markdown_content += """
### Expert vs Market Disagreements:
"""
            for disagreement in odds_patterns['expert_market_disagreements'][:3]:  # Show top 3
                markdown_content += f"- **{disagreement['game']}**: Expert {disagreement['expert_prob']:.1%} vs Market {disagreement['betting_prob']:.1%} ({disagreement['disagreement']:.1%} difference)\n"
        
        markdown_content += f"""
---
*Generated using {strategy} strategy with CBS Sports expert consensus + betting odds data*
"""
        
        # Save to file
        filename = f'data/outputs/2025/week-week{self.week}-{strategy}-enhanced-picks.md'
        with open(filename, 'w') as f:
            f.write(markdown_content)
        
        print(f"💾 Saved {strategy} enhanced picks to: {filename}")
        return filename
    
    def generate_all_enhanced_strategies(self) -> Dict[str, str]:
        """
        Generate picks for all enhanced strategies and return file paths
        """
        strategies = ['odds_enhanced', 'market_misalignment', 'high_confidence_fades']
        output_files = {}
        
        for strategy in strategies:
            print(f"\n🎯 Generating {strategy} enhanced picks...")
            
            if strategy == 'odds_enhanced':
                picks = self.generate_odds_enhanced_picks()
            elif strategy == 'market_misalignment':
                picks = self.generate_market_misalignment_picks()
            else:  # high_confidence_fades
                picks = self.generate_high_confidence_fades()
            
            output_file = self.save_enhanced_picks_to_markdown(picks, strategy)
            output_files[strategy] = output_file
        
        return output_files

def main():
    """
    Main function for generating enhanced weekly picks
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate enhanced weekly picks with betting odds")
    parser.add_argument("--week", type=int, required=True, help="Week number")
    parser.add_argument("--strategy", choices=['odds_enhanced', 'market_misalignment', 'high_confidence_fades', 'all'], 
                       default='all', help="Enhanced picking strategy")
    
    args = parser.parse_args()
    
    # Create generator
    generator = EnhancedWeeklyPicksGenerator(args.week)
    
    print(f"🎯 **WEEK {args.week} ENHANCED PICKS GENERATOR**")
    print("=" * 60)
    
    if args.strategy == 'all':
        # Generate all enhanced strategies
        output_files = generator.generate_all_enhanced_strategies()
        
        print(f"\n✅ **ALL ENHANCED STRATEGIES GENERATED**")
        print("=" * 50)
        for strategy, file_path in output_files.items():
            print(f"📄 {strategy.replace('_', ' ').title()}: {file_path}")
    else:
        # Generate specific strategy
        if args.strategy == 'odds_enhanced':
            picks = generator.generate_odds_enhanced_picks()
        elif args.strategy == 'market_misalignment':
            picks = generator.generate_market_misalignment_picks()
        else:  # high_confidence_fades
            picks = generator.generate_high_confidence_fades()
        
        output_file = generator.save_enhanced_picks_to_markdown(picks, args.strategy)
        
        print(f"\n✅ **{args.strategy.upper().replace('_', ' ')} PICKS GENERATED**")
        print(f"📄 Output: {output_file}")

if __name__ == "__main__":
    main()









