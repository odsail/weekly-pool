# NFL Confidence Picks (Python)

This project automates weekly confidence-point picks for NFL pools with **machine learning enhancement**:
1. **Fetch** moneylines (H2H) for upcoming NFL games via **The Odds API**.
2. **Convert** American odds → implied win probabilities and **remove the vig**.
3. **Apply ML model** to optimize confidence point assignments based on historical accuracy.
4. **Store** all data in SQLite database for continuous learning.
5. **Export** results to CSV + Markdown.

> The system learns from your historical picks and gets smarter each week!

---

## Quick Start

```bash
# (optional) create & activate a venv
python3 -m venv .venv && source .venv/bin/activate   # macOS/Linux
# Windows: python -m venv .venv && .venv\Scripts\activate

pip install -r requirements.txt

# Copy the example env and add your key from https://the-odds-api.com/
cp .env.example .env
# then edit .env and set ODDS_API_KEY=...

# Generate picks for Week 2 (analyzes Week 1 results first)
python enhanced_picks_generator.py --week 2 --analyze-prior
```

**Outputs:**
- **Database**: `data/nfl_pool.db` (all historical data)
- **Picks CSV**: `data/outputs/2025/week-week2-picks.csv`
- **Picks Markdown**: `data/outputs/2025/week-week2-picks.md`
- **Analysis**: `data/analysis/2025/week1-analysis.json`

> The system automatically analyzes prior week results and retrains the ML model!

---

## Commands

### Enhanced Picks Generator (Recommended)
```bash
# Generate picks for a specific week with prior week analysis
python enhanced_picks_generator.py --week 3 --analyze-prior

# Generate picks without ML enhancement
python enhanced_picks_generator.py --week 2 --no-ml

# Generate picks without prior week analysis
python enhanced_picks_generator.py --week 2
```

### Legacy Commands (Still Available)
```bash
# Original auto mode (no database/ML)
python src/main.py auto --week 2 --pool-size 16

# Fetch odds only
python src/main.py fetch --week 2 --out data/raw/2025/week-2-odds.json

# Compute picks from JSON
python src/main.py compute --in data/raw/2025/week-2-odds.json --pool-size 16
```

### Analysis Commands
```bash
# Analyze prior week results
python espn_prior_week_analysis.py

# Export analysis to CSV/Markdown
python export_analysis.py

# Check API credits remaining
python check_credits.py
```

### Database Commands
```bash
# Migrate existing data to database
python migrate_to_database.py --year 2025

# Train ML model manually
python ml_model.py

# Update picks with results
python update_pick_results.py
```

---

## How the math works

### Basic Probability Calculation
- Convert American odds to implied probability:
  - If odds > 0:  `p = 100 / (odds + 100)`
  - If odds < 0:  `p = -odds / (-odds + 100)`
- **De-vig** (normalize the two sides so they sum to 1):
  - `p_home = p_home_raw / (p_home_raw + p_away_raw)`
  - `p_away = 1 - p_home`

### Confidence Point Assignment
- **Standard Method**: Sort by `max(p_home, p_away)` and assign highest probability the largest confidence value
- **ML Enhanced**: Uses historical accuracy data to optimize confidence point assignments
- **Auto-adjustment**: Pool size automatically adjusts for bye weeks

### Machine Learning Features
- **Historical Accuracy**: Tracks pick accuracy by confidence level
- **Team Performance**: 4-week rolling averages for each team
- **Odds Trends**: ML odds differences and ratios
- **Seasonal Patterns**: Week-based features and trends

---

## Database Schema

The system uses SQLite to store:
- **Teams**: All 32 NFL teams with conference/division
- **Games**: Results, scores, margins, winners
- **Odds**: Historical odds data from The Odds API
- **Picks**: All picks with confidence points and results
- **Analysis**: Prior week analysis and accuracy metrics

---

## Weekly Workflow

### Thursday (Start of Week N):
```bash
python enhanced_picks_generator.py --week N --analyze-prior
```
This single command:
1. Analyzes Week N-1 results
2. Retrains ML model with new data
3. Generates Week N picks with ML enhancement
4. Stores everything in database
5. Exports picks to files

### Monday (End of Week N):
- System automatically updates picks with actual results
- Week N analysis ready for next week's picks

---

## Notes
- **API Credits**: The Odds API free tier has 500 credits. Monitor usage with `python check_credits.py`
- **ML Model**: Becomes effective after 4-6 weeks of data
- **Fallback**: Uses standard ranking when ML model unavailable
- **Data Sources**: Can integrate ESPN API, SportsDataIO, or other sources

Enjoy, and may your 16s always hit! 🏈
