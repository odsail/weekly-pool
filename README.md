# NFL Confidence Picks (Python)

This project automates weekly confidence-point picks for NFL pools:
1. **Fetch** moneylines (H2H) for upcoming NFL games via **The Odds API**.
2. **Convert** American odds → implied win probabilities and **remove the vig**.
3. **Rank** games by win probability and **assign confidence points** (e.g., 16..1).
4. **Export** results to CSV + Markdown.

> If your pool has fewer than 16 games (bye weeks), points automatically adjust to the game count.

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

# Run in "auto" mode: fetch odds + compute picks + export
python src/main.py auto --pool-size 16 --days 9
```

Outputs land under `data/`:
- Raw odds JSON: `data/raw/YYYY/week-<auto>.json`
- Picks CSV: `data/outputs/YYYY/week-<auto>-picks.csv`
- Picks Markdown: `data/outputs/YYYY/week-<auto>-picks.md`

> Don’t want an API? You can **supply a CSV** of games + moneylines and run `compute` directly.
> See **Manual Input** below.

---

## Commands

### Auto (fetch + compute)
```bash
python src/main.py auto --pool-size 16 --days 9 --bookmakers "DraftKings,FanDuel"
```
- `--pool-size`: number of confidence points (usually equals games in your pool).
- `--days`: how many days ahead to pull games (default 9).
- `--bookmakers`: optional preference order; we’ll pick the first book that lists both sides.

### Fetch only
```bash
python src/main.py fetch --days 9 --out data/raw/2025/week-1-odds.json
```

### Compute picks from a previously saved JSON
```bash
python src/main.py compute --in data/raw/2025/week-1-odds.json --pool-size 16
```

### Manual Input (no API)
Prepare a CSV like:
```csv
away_team,home_team,away_ml,home_ml,commence_time
Green Bay Packers,Chicago Bears,120,-140,2025-09-07T17:00:00Z
...
```
Then:
```bash
python src/main.py compute --in-csv my_games.csv --pool-size 16
```

---

## How the math works

- Convert American odds to implied probability:
  - If odds > 0:  `p = 100 / (odds + 100)`
  - If odds < 0:  `p = -odds / (-odds + 100)`
- **De-vig** (normalize the two sides so they sum to 1):
  - `p_home = p_home_raw / (p_home_raw + p_away_raw)`
  - `p_away = 1 - p_home`
- **Assign points**: sort by `max(p_home, p_away)` and give the highest prob the largest confidence value.

If two games are very close, you still maximize **expected points** by assigning higher points to the larger favorite:
> Expected value = win probability × points. Sorting by win probability maximizes the sum.

---

## Notes
- The Odds API free tier may have rate limits. Cache your `raw` JSON and re-run `compute` as needed.
- You can swap in other data sources (ESPN JSON, Elo models, etc.). Just produce the same minimal columns and call `compute`.

Enjoy, and may your 16s always hit.
