"""
build_year.py
-------------
Step 2: Reconstruct the full year schedule from the 2 base samples.

Takes the raw data from fetch_schedule.py and expands it into
one row per flight per day for the entire year.

Usage:
    python build_year.py
    python build_year.py --year 2027 --output full_schedule.csv
"""

import json
import csv
import argparse
from datetime import date, timedelta
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────

DATA_DIR = Path("data")
INPUT_FILE = DATA_DIR / "vn_raw_schedule.json"

# IATA season boundaries (approximate, adjust yearly)
# Summer: last Sunday of March → last Saturday of October
SUMMER_START = date(2026, 3, 29)
SUMMER_END   = date(2026, 10, 25)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def is_summer(d: date) -> bool:
    return SUMMER_START <= d <= SUMMER_END


def get_flights_for_day(
    target: date,
    summer: list[dict],
    winter: list[dict],
    holidays: dict[str, list[dict]],
) -> list[dict]:
    """Return all flights for a given date."""

    target_str = target.isoformat()

    # Holiday override — use actual fetched data for special days
    if target_str in holidays:
        base = holidays[target_str]
        for f in base:
            f["date"] = target_str
            f["is_holiday"] = True
        return base

    # Pick season schedule
    base = summer if is_summer(target) else winter
    weekday = target.weekday()

    flights = []
    for f in base:
        if f["weekday"] == weekday:
            row = f.copy()
            row["date"] = target_str
            row["is_holiday"] = False
            flights.append(row)

    return flights


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Build full year schedule")
    parser.add_argument("--year", type=int, default=2026, help="Year to build (default: 2026)")
    parser.add_argument("--output", default="vn_full_year.csv", help="Output filename")
    args = parser.parse_args()

    if not INPUT_FILE.exists():
        print(f"❌ {INPUT_FILE} not found. Run fetch_schedule.py first.")
        return

    # Load raw data
    with open(INPUT_FILE, encoding="utf-8") as f:
        raw = json.load(f)

    summer   = raw["summer_schedule"]
    winter   = raw["winter_schedule"]
    holidays = raw["holiday_schedules"]

    print("=" * 55)
    print("  Vietnam Airlines Year Schedule Builder")
    print("=" * 55)
    print(f"\n📅 Building schedule for {args.year}...")

    all_flights = []
    start = date(args.year, 1, 1)
    end   = date(args.year, 12, 31)
    current = start

    while current <= end:
        daily = get_flights_for_day(current, summer, winter, holidays)
        all_flights.extend(daily)
        current += timedelta(days=1)

    # Sort by date then departure time
    all_flights.sort(key=lambda x: (x["date"], x["dep_time"]))

    # ── Write CSV ──
    out_csv = DATA_DIR / args.output
    fieldnames = [
        "date", "flight_number",
        "from_iata", "from_name",
        "to_iata", "to_name",
        "dep_time", "arr_time",
        "is_holiday",
    ]

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_flights)

    # ── Write JSON too ──
    out_json = DATA_DIR / args.output.replace(".csv", ".json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_flights, f, ensure_ascii=False, indent=2)

    # ── Stats ──
    import os
    csv_size = os.path.getsize(out_csv)
    json_size = os.path.getsize(out_json)

    print(f"\n✅ Done!")
    print(f"   Total flights:  {len(all_flights):,}")
    print(f"   Days covered:   {(end - start).days + 1}")
    print(f"   CSV size:       {csv_size / 1024:.1f} KB  → {out_csv}")
    print(f"   JSON size:      {json_size / 1024:.1f} KB  → {out_json}")
    print(f"\n📊 Quick breakdown:")

    # Count by route
    routes = {}
    for f in all_flights:
        key = f"{f['from_iata']}→{f['to_iata']}"
        routes[key] = routes.get(key, 0) + 1

    top = sorted(routes.items(), key=lambda x: -x[1])[:10]
    print(f"\n   Top 10 routes:")
    for route, count in top:
        print(f"     {route}: {count} flights/year")


if __name__ == "__main__":
    main()