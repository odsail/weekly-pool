# NFL Confidence Pool Analysis System

A comprehensive data-driven system for generating NFL confidence pool picks using expert consensus, betting odds, machine learning, and historical performance analysis.

## 🏈 Overview

This system analyzes NFL games to generate optimal confidence pool picks by combining multiple data sources and strategies. It tracks performance over time and continuously improves through machine learning and historical analysis.

### Key Features

- **Expert Consensus Integration**: Scrapes CBS Sports expert picks
- **Betting Odds Analysis**: Incorporates market intelligence from sportsbooks
- **Machine Learning Enhancement**: Learns from historical performance
- **Multiple Strategies**: Expert consensus, contrarian, odds-enhanced, market misalignment
- **Historical Analysis**: Tracks consensus failures and performance patterns
- **Database-Driven**: SQLite database for persistent data storage
- **Automated Workflow**: Single command generates picks for any week

## 🚀 Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

### Generate Week Picks

```bash
# Scrape expert picks and betting odds
python scrape_cbs_expert_picks_v3.py --week 8

# Generate picks using odds-enhanced strategy
python enhanced_weekly_picks_generator.py --week 8 --strategy odds_enhanced
```

### Complete Weekly Workflow

```bash
# Thursday: Generate picks for upcoming week
python enhanced_weekly_picks_generator.py --week 8 --strategy odds_enhanced

# Monday: Analyze results (automatic)
python analyze_prior_week.py --week 7
```

## 📊 System Architecture

### Core Components

1. **Data Collection**
   - `scrape_cbs_expert_picks_v3.py` - Scrapes expert picks and betting odds
   - `enhanced_expert_picks_analyzer.py` - Analyzes expert consensus and market data

2. **Pick Generation**
   - `enhanced_weekly_picks_generator.py` - Main picks generator with multiple strategies
   - `enhanced_picks_generator.py` - Database-driven picks with ML enhancement

3. **Analysis & Learning**
   - `consensus_failure_analysis.py` - Analyzes historical consensus failures
   - `analyze_prior_week.py` - Post-game analysis and model retraining

4. **Data Management**
   - `database_manager.py` - SQLite database operations
   - `database_schema.sql` - Complete database schema

### Database Schema

The system uses SQLite with the following key tables:

- **`teams`** - NFL team information
- **`games`** - Game results and metadata
- **`odds`** - Historical betting odds
- **`picks`** - Generated picks with confidence points
- **`pool_results`** - Actual pool participant results
- **`analysis_results`** - Performance analysis data
- **`expert_picks`** - Expert consensus tracking

## 🎯 Pick Generation Strategies

### 1. Odds Enhanced (Recommended)
Combines betting odds (70% weight) with expert consensus (30% weight).

```bash
python enhanced_weekly_picks_generator.py --week 8 --strategy odds_enhanced
```

### 2. Market Misalignment
Identifies games where experts disagree with betting market.

```bash
python enhanced_weekly_picks_generator.py --week 8 --strategy market_misalignment
```

### 3. High Confidence Fades
Fades games with strong expert and betting consensus.

```bash
python enhanced_weekly_picks_generator.py --week 8 --strategy high_confidence_fades
```

### 4. Expert Consensus
Pure expert consensus with minimal ML influence.

```bash
python enhanced_weekly_picks_generator.py --week 8 --strategy expert_consensus
```

## 📈 Performance Tracking

### Historical Performance

The system tracks multiple performance metrics:

- **Overall Accuracy**: Percentage of correct picks
- **Confidence Accuracy**: Performance by confidence point level
- **Strategy Comparison**: Performance across different strategies
- **Consensus Failure Analysis**: Patterns in expert consensus failures

### Key Insights from 2025 Season

- **Week 4 Performance**: 56.2% accuracy (9/16 correct)
- **Contrarian Strategy**: 50.0% accuracy (8/16 correct)
- **Best Performing**: Medium risk contrarian picks (4/5 correct)
- **Primary Model**: Expert consensus with ML enhancement

## 🔧 Advanced Usage

### Custom Analysis

```bash
# Analyze consensus failures
python consensus_failure_analysis.py

# Compare strategies
python comprehensive_analysis.py --week 8

# Export analysis results
python export_analysis.py --week 8
```

### Database Operations

```bash
# Initialize database
python database_manager.py --init

# Update with prior week results
python update_pool_results_with_outcomes.py --week 7

# Query specific data
python database_manager.py --query "SELECT * FROM picks WHERE week = 8"
```

### Special Scenarios

```bash
# Handle Thursday night loss
python enhanced_weekly_picks_generator_modified.py --week 6 --thursday-loss

# Generate alternate picks
python create_week7_vikings_alternate.py
```

## 📁 File Structure

```
weekly-pool/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── database_schema.sql                 # Database schema
├── database_manager.py                 # Database operations
├── scrape_cbs_expert_picks_v3.py      # Expert picks scraper
├── enhanced_weekly_picks_generator.py  # Main picks generator
├── enhanced_expert_picks_analyzer.py   # Expert analysis
├── consensus_failure_analysis.py       # Historical analysis
├── analyze_prior_week.py              # Post-game analysis
├── data/
│   ├── nfl_pool_v2.db                 # SQLite database
│   ├── expert-picks-week-*.json       # Scraped expert data
│   └── outputs/2025/                  # Generated picks and analysis
│       ├── week-week*-*.md            # Markdown picks
│       ├── week-week*-*.csv           # CSV picks
│       └── *-analysis-*.md            # Analysis reports
└── models/                            # ML model files
```

## 🎮 Weekly Workflow

### Thursday (Pick Generation)
1. **Scrape Data**: `python scrape_cbs_expert_picks_v3.py --week N`
2. **Generate Picks**: `python enhanced_weekly_picks_generator.py --week N --strategy odds_enhanced`
3. **Review Output**: Check `data/outputs/2025/week-weekN-*.md`

### Monday (Analysis)
1. **Update Results**: System automatically updates with game outcomes
2. **Analyze Performance**: `python analyze_prior_week.py --week N`
3. **Retrain Models**: ML models automatically retrain with new data

## 🔍 Key Features Explained

### Betting Odds Integration
- Converts American odds to win probabilities
- Identifies market consensus vs expert opinion
- Uses odds as primary factor (70% weight) in odds_enhanced strategy

### Expert Consensus Analysis
- Scrapes 7 CBS Sports experts
- Calculates consensus percentages
- Identifies universal (7/7) and near-universal (6/7) consensus

### Contrarian Strategy
- Fades popular picks based on historical consensus failures
- Assigns lower confidence points to higher-risk contrarian picks
- Tracks consensus failure patterns from previous weeks

### Machine Learning Enhancement
- Learns from historical accuracy data
- Improves confidence point assignment over time
- Incorporates team performance trends and travel factors

## 📊 Output Files

### Pick Files
- **Markdown**: `week-weekN-strategy-enhanced-picks.md` - Human-readable picks
- **CSV**: `week-weekN-strategy-enhanced-picks.csv` - Machine-readable picks

### Analysis Files
- **Performance**: `weekN-analysis-summary.md` - Strategy comparison
- **Tracking**: `weekN-model-tracking.json` - ML model performance
- **Consensus**: `weekN-consensus-failure-analysis.md` - Historical patterns

## 🎯 Strategy Recommendations

### For Conservative Players
- Use **Expert Consensus** strategy
- Focus on games with 6/7 or 7/7 expert agreement
- Avoid contrarian approaches

### For Aggressive Players
- Use **High Confidence Fades** strategy
- Target universal consensus games for maximum upside
- Accept higher risk for higher reward

### For Balanced Approach
- Use **Odds Enhanced** strategy (recommended)
- Combines market intelligence with expert opinion
- Provides good balance of accuracy and upside

## 🔧 Troubleshooting

### Common Issues

1. **Missing Expert Data**
   ```bash
   # Re-scrape expert picks
   python scrape_cbs_expert_picks_v3.py --week 8
   ```

2. **Database Errors**
   ```bash
   # Reinitialize database
   python database_manager.py --init
   ```

3. **Missing Dependencies**
   ```bash
   # Install requirements
   pip install -r requirements.txt
   ```

### Performance Issues

- **Slow Scraping**: CBS Sports may rate limit - wait between requests
- **Database Locks**: Ensure only one process accesses database at a time
- **Memory Usage**: Large datasets may require chunked processing

## 📈 Future Enhancements

### Planned Features
- **Real-time Odds**: Live odds updates during games
- **Weather Integration**: Weather impact on outdoor games
- **Injury Reports**: Player availability impact
- **Advanced ML**: Deep learning models for pick optimization
- **Web Interface**: Browser-based pick management

### Data Sources
- **ESPN API**: Additional expert picks and stats
- **Weather API**: Game-day weather conditions
- **Injury API**: Player availability data
- **Social Media**: Sentiment analysis for team momentum

## 🤝 Contributing

### Development Setup
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Initialize database: `python database_manager.py --init`
4. Run tests: `python -m pytest tests/`

### Code Standards
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include type hints for function parameters
- Write tests for new features

## 📄 License

This project is for personal use in NFL confidence pool analysis. Please respect CBS Sports' terms of service when scraping their data.

## 🏆 Success Metrics

The system aims to:
- **Win Weekly Pools**: Finish in top 25% of participants
- **Improve Over Time**: Increase accuracy through ML learning
- **Beat Expert Consensus**: Outperform pure expert picks
- **Minimize Risk**: Avoid catastrophic weeks with multiple high-confidence losses

---

**Happy Picking! 🏈**

For questions or issues, please check the troubleshooting section or review the generated analysis files in `data/outputs/2025/`.