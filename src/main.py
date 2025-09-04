#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv

# ----------------------- Utilities -----------------------

def american_to_implied_prob(odds: int) -> float:
    """Convert American odds to implied probability (0..1), without removing vig."""
    if odds is None:
        return None
    try:
        odds = int(odds)
    except (ValueError, TypeError):
        return None
    if odds > 0:
        return 100.0 / (odds + 100.0)
    else:
        return -odds / (-odds + 100.0)

def devig_two_way(p1: float, p2: float) -> Tuple[Optional[float], Optional[float]]:
    """Normalize two implied probs to sum to 1 (simple de-vig)."""
    if p1 is None or p2 is None:
        return None, None
    s = p1 + p2
    if s <= 0:
        return None, None
    return p1 / s, p2 / s

def ensure_dir(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def iso_now():
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def parse_bookmakers_preference(pref_str: Optional[str]) -> List[str]:
    if not pref_str:
        return []
    return [b.strip() for b in pref_str.split(",") if b.strip()]

# ----------------------- Odds API Fetch -----------------------

def fetch_odds(days: int = 9, regions: str = "us", bookmakers_pref: Optional[str] = None) -> Dict:
    """
    Fetch upcoming NFL H2H odds from The Odds API.
    Docs: https://the-odds-api.com/
    """
    load_dotenv()
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        raise SystemExit("Missing ODDS_API_KEY in environment. Copy .env.example to .env and set your key.")

    url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
    params = {
        "regions": regions or os.getenv("REGIONS", "us"),
        "markets": "h2h",
        "oddsFormat": "american",
        "apiKey": api_key,
        "dateFormat": "iso",
        "daysFrom": 0,
        "daysTo": days,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # Attach our fetch metadata
    return {
        "fetched_at": iso_now(),
        "params": params,
        "events": data,
        "bookmakers_preference": parse_bookmakers_preference(bookmakers_pref or os.getenv("BOOKMAKERS", "")),
    }

def pick_bookmakers_line(event: Dict, preferred: List[str]) -> Optional[Dict]:
    """
    From a single event, choose a bookmaker/market that has both sides' H2H prices.
    We try preferred order first; otherwise fall back to first complete market found.
    """
    bms = event.get("bookmakers", [])
    # try preferred order
    for name in preferred:
        for bm in bms:
            if bm.get("title") == name:
                for m in bm.get("markets", []):
                    if m.get("key") == "h2h" and len(m.get("outcomes", [])) >= 2:
                        return {"bookmaker": name, "market": m}
    # fallback: any complete h2h
    for bm in bms:
        for m in bm.get("markets", []):
            if m.get("key") == "h2h" and len(m.get("outcomes", [])) >= 2:
                return {"bookmaker": bm.get("title"), "market": m}
    return None

def normalize_event_row(event: Dict, preferred: List[str]) -> Optional[Dict]:
    """
    Produce a flat row with away/home teams, moneylines, commence_time, etc.
    """
    home = event.get("home_team")
    away = event.get("away_team")
    commence = event.get("commence_time")

    pick = pick_bookmakers_line(event, preferred)
    if not pick:
        return None
    m = pick["market"]
    outcomes = m.get("outcomes", [])

    # Outcomes can be unordered; map by name
    prices: Dict[str, Optional[int]] = {}
    for o in outcomes:
        try:
            prices[o["name"]] = int(o.get("price"))
        except (TypeError, ValueError):
            prices[o["name"]] = None

    away_ml = prices.get(away)
    home_ml = prices.get(home)

    return dict(
        event_id=event.get("id"),
        bookmaker=pick["bookmaker"],
        commence_time=commence,
        away_team=away,
        home_team=home,
        away_ml=away_ml,
        home_ml=home_ml,
    )

def events_to_dataframe(payload: Dict) -> pd.DataFrame:
    preferred = payload.get("bookmakers_preference", [])
    rows = []
    for ev in payload.get("events", []):
        row = normalize_event_row(ev, preferred)
        if row:
            rows.append(row)
    df = pd.DataFrame(rows)
    # compute raw implied probs
    df["away_implied_raw"] = df["away_ml"].apply(american_to_implied_prob)
    df["home_implied_raw"] = df["home_ml"].apply(american_to_implied_prob)
    # de-vig
    dev = df.apply(lambda r: devig_two_way(r["away_implied_raw"], r["home_implied_raw"]), axis=1)
    df["away_prob"] = [t[0] if t else None for t in dev]
    df["home_prob"] = [t[1] if t else None for t in dev]
    # pick side
    df["pick_team"] = df.apply(lambda r: r["home_team"] if (r["home_prob"] or 0) >= (r["away_prob"] or 0) else r["away_team"], axis=1)
    df["pick_prob"] = df.apply(lambda r: max(r["home_prob"] or 0, r["away_prob"] or 0), axis=1)
    return df

# ----------------------- Confidence Assignment -----------------------

def assign_confidence_points(df: pd.DataFrame, pool_size: Optional[int] = None) -> pd.DataFrame:
    """
    Given a DataFrame with 'pick_prob', assign descending confidence points.
    If pool_size is None, equals the number of games.
    """
    df = df.copy()
    df = df.sort_values(by=["pick_prob", "commence_time"], ascending=[False, True]).reset_index(drop=True)
    n = pool_size or len(df)
    # Highest prob gets n, next n-1, ... at least 1
    df["confidence_points"] = list(range(n, n - len(df), -1))
    return df

# ----------------------- I/O -----------------------

def save_raw_json(data: Dict, outpath: str):
    ensure_dir(outpath)
    with open(outpath, "w") as f:
        json.dump(data, f, indent=2)

def load_raw_json(inpath: str) -> Dict:
    with open(inpath, "r") as f:
        return json.load(f)

def export_picks(df: pd.DataFrame, out_csv: str, out_md: Optional[str] = None):
    ensure_dir(out_csv)
    # CSV friendly selection
    cols = [
        "event_id", "commence_time",
        "away_team", "home_team",
        "away_ml", "home_ml",
        "away_prob", "home_prob",
        "pick_team", "pick_prob",
        "confidence_points", "bookmaker",
    ]
    # add missing cols if custom CSV input
    for c in cols:
        if c not in df.columns:
            df[c] = None
    df[cols].to_csv(out_csv, index=False)

    if out_md:
        # Pretty markdown table (sorted by points desc)
        display = df.sort_values("confidence_points", ascending=False).copy()
        display["commence_time"] = display["commence_time"].astype(str).str.replace("T", " ").str.replace("Z", "")
        display["prob%"] = (display["pick_prob"] * 100).round(1)
        mcols = ["confidence_points", "pick_team", "prob%", "home_team", "home_ml", "away_team", "away_ml", "commence_time", "bookmaker"]
        lines = ["| Points | Pick | Win% | Home | ML | Away | ML | Kickoff (UTC) | Book |",
                 "|---:|---|---:|---|---:|---|---:|---|---|"]
        for _, r in display[mcols].iterrows():
            line = f"| {int(r['confidence_points'])} | {r['pick_team']} | {r['prob%']:.1f} | {r['home_team']} | {r['home_ml']} | {r['away_team']} | {r['away_ml']} | {r['commence_time']} | {r['bookmaker']} |"
            lines.append(line)
        ensure_dir(out_md)
        with open(out_md, "w") as f:
            f.write("\n".join(lines))

# ----------------------- Manual CSV ingest -----------------------

def load_manual_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # normalize columns
    rename_map = {
        "away odds": "away_ml",
        "home odds": "home_ml",
        "kickoff": "commence_time",
    }
    for k, v in rename_map.items():
        if k in df.columns and v not in df.columns:
            df.rename(columns={k: v}, inplace=True)
    for needed in ["away_team", "home_team", "away_ml", "home_ml"]:
        if needed not in df.columns:
            raise SystemExit(f"Manual CSV is missing required column: {needed}")
    # derive implied / pick same as events pipeline
    df["away_implied_raw"] = df["away_ml"].apply(american_to_implied_prob)
    df["home_implied_raw"] = df["home_ml"].apply(american_to_implied_prob)
    dev = df.apply(lambda r: devig_two_way(r["away_implied_raw"], r["home_implied_raw"]), axis=1)
    df["away_prob"] = [t[0] if t else None for t in dev]
    df["home_prob"] = [t[1] if t else None for t in dev]
    df["pick_team"] = df.apply(lambda r: r["home_team"] if (r["home_prob"] or 0) >= (r["away_prob"] or 0) else r["away_team"], axis=1)
    df["pick_prob"] = df.apply(lambda r: max(r["home_prob"] or 0, r["away_prob"] or 0), axis=1)
    # fill commence_time if missing
    if "commence_time" not in df.columns:
        df["commence_time"] = ""
    df["bookmaker"] = df.get("bookmaker", pd.Series(["manual"]*len(df)))
    df["event_id"] = df.get("event_id", pd.Series(["manual"]*len(df)))
    return df

# ----------------------- CLI -----------------------

def cmd_fetch(args):
    payload = fetch_odds(days=args.days, regions=args.regions, bookmakers_pref=args.bookmakers)
    year = dt.datetime.utcnow().year
    out = args.out or f"data/raw/{year}/week-auto-odds.json"
    save_raw_json(payload, out)
    print(f"Wrote raw odds to {out} (events={len(payload.get('events', []))})")

def cmd_compute(args):
    if args.in_csv:
        df = load_manual_csv(args.in_csv)
    else:
        payload = load_raw_json(args.in_json)
        df = events_to_dataframe(payload)

    df = assign_confidence_points(df, pool_size=args.pool_size)

    # outputs
    year = dt.datetime.utcnow().year
    base_name = args.name or "week-auto"
    out_csv = args.out_csv or f"data/outputs/{year}/{base_name}-picks.csv"
    out_md = args.out_md or f"data/outputs/{year}/{base_name}-picks.md"
    export_picks(df, out_csv=out_csv, out_md=out_md)
    print(f"Wrote {out_csv} and {out_md}")

def cmd_auto(args):
    # fetch then compute
    year = dt.datetime.utcnow().year
    raw_out = f"data/raw/{year}/week-auto-odds.json"
    payload = fetch_odds(days=args.days, regions=args.regions, bookmakers_pref=args.bookmakers)
    save_raw_json(payload, raw_out)

    df = events_to_dataframe(payload)
    df = assign_confidence_points(df, pool_size=args.pool_size)

    out_csv = f"data/outputs/{year}/week-auto-picks.csv"
    out_md = f"data/outputs/{year}/week-auto-picks.md"
    export_picks(df, out_csv=out_csv, out_md=out_md)
    print(f"Auto: wrote {raw_out}, {out_csv}, {out_md} (games={len(df)})")

def build_parser():
    p = argparse.ArgumentParser(description="NFL Confidence-Pick helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    pf = sub.add_parser("fetch", help="Fetch raw odds JSON from The Odds API")
    pf.add_argument("--days", type=int, default=9, help="Days ahead to include (default 9)")
    pf.add_argument("--regions", type=str, default=None, help="Regions parameter (default from .env or 'us')")
    pf.add_argument("--bookmakers", type=str, default=None, help="Preferred bookmakers, comma-separated")
    pf.add_argument("--out", type=str, default=None, help="Output JSON path")
    pf.set_defaults(func=cmd_fetch)

    pc = sub.add_parser("compute", help="Compute picks from raw JSON or manual CSV")
    pc.add_argument("--in-json", dest="in_json", type=str, default=None, help="Input raw odds JSON path")
    pc.add_argument("--in-csv", dest="in_csv", type=str, default=None, help="Manual CSV with away/home ML columns")
    pc.add_argument("--pool-size", type=int, default=None, help="Number of confidence points (defaults to #games)")
    pc.add_argument("--name", type=str, default=None, help="Base name for output files (e.g., week-1)")
    pc.add_argument("--out-csv", type=str, default=None, help="Output CSV path")
    pc.add_argument("--out-md", type=str, default=None, help="Output Markdown path")
    pc.set_defaults(func=cmd_compute)

    pa = sub.add_parser("auto", help="Fetch + compute in one go")
    pa.add_argument("--days", type=int, default=9, help="Days ahead to include (default 9)")
    pa.add_argument("--regions", type=str, default=None, help="Regions parameter (default from .env or 'us')")
    pa.add_argument("--bookmakers", type=str, default=None, help="Preferred bookmakers, comma-separated")
    pa.add_argument("--pool-size", type=int, default=16, help="Number of confidence points (default 16)")
    pa.set_defaults(func=cmd_auto)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
