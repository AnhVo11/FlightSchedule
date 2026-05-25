# FlightSchedule

Collect the full domestic flight schedule for all 6 Vietnamese airlines, for free.

---

## Airlines Covered

| IATA | Airline |
|------|---------|
| VN   | Vietnam Airlines |
| VJ   | Vietjet Air |
| QH   | Bamboo Airways |
| VU   | Vietravel Airlines |
| BL   | Pacific Airlines |
| 0V   | VASCO |

---

## Folder Structure

```
FlightSchedule/
├── fetch_today.py    ← Run every day for 7-14 days
├── build_year.py     ← Run once after 7+ days of data
├── README.md
└── data/
    ├── 2026-05-25.json     ← one file per day (auto created)
    ├── 2026-05-26.json
    ├── all_days.json        ← combined history (auto created)
    └── vietnam_flights_2026.csv  ← final output
```

---

## Setup

```bash
pip3 install requests
```

Get a free API key at: https://aviationstack.com/signup/free

---

## Step 1 — Run every day for 7-14 days

```bash
python3 fetch_today.py --key YOUR_API_KEY_HERE
```

Run this **once per day**. It will:
- Fetch today's flights for all 6 airlines
- Save them to `data/YYYY-MM-DD.json`
- After 7+ days, automatically detect when the schedule repeats
- Tell you when you can stop

---

## Step 2 — Build the full year (after 7+ days)

```bash
python3 build_year.py --year 2026
```

Output:
- `data/vietnam_flights_2026.csv` ← open in Excel
- `data/vietnam_flights_2026.json` ← use in code

---

## How duplicate detection works

After 7 days you have one sample for each day of the week (Mon–Sun).
The script compares each new day against the same weekday from the previous week.
When 85%+ of flights match → the schedule is repeating → you can stop.

---

## All Airports Covered (21 total)

HAN, SGN, DAD, HPH, VII, HUI, PQC, CXR, UIH, DLI,
BMV, VCA, PXU, VDH, TBB, DIN, VCS, CAH, VKG, VCL, THD