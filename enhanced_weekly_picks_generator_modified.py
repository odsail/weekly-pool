#!/usr/bin/env python3
"""
Enhanced Weekly Picks Generator - Modified to handle Thursday losses
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
    
    def __init__(self, week: int, thursday_loss=None):
        self.week = week
        self.analyzer = EnhancedExpertPicksAnalyzer(week)
        self.analysis = None
        self.thursday_loss = thursday_loss  # Format: {'game': '...', 'pick': '...', 'confidence_used': 16, 'result': 'LOSS'}
        
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
        
        # Handle Thursday loss scenario
        if self.thursday_loss:
            # Remove the Thursday game from consideration
            thursday_game = self.thursday_loss['game']
            consensus_data = [game for game in consensus_data if thursday_game not in game['game']]
            
            # Assign confidence points from 15 down to 1 (since 16 was used Thursday)
            confidence_points = list(range(15, 0, -1))  # 15 down to 1
        else:
            # Normal scenario - assign confidence points (16 to 1)
            confidence_points = list(range(16, 0, -1))  # 16 down to 1
        
        # Assign confidence points
        picks = []
        for i, game_data in enumerate(consensus_data):
            if i < len(confidence_points):
                confidence = confidence_points[i]
                
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
    
    def save_enhanced_picks_to_markdown(self, picks: List[Dict], strategy: str) -> str:
        """
        Save enhanced picks to markdown file with odds information
        """
        analysis = self.load_analysis()
        odds_patterns = analysis['odds_patterns']
        
        # Create output directory
        os.makedirs('data/outputs/2025', exist_ok=True)
        
        # Determine file suffix based on Thursday loss
        if self.thursday_loss:
            file_suffix = f"-{strategy}-enhanced-picks-post-thursday.md"
            title_suffix = " (Post-Thursday)"
        else:
            file_suffix = f"-{strategy}-enhanced-picks.md"
            title_suffix = ""
        
        # Generate markdown content
        markdown_content = f"""# Week {self.week} NFL Confidence Picks - {strategy.title()}{title_suffix}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Command Used:** `python enhanced_weekly_picks_generator_modified.py --week {self.week} --strategy {strategy}`  
**Strategy:** {strategy.title()} (Enhanced with Betting Odds)  
**Data Source:** CBS Sports expert picks + Betting odds
"""
        
        # Add Thursday loss section if applicable
        if self.thursday_loss:
            markdown_content += f"""
## Thursday Night Result

**❌ LOSS - {self.thursday_loss['confidence_used']} Points Used:**
- **Game**: {self.thursday_loss['game']}
- **Pick**: {self.thursday_loss['pick']} ({self.thursday_loss['confidence_used']} points)
- **Result**: {self.thursday_loss['result']}
- **Impact**: {self.thursday_loss['confidence_used']} confidence points already used

"""
        
        markdown_content += f"""
## Methodology

This week's picks incorporate **betting odds** as a primary factor, combined with expert consensus. Betting odds represent market consensus and are often more predictive than expert opinion alone.

**IMPORTANT:** We are picking the **straight-up winner** of each game, NOT covering the point spread.

### Enhanced Analysis:
- **Expert Consensus**: CBS Sports expert picks (7 experts)
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

- **Primary Factor**: Betting odds (70% weight)
- **Secondary Factor**: Expert consensus (30% weight)
- **Target**: Games where market and experts agree
- **Confidence**: Highest points to strongest combined probability
"""
        
        if self.thursday_loss:
            markdown_content += f"""
### Thursday Night Impact:
- **Points Lost**: {self.thursday_loss['confidence_used']} points (highest confidence)
- **Remaining Points**: 1-15 (15 games)
- **Strategy**: Focus on remaining high-probability games
- **Recovery**: Need strong performance on remaining picks
"""
        
        # Add expert-market disagreement details
        if odds_patterns['expert_market_disagreements']:
            markdown_content += """
### Expert vs Market Disagreements:
"""
            for disagreement in odds_patterns['expert_market_disagreements'][:3]:  # Show top 3
                markdown_content += f"- **{disagreement['game']}**: Expert {disagreement['expert_prob']:.1%} vs Market {disagreement['betting_prob']:.1%} ({disagreement['disagreement']:.1%} difference)\n"
        
        # Add Monday night tie-breaker
        markdown_content += f"""
## Monday Night Game - Tie Breaker

| Game | Pick | Total Points |
|------|------|-------------|
| Chicago Bears @ Washington Commanders | Washington Commanders | **45** |

---
*Generated using {strategy} strategy with CBS Sports expert consensus + betting odds data*
"""
        
        # Save to file
        filename = f'data/outputs/2025/week-week{self.week}{file_suffix}'
        with open(filename, 'w') as f:
            f.write(markdown_content)
        
        print(f"💾 Saved {strategy} enhanced picks to: {filename}")
        return filename

def main():
    """
    Main function for generating enhanced weekly picks
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate enhanced weekly picks with betting odds")
    parser.add_argument("--week", type=int, required=True, help="Week number")
    parser.add_argument("--strategy", choices=['odds_enhanced', 'market_misalignment', 'high_confidence_fades'], 
                       default='odds_enhanced', help="Enhanced picking strategy")
    parser.add_argument("--thursday-loss", type=str, help="Thursday loss info: 'game|pick|confidence|result'")
    
    args = parser.parse_args()
    
    # Parse Thursday loss if provided
    thursday_loss = None
    if args.thursday_loss:
        parts = args.thursday_loss.split('|')
        if len(parts) == 4:
            thursday_loss = {
                'game': parts[0],
                'pick': parts[1],
                'confidence_used': int(parts[2]),
                'result': parts[3]
            }
    
    # Create generator
    generator = EnhancedWeeklyPicksGenerator(args.week, thursday_loss)
    
    print(f"🎯 **WEEK {args.week} ENHANCED PICKS GENERATOR**")
    print("=" * 60)
    
    if thursday_loss:
        print(f"📊 Accounting for Thursday night loss: {thursday_loss['pick']} ({thursday_loss['confidence_used']} points)")
    
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
