#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import pandas as pd

from providers.espn import get_scoreboard_by_range, extract_events, events_with_probabilities

def assign_confidence_points(df: pd.DataFrame, pool_size: int) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(by=["pick_prob", "commence_time"], ascending=[False, True]).reset_index(drop=True)
    n = min(pool_size, len(df)) if pool_size else len(df)
    df["confidence_points"] = list(range(n, n - len(df), -1))
    return df

def export(df: pd.DataFrame, out_csv: str, out_md: str):
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    cols = ["event_id","commence_time","away_team","home_team","away_prob","home_prob","pick_team","pick_prob","confidence_points","bookmaker"]
    for c in cols:
        if c not in df.columns:
            df[c] = None
    df[cols].to_csv(out_csv, index=False)
    disp = df.sort_values("confidence_points", ascending=False).copy()
    disp["prob%"] = (disp["pick_prob"]*100).round(1)
    disp["commence_time"] = disp["commence_time"].astype(str).str.replace("T"," ").str.replace("Z","")
    lines = ["| Points | Pick | Win% | Home | Away | Kickoff (UTC) | Source |",
             "|---:|---|---:|---|---|---|---|"]
    for _, r in disp.iterrows():
        lines.append(f"| {int(r['confidence_points'])} | {r['pick_team']} | {r['prob%']:.1f} | {r['home_team']} | {r['away_team']} | {r['commence_time']} | {r['bookmaker']} |")
    with open(out_md, "w") as f:
        f.write("\n".join(lines))

def cmd_auto(args):
    today = dt.date.today()
    end = today + dt.timedelta(days=args.days)
    sb = get_scoreboard_by_range(today, end)
    rows = extract_events(sb)
    df = events_with_probabilities(rows, sleep_between=args.sleep)
    if "pick_prob" not in df or df["pick_prob"].isna().any():
        df["pick_prob"] = df[["home_prob","away_prob"]].max(axis=1)
        df["pick_team"] = df.apply(lambda r: r["home_team"] if (r["home_prob"] or 0) >= (r["away_prob"] or 0) else r["away_team"], axis=1)
    df = assign_confidence_points(df, pool_size=args.pool_size)
    year = dt.datetime.utcnow().year
    out_csv = f"data/outputs/{year}/espn-week-auto-picks.csv"
    out_md  = f"data/outputs/{year}/espn-week-auto-picks.md"
    export(df, out_csv, out_md)
    print(f"Wrote {out_csv} and {out_md} (games={len(df)})")

def build_parser():
    p = argparse.ArgumentParser(description="NFL Confidence Picks via ESPN (no API key)")
    p.add_argument("--days", type=int, default=9, help="Include games through this many days ahead (default 9)")
    p.add_argument("--pool-size", type=int, default=16, help="Total confidence points to distribute (default 16)")
    p.add_argument("--sleep", type=float, default=0.0, help="Seconds to sleep between ESPN probability calls (avoid rate limits)")
    sub = p.add_subparsers(dest="cmd", required=True)
    pa = sub.add_parser("auto", help="Fetch scoreboard + probabilities, export picks")
    pa.set_defaults(func=cmd_auto)
    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
