#!/usr/bin/env python3
"""
Weekly Picks Generator - Reusable component for generating weekly picks
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from expert_picks_analyzer import ExpertPicksAnalyzer

class WeeklyPicksGenerator:
    """
    Generates weekly picks using expert consensus and other factors
    """
    
    def __init__(self, week: int):
        self.week = week
        self.analyzer = ExpertPicksAnalyzer(week)
        self.analysis = None
        
    def load_analysis(self) -> Dict:
        """
        Load or generate expert picks analysis
        """
        if self.analysis is None:
            self.analysis = self.analyzer.generate_analysis()
        return self.analysis
    
    def generate_consensus_picks(self) -> List[Dict]:
        """
        Generate picks based on expert consensus
        """
        analysis = self.load_analysis()
        consensus_data = analysis['consensus_data']
        
        # Sort by win probability for confidence assignment
        consensus_data.sort(key=lambda x: x['win_probability'], reverse=True)
        
        # Assign confidence points (16 to 1)
        picks = []
        for i, game_data in enumerate(consensus_data):
            confidence = 16 - i
            
            picks.append({
                'confidence': confidence,
                'pick': game_data['consensus_team'],
                'win_prob': game_data['win_probability'],
                'home_team': game_data['home_team'],
                'away_team': game_data['away_team'],
                'consensus_count': game_data['consensus_count'],
                'total_experts': game_data['total_experts'],
                'consensus_percentage': game_data['consensus_percentage'],
                'game': game_data['game']
            })
        
        return picks
    
    def generate_contrarian_picks(self) -> List[Dict]:
        """
        Generate contrarian picks (fading strong consensus)
        """
        analysis = self.load_analysis()
        contrarian_opps = analysis['contrarian_opportunities']
        
        # Focus on universal consensus fades (highest risk/reward)
        universal_fades = contrarian_opps['universal_consensus']
        
        # Sort by consensus strength (highest first for lowest confidence)
        universal_fades.sort(key=lambda x: x['consensus_percentage'], reverse=True)
        
        picks = []
        for i, game_data in enumerate(universal_fades):
            # Assign lowest confidence points to highest consensus fades
            confidence = i + 1
            
            # Pick the underdog (non-consensus team)
            consensus_team = game_data['consensus_team']
            if consensus_team == game_data['home_team']:
                contrarian_pick = game_data['away_team']
            else:
                contrarian_pick = game_data['home_team']
            
            picks.append({
                'confidence': confidence,
                'pick': contrarian_pick,
                'win_prob': 1.0 - game_data['win_probability'],  # Inverse probability
                'home_team': game_data['home_team'],
                'away_team': game_data['away_team'],
                'consensus_count': game_data['consensus_count'],
                'total_experts': game_data['total_experts'],
                'consensus_percentage': game_data['consensus_percentage'],
                'game': game_data['game'],
                'fade_team': consensus_team
            })
        
        return picks
    
    def generate_hybrid_picks(self, consensus_weight: float = 0.7) -> List[Dict]:
        """
        Generate hybrid picks combining consensus and contrarian strategies
        """
        consensus_picks = self.generate_consensus_picks()
        contrarian_picks = self.generate_contrarian_picks()
        
        # Combine strategies based on weight
        hybrid_picks = []
        
        # Take top consensus picks for high confidence
        high_confidence_count = int(16 * consensus_weight)
        hybrid_picks.extend(consensus_picks[:high_confidence_count])
        
        # Fill remaining with contrarian picks
        remaining_count = 16 - len(hybrid_picks)
        if remaining_count > 0 and contrarian_picks:
            # Take top contrarian picks
            hybrid_picks.extend(contrarian_picks[:remaining_count])
        
        # Reassign confidence points
        for i, pick in enumerate(hybrid_picks):
            pick['confidence'] = 16 - i
        
        return hybrid_picks
    
    def save_picks_to_markdown(self, picks: List[Dict], strategy: str) -> str:
        """
        Save picks to markdown file
        """
        analysis = self.load_analysis()
        patterns = analysis['patterns']
        
        # Create output directory
        os.makedirs('data/outputs/2025', exist_ok=True)
        
        # Generate markdown content
        markdown_content = f"""# Week {self.week} NFL Confidence Picks - {strategy.title()}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Command Used:** `python weekly_picks_generator.py --week {self.week} --strategy {strategy}`  
**Strategy:** {strategy.title()}  
**Data Source:** CBS Sports expert picks (7 experts)

## Methodology

This week's picks are based on {strategy} strategy using CBS Sports expert consensus data.

**IMPORTANT:** We are picking the **straight-up winner** of each game, NOT covering the point spread.

### Expert Consensus Calculation:
- **7/7 experts (100%)**: Win probability 0.85
- **6/7 experts (85.7%)**: Win probability 0.75-0.85
- **5/7 experts (71.4%)**: Win probability 0.65-0.75
- **4/7 experts (57.1%)**: Win probability 0.55-0.65
- **Split decisions**: Win probability 0.50-0.55

## Week {self.week} Picks

| Points | Pick | Win% | Consensus | Home | Away | Expert Split |
|--------|------|------|-----------|------|------|--------------|
"""
        
        for pick in picks:
            consensus_str = f"{pick['consensus_count']}/{pick['total_experts']} ({pick['consensus_percentage']:.1f}%)"
            markdown_content += f"| {pick['confidence']} | {pick['pick']} | {pick['win_prob']:.1%} | {consensus_str} | {pick['home_team']} | {pick['away_team']} | {pick['consensus_count']}/{pick['total_experts']} |\n"
        
        # Add insights section
        markdown_content += f"""
## Key Insights

### Consensus Analysis:
- **Total Games**: {patterns['total_games']}
- **Universal Consensus**: {patterns['universal_consensus_games']} games ({patterns['universal_consensus_rate']:.1f}%)
- **Strong Consensus**: {patterns['strong_consensus_games']} games
- **Split Decisions**: {patterns['split_decision_games']} games

### Strategy Notes:
"""
        
        if strategy == 'contrarian':
            markdown_content += """
- **High Risk/Reward**: Fading universal consensus (7/7 or 6/7 experts)
- **Confidence Assignment**: Lowest points to highest consensus fades
- **Target**: Games where experts are most likely to be wrong
"""
        elif strategy == 'hybrid':
            markdown_content += """
- **Balanced Approach**: Combines consensus and contrarian strategies
- **High Confidence**: Expert consensus picks
- **Low Confidence**: Contrarian fades
"""
        else:
            markdown_content += """
- **Expert Consensus**: Following majority expert opinion
- **Confidence Assignment**: Highest points to strongest consensus
- **Target**: Games where experts agree most strongly
"""
        
        markdown_content += f"""
---
*Generated using {strategy} strategy with CBS Sports expert consensus data*
"""
        
        # Save to file
        filename = f'data/outputs/2025/week-week{self.week}-{strategy}-picks.md'
        with open(filename, 'w') as f:
            f.write(markdown_content)
        
        print(f"💾 Saved {strategy} picks to: {filename}")
        return filename
    
    def generate_all_strategies(self) -> Dict[str, str]:
        """
        Generate picks for all strategies and return file paths
        """
        strategies = ['consensus', 'contrarian', 'hybrid']
        output_files = {}
        
        for strategy in strategies:
            print(f"\n🎯 Generating {strategy} picks...")
            
            if strategy == 'consensus':
                picks = self.generate_consensus_picks()
            elif strategy == 'contrarian':
                picks = self.generate_contrarian_picks()
            else:  # hybrid
                picks = self.generate_hybrid_picks()
            
            output_file = self.save_picks_to_markdown(picks, strategy)
            output_files[strategy] = output_file
        
        return output_files

def main():
    """
    Main function for generating weekly picks
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate weekly picks")
    parser.add_argument("--week", type=int, required=True, help="Week number")
    parser.add_argument("--strategy", choices=['consensus', 'contrarian', 'hybrid', 'all'], 
                       default='all', help="Picking strategy")
    
    args = parser.parse_args()
    
    # Create generator
    generator = WeeklyPicksGenerator(args.week)
    
    print(f"🎯 **WEEK {args.week} PICKS GENERATOR**")
    print("=" * 50)
    
    if args.strategy == 'all':
        # Generate all strategies
        output_files = generator.generate_all_strategies()
        
        print(f"\n✅ **ALL STRATEGIES GENERATED**")
        print("=" * 40)
        for strategy, file_path in output_files.items():
            print(f"📄 {strategy.title()}: {file_path}")
    else:
        # Generate specific strategy
        if args.strategy == 'consensus':
            picks = generator.generate_consensus_picks()
        elif args.strategy == 'contrarian':
            picks = generator.generate_contrarian_picks()
        else:  # hybrid
            picks = generator.generate_hybrid_picks()
        
        output_file = generator.save_picks_to_markdown(picks, args.strategy)
        
        print(f"\n✅ **{args.strategy.upper()} PICKS GENERATED**")
        print(f"📄 Output: {output_file}")

if __name__ == "__main__":
    main()









