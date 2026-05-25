"""
fetch_schedule.py
-----------------
Step 1: Fetch Vietnam Airlines domestic schedule from AviationStack.

We only need 2 representative days:
  - One day in Summer season (April–October)
  - One day in Winter season (November–March)

Then we also fetch ~10 holiday days separately.

Usage:
    pip install requests
    python fetch_schedule.py --key YOUR_API_KEY
"""

import requests
import json
import time
import argparse
from datetime import date, timedelta
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────

AIRLINE_IATA = "VN"  # Vietnam Airlines IATA code

# One representative weekday for each season
# (Monday, so we capture full weekday schedule)
SUMMER_SAMPLE_DATE = "2026-06-08"   # Monday in summer
WINTER_SAMPLE_DATE = "2026-11-09"   # Monday in winter

# ALL Vietnam domestic airports Vietnam Airlines serves
VIETNAM_AIRPORTS = {
    "HAN", "SGN", "DAD", "HPH", "VII", "HUI", "PQC", "CXR",
    "UIH", "DLI", "BMV", "VCA", "PXU", "VDH", "TBB", "DIN",
    "VCS", "CAH", "VKG", "VCL", "THD",
}

# Vietnamese public holidays — scrape these separately
# because extra flights are added around them
HOLIDAY_DATES = [
    "2027-01-01",  # New Year
    "2027-01-28",  # Tet eve
    "2027-01-29",  # Tet day 1
    "2027-01-30",  # Tet day 2
    "2027-01-31",  # Tet day 3
    "2027-02-01",  # Tet day 4
    "2027-04-30",  # Reunification Day
    "2027-05-01",  # Labour Day
    "2027-09-02",  # National Day
]

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

# ─── Fetcher ──────────────────────────────────────────────────────────────────

def fetch_flights_for_date(api_key: str, flight_date: str) -> list[dict]:
    """Fetch all VN domestic flights for a given date from AviationStack."""

    url = "http://api.aviationstack.com/v1/flights"
    all_flights = []
    offset = 0
    limit = 100  # max per request on free tier

    print(f"  Fetching {flight_date}...", end="", flush=True)

    while True:
        params = {
            "access_key": api_key,
            "airline_iata": AIRLINE_IATA,
            "flight_date": flight_date,
            "limit": limit,
            "offset": offset,
        }

        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            print(f"\n  ⚠️  Request failed: {e}")
            break

        if "error" in data:
            print(f"\n  ⚠️  API error: {data['error']['message']}")
            break

        flights = data.get("data", [])
        if not flights:
            break

        # Filter domestic Vietnam only — using complete airport set
        domestic = [
            f for f in flights
            if f.get("departure", {}).get("iata") in VIETNAM_AIRPORTS
            and f.get("arrival", {}).get("iata") in VIETNAM_AIRPORTS
        ]
        all_flights.extend(domestic)

        # Paginate
        total = data.get("pagination", {}).get("total", 0)
        offset += limit
        if offset >= total:
            break

        time.sleep(0.5)  # be polite to the API

    print(f" {len(all_flights)} domestic flights found.")
    return all_flights


def clean_flight(f: dict, sample_date: str) -> dict:
    """Extract only the fields we care about from raw API response."""
    dep = f.get("departure", {})
    arr = f.get("arrival", {})
    flight = f.get("flight", {})

    # Extract time only (HH:MM) — date will be reconstructed later
    dep_time = (dep.get("scheduled") or "")[-14:-9] if dep.get("scheduled") else ""
    arr_time = (arr.get("scheduled") or "")[-14:-9] if arr.get("scheduled") else ""

    return {
        "flight_number": flight.get("iata", ""),
        "from_iata": dep.get("iata", ""),
        "from_name": dep.get("airport", ""),
        "to_iata": arr.get("iata", ""),
        "to_name": arr.get("airport", ""),
        "dep_time": dep_time,   # e.g. "06:00"
        "arr_time": arr_time,   # e.g. "08:05"
        "weekday": date.fromisoformat(sample_date).weekday(),  # 0=Mon, 6=Sun
        "sample_date": sample_date,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fetch Vietnam Airlines schedule")
    parser.add_argument("--key", required=True, help="Your AviationStack API key")
    args = parser.parse_args()

    print("=" * 55)
    print("  Vietnam Airlines Schedule Fetcher")
    print("=" * 55)

    # --- Fetch summer and winter base schedules ---
    print("\n📅 Fetching base schedules (2 days)...")

    summer_raw = fetch_flights_for_date(args.key, SUMMER_SAMPLE_DATE)
    winter_raw = fetch_flights_for_date(args.key, WINTER_SAMPLE_DATE)

    summer = [clean_flight(f, SUMMER_SAMPLE_DATE) for f in summer_raw]
    winter = [clean_flight(f, WINTER_SAMPLE_DATE) for f in winter_raw]

    # NOTE: The above only gives us Monday's schedule.
    # For a complete weekly pattern, repeat for each day of the week.
    # Uncomment below if you want all 7 days (uses 14 API calls total):
    #
    # for i in range(1, 7):
    #     d = (date.fromisoformat(SUMMER_SAMPLE_DATE) + timedelta(days=i)).isoformat()
    #     summer += [clean_flight(f, d) for f in fetch_flights_for_date(args.key, d)]
    # ... same for winter

    # --- Fetch holiday dates ---
    print("\n🎉 Fetching holiday schedules...")
    holidays = {}
    for hdate in HOLIDAY_DATES:
        raw = fetch_flights_for_date(args.key, hdate)
        holidays[hdate] = [clean_flight(f, hdate) for f in raw]
        time.sleep(1)

    # --- Save raw data ---
    output = {
        "meta": {
            "airline": "Vietnam Airlines (VN)",
            "summer_sample": SUMMER_SAMPLE_DATE,
            "winter_sample": WINTER_SAMPLE_DATE,
            "fetched_at": str(date.today()),
        },
        "summer_schedule": summer,
        "winter_schedule": winter,
        "holiday_schedules": holidays,
    }

    out_file = OUTPUT_DIR / "vn_raw_schedule.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Saved to {out_file}")
    print(f"   Summer flights: {len(summer)}")
    print(f"   Winter flights: {len(winter)}")
    print(f"   Holiday days:   {len(holidays)}")
    print("\n👉 Now run: python build_year.py")


if __name__ == "__main__":
    main()