import datetime as dt
import time
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests

SITE_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
CORE_BASE = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl"

def _get(url: str, params: Optional[Dict]=None, timeout: int = 30) -> Dict:
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()

def get_scoreboard_by_range(start_date: dt.date, end_date: dt.date) -> Dict:
    s = start_date.strftime("%Y%m%d")
    e = end_date.strftime("%Y%m%d")
    url = SITE_SCOREBOARD
    params = {"limit": 1000, "dates": f"{s}-{e}"}
    return _get(url, params=params)

def extract_events(scoreboard: Dict) -> List[Dict]:
    out = []
    for ev in scoreboard.get("events", []):
        eid = ev.get("id")
        date = ev.get("date")
        competitions = ev.get("competitions", [])
        if not competitions:
            continue
        comp = competitions[0]
        competitors = comp.get("competitors", [])
        home, away = None, None
        for c in competitors:
            t = c.get("team", {})
            entry = {
                "team_id": t.get("id"),
                "team_abbr": t.get("abbreviation") or t.get("shortDisplayName"),
                "team_name": t.get("displayName") or t.get("name"),
                "home_away": c.get("homeAway"),
            }
            if entry["home_away"] == "home":
                home = entry
            elif entry["home_away"] == "away":
                away = entry
        if home and away:
            out.append({
                "event_id": str(eid),
                "commence_time": date,
                "home_team": home["team_name"],
                "away_team": away["team_name"],
                "home_abbr": home["team_abbr"],
                "away_abbr": away["team_abbr"],
            })
    return out

def _safe_float(x):
    try:
        return float(x)
    except Exception:
        return None

def _fetch_latest_probs_for_event(event_id: str) -> Tuple[Optional[float], Optional[float]]:
    list_url = f"{CORE_BASE}/events/{event_id}/competitions/{event_id}/probabilities"
    js = _get(list_url, params={"limit": 200})

    items = js.get("items") or []
    if items:
        last = items[-1]
        ref = last.get("$ref")
        if ref:
            js = _get(ref)

    home_p = js.get("homeWinPercentage") or js.get("homeTeam", {}).get("winPercentage")
    away_p = js.get("awayWinPercentage") or js.get("awayTeam", {}).get("winPercentage")

    def norm(p):
        if p is None:
            return None
        p = _safe_float(p)
        if p is None:
            return None
        return p/100.0 if p > 1.0 else p

    return norm(home_p), norm(away_p)

def events_with_probabilities(rows: List[Dict], sleep_between: float = 0.0) -> pd.DataFrame:
    records = []
    for r in rows:
        home_p, away_p = None, None
        try:
            home_p, away_p = _fetch_latest_probs_for_event(r["event_id"])
        except Exception:
            pass
        pick_prob = None
        pick_team = None
        if home_p is not None and away_p is not None:
            pick_prob = max(home_p, away_p)
            pick_team = r["home_team"] if home_p >= away_p else r["away_team"]
        records.append({
            **r,
            "home_prob": home_p,
            "away_prob": away_p,
            "pick_prob": pick_prob,
            "pick_team": pick_team,
            "bookmaker": "ESPN-probabilities"
        })
        if sleep_between:
            time.sleep(sleep_between)
    return pd.DataFrame.from_records(records)
