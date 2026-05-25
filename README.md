# Vietnam Airlines Year Schedule

Get the full domestic schedule for Vietnam Airlines in under 1 hour, for free.

---

## Folder Structure

```
flight_schedule/
├── fetch_schedule.py   ← Step 1: pull data from API
├── build_year.py       ← Step 2: expand into full year
├── README.md           ← this file
└── data/               ← create this empty folder manually
```

---

## Setup

```bash
pip install requests
```

Get a **free API key** at: https://aviationstack.com/signup/free
(Free tier = 100 requests/month — enough for this entire project)

---

## Step 1: Fetch the raw schedule

```bash
python fetch_schedule.py --key YOUR_API_KEY_HERE
```

This makes ~11 API calls total:
- 1 call for summer base day (Monday in June)
- 1 call for winter base day (Monday in November)
- 9 calls for Vietnamese public holidays

Output: `data/vn_raw_schedule.json`

### Want a more accurate weekly pattern?

Uncomment the loop in `fetch_schedule.py` to fetch all 7 days of the week
instead of just Monday. This uses 14 API calls instead of 2 for base schedules.

---

## Step 2: Build the full year

```bash
python build_year.py --year 2026
```

Output:
- `data/vn_full_year.csv`  ← open in Excel/Sheets
- `data/vn_full_year.json` ← use in code

---

## Output Format

```
date,flight_number,from_iata,from_name,to_iata,to_name,dep_time,arr_time,is_holiday
2026-01-01,VN123,HAN,Noi Bai,SGN,Tan Son Nhat,06:00,08:05,False
2026-01-01,VN201,SGN,Tan Son Nhat,DAD,Da Nang,07:30,08:45,False
...
```

---

## All Airports Covered (21 total)

| IATA | City | Tier |
|------|------|------|
| HAN  | Hanoi | Hub |
| SGN  | Ho Chi Minh City | Hub |
| DAD  | Da Nang | Hub |
| HPH  | Hai Phong | Mid |
| VII  | Vinh | Mid |
| HUI  | Hue | Mid |
| PQC  | Phu Quoc | Mid |
| CXR  | Nha Trang | Mid |
| UIH  | Quy Nhon | Mid |
| DLI  | Da Lat | Mid |
| BMV  | Buon Ma Thuot | Mid |
| VCA  | Can Tho | Mid |
| PXU  | Pleiku | Small |
| VDH  | Dong Hoi | Small |
| TBB  | Tuy Hoa | Small |
| DIN  | Dien Bien Phu | Small |
| VCS  | Con Dao | Small |
| CAH  | Ca Mau | Small |
| VKG  | Rach Gia | Small |
| VCL  | Chu Lai | Small |
| THD  | Thanh Hoa | Small |

---

## How it works

Airlines use 2 fixed seasons per year (IATA standard):
- **Summer**: Late March → Late October
- **Winter**: Late October → Late March

The weekly schedule is identical within each season.
So we only need to fetch 2 days to know the whole year,
then expand them day-by-day while swapping in actual fetched
data for holidays (when extra flights are added).

---

## Vietnamese Public Holidays Covered

| Holiday | Date |
|---------|------|
| New Year | Jan 1 |
| Tết (4 days) | Late Jan / Early Feb |
| Reunification Day | Apr 30 |
| Labour Day | May 1 |
| National Day | Sep 2 |