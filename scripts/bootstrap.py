#!/usr/bin/env python3
# Creates year/week folders to keep things tidy (optional helper)

import argparse
import os
from pathlib import Path
from datetime import datetime

def ensure(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=datetime.utcnow().year)
    ap.add_argument("--week", type=str, default="auto")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    ensure(root / f"data/raw/{args.year}")
    ensure(root / f"data/outputs/{args.year}")
    print(f"Ready: data/raw/{args.year} and data/outputs/{args.year}/")

if __name__ == "__main__":
    main()
