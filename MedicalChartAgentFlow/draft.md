# AI Medical Chart Validation — 2-Hour Demo Plan

> Streamlit · sqlite3 · pdfplumber · 4 files · zero LLM · zero frontend framework

---

## What We Keep, What We Cut

| V1 Plan | Demo Plan | Why |
|---------|-----------|-----|
| React + Vite + Zustand | ~~Cut~~ → Streamlit | Streamlit handles upload, progress, charts natively |
| FastAPI + WebSocket | ~~Cut~~ → Streamlit runs in-process | No server needed for demo |
| SQLAlchemy + Alembic | ~~Cut~~ → `sqlite3` (built-in) | Zero config, no migrations |
| spaCy + icd10-cm | ~~Cut~~ → regex + keyword list | 80% coverage, zero setup |
| 12 vibe prompts | → 3 prompts | One per file |
| 14 sprints / 14 days | → 4 × 30-min blocks | Fits 2 hours |
| pytest + Docker | ~~Cut~~ → manual test with sample data | Demo, not production |
| Real chart PDFs | → `.txt` sample files | Skip PDF parsing complexity |

**The 4 agents still exist and still do real work — just as plain Python functions, not classes.**

---

## Final File Structure (4 files total)

```
medchart_demo/
├── app.py              # Streamlit UI — all 3 tabs (~220 lines)
├── agents.py           # 4 agent functions + scoring logic (~150 lines)
├── db.py               # sqlite3 init + read/write helpers (~60 lines)
├── requirements.txt    # 4 packages
└── sample_data/
    ├── chart_MBR001.txt    # Approved case (clean chart)
    ├── chart_MBR002.txt    # Rejected case (diagnosis mismatch)
    ├── chart_MBR003.txt    # Manual review case (date anomaly)
    └── gap_report.csv      # 3 gap requirements for MBR001–003
```

---

## Tech Stack

```
streamlit          # UI: upload + progress + dashboard
pdfplumber         # PDF reading (fallback; txt files used for demo)
pandas             # Gap report CSV parsing
```

That's it. `sqlite3` is Python built-in. No pip installs beyond these three.

---

## Sample Data to Bundle

### `sample_data/gap_report.csv`
```csv
member_id,gap_id,gap_description,required_icd_codes,window_start,window_end
MBR001,G1,Annual wellness visit,Z00.00,2024-01-01,2024-12-31
MBR002,G2,Breast cancer screening,Z12.31,2024-01-01,2024-12-31
MBR003,G3,Diabetes HbA1c check,E11.9,2024-07-01,2024-12-31
```

### `sample_data/chart_MBR001.txt` — Clean (should → Approved)
```
Member ID: MBR001
Visit Date: 2024-09-15
Provider NPI: 1234567890
Diagnosis Codes: Z00.00, Z23
Medications: Lisinopril 10mg daily
Lab Results: HbA1c: 6.8 on 2024-09-15, BP: 118/76
Notes: Annual wellness completed. Preventive care up to date.
```

### `sample_data/chart_MBR002.txt` — Mismatch (should → Rejected)
```
Member ID: MBR002
Visit Date: 2024-11-20
Provider NPI: 9876543210
Diagnosis Codes: E11.9, Z79.4
Medications: Metformin 500mg twice daily
Lab Results: HbA1c: 7.9 on 2024-11-20
Notes: Diabetes management follow-up. No screening performed.
```

### `sample_data/chart_MBR003.txt` — Date anomaly (should → Manual Review)
```
Member ID: MBR003
Visit Date: 2024-12-01
Provider NPI: 5551234567
Diagnosis Codes: E11.9, Z13.1
Medications: Metformin 1000mg daily, Jardiance 10mg
Lab Results: HbA1c: 8.2 on 2023-03-10
Notes: Diabetes monitoring visit.
```

---

## Database Schema (sqlite3, 2 tables only)

```sql
CREATE TABLE IF NOT EXISTS results (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id   TEXT NOT NULL,
    filename    TEXT NOT NULL,
    decision    TEXT NOT NULL,        -- approved | rejected | manual_review
    confidence  REAL NOT NULL,
    gap_score   REAL,
    disc_count  INTEGER DEFAULT 0,
    flags       TEXT,                 -- pipe-separated flag descriptions
    reasoning   TEXT,                 -- JSON string for score breakdown
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

One table. No foreign keys. No migrations.

---

## Agent Logic (`agents.py`)

### Function 1: `run_extract_agent(text: str) -> dict`

```python
# No LLM, no spaCy — pure regex on plain text
import re

KNOWN_ICD = {"Z00.00","Z12.31","E11.9","Z23","Z79.4","Z13.1","E11.65"}

def run_extract_agent(text):
    member_id = re.search(r"Member ID:\s*(\S+)", text)
    visit_date = re.search(r"Visit Date:\s*([\d-]+)", text)
    npi = re.search(r"Provider NPI:\s*(\d+)", text)
    icd_line = re.search(r"Diagnosis Codes:\s*(.+)", text)
    lab_line = re.search(r"Lab Results:\s*(.+)", text)

    raw_codes = [c.strip() for c in icd_line.group(1).split(",")] if icd_line else []
    valid_codes = [c for c in raw_codes if c in KNOWN_ICD]

    # Extract HbA1c value
    hba1c = re.search(r"HbA1c:\s*([\d.]+)", text)

    return {
        "member_id":  member_id.group(1) if member_id else None,
        "visit_date": visit_date.group(1) if visit_date else None,
        "npi":        npi.group(1) if npi else None,
        "icd_codes":  valid_codes,
        "all_codes":  raw_codes,
        "hba1c":      float(hba1c.group(1)) if hba1c else None,
        "raw_text":   text
    }
```

### Function 2: `run_gap_match_agent(extracted: dict, gap_row: dict) -> dict`

```python
from datetime import date

def run_gap_match_agent(extracted, gap_row):
    scores = {}

    # R1: ICD code match (weight 0.5)
    required = [c.strip() for c in gap_row["required_icd_codes"].split("|")]
    found = set(extracted["icd_codes"])
    icd_score = 1.0 if any(r in found for r in required) else 0.0
    scores["icd_match"] = icd_score

    # R2: Visit date in window (weight 0.4)
    try:
        vd = date.fromisoformat(extracted["visit_date"])
        ws = date.fromisoformat(gap_row["window_start"])
        we = date.fromisoformat(gap_row["window_end"])
        date_score = 1.0 if ws <= vd <= we else 0.0
    except:
        date_score = 0.0
    scores["date_in_window"] = date_score

    # R3: Provider NPI present (weight 0.1)
    scores["provider_npi"] = 1.0 if extracted.get("npi") else 0.0

    composite = scores["icd_match"]*0.5 + scores["date_in_window"]*0.4 + scores["provider_npi"]*0.1
    return {"composite": round(composite, 2), "per_rule": scores}
```

### Function 3: `run_discrepancy_agent(extracted: dict) -> list`

```python
def run_discrepancy_agent(extracted):
    flags = []

    # D1: HbA1c physiologically impossible
    if extracted.get("hba1c") and (extracted["hba1c"] > 15 or extracted["hba1c"] < 2):
        flags.append({"severity": "high", "msg": f"HbA1c={extracted['hba1c']} is outside physiological range"})

    # D2: Lab date vs visit date gap (simple check via regex in raw text)
    import re
    lab_dates = re.findall(r"HbA1c:.*?on\s*([\d-]+)", extracted.get("raw_text",""))
    if lab_dates and extracted.get("visit_date"):
        from datetime import date
        try:
            vd = date.fromisoformat(extracted["visit_date"])
            ld = date.fromisoformat(lab_dates[0])
            gap_days = abs((vd - ld).days)
            if gap_days > 365:
                flags.append({"severity": "high", "msg": f"Lab date {lab_dates[0]} is {gap_days} days from visit"})
            elif gap_days > 180:
                flags.append({"severity": "medium", "msg": f"Lab date {lab_dates[0]} is {gap_days} days from visit"})
        except:
            pass

    # D3: Unknown ICD codes in chart (potential typos)
    unknown = [c for c in extracted.get("all_codes", []) if c not in extracted.get("icd_codes", [])]
    if unknown:
        flags.append({"severity": "low", "msg": f"Unrecognized codes: {', '.join(unknown)}"})

    # D4: Missing member ID
    if not extracted.get("member_id"):
        flags.append({"severity": "high", "msg": "Member ID not found in chart"})

    return flags
```

### Function 4: `run_decision_agent(gap: dict, flags: list, extracted: dict) -> dict`

```python
def run_decision_agent(gap_result, flags, extracted):
    base = gap_result["composite"]

    # Penalties
    high   = sum(1 for f in flags if f["severity"] == "high")
    medium = sum(1 for f in flags if f["severity"] == "medium")
    low    = sum(1 for f in flags if f["severity"] == "low")
    penalty = (high * 0.20) + (medium * 0.10) + (low * 0.03)

    score = round(max(0.0, min(1.0, base - penalty)), 2)

    # Hard overrides — no LLM, pure logic
    if not extracted.get("member_id"):
        return {"decision": "rejected", "score": score, "reason": "Missing member ID (hard reject)"}
    if high > 0:
        return {"decision": "manual_review", "score": score, "reason": f"{high} high-severity flag(s) found"}
    if gap_result["per_rule"]["icd_match"] == 0.0:
        return {"decision": "rejected", "score": score, "reason": "Required diagnosis code not in chart"}

    # Threshold routing
    if score >= 0.85:
        decision = "approved"
    elif score <= 0.40:
        decision = "rejected"
    else:
        decision = "manual_review"

    return {"decision": decision, "score": score, "reason": f"Score {score} (base {base} - penalty {round(penalty,2)})"}
```

---

## Streamlit UI (`app.py`) — 3 Tabs

### Tab 1: Validate a Chart
```
[ Upload chart file (txt or pdf) ]     [ Use sample data instead ▾ ]
[ Select gap report (csv) ]            [ Use bundled gap_report.csv ]

                    [ Run Validation ]

━━━━━━━━━━━━━━━━ Agent Progress ━━━━━━━━━━━━━━━━
  ✅  Extract Agent      — MBR001 | 3 ICD codes | visit: 2024-09-15
  ✅  Gap Match Agent    — Score: 1.0 | ICD: ✓ | Date: ✓ | NPI: ✓
  ✅  Discrepancy Agent  — 0 flags found
  ✅  Decision Agent     — APPROVED (confidence: 0.97)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Tab 2: Results Table
```
Filter: [All ▾]  [Last 7 days ▾]

Member ID  Decision        Confidence  Flags  Date
MBR001     ✅ Approved     97%         0      2024-12-01
MBR002     ❌ Rejected     28%         1      2024-12-01
MBR003     ⚠  Manual Rev  55%         1      2024-12-01
```

### Tab 3: Dashboard
```
╔══════════╗  ╔══════════╗  ╔══════════╗  ╔══════════╗
║ Total: 3 ║  ║  ✅  1   ║  ║  ❌  1   ║  ║  ⚠  1   ║
╚══════════╝  ╚══════════╝  ╚══════════╝  ╚══════════╝
              Approved       Rejected       Review

[Bar chart — decisions by date]
```

---

## 3 Vibe Coding Prompts

### Prompt A — `db.py` + `agents.py` + sample data (30 min)

Paste this into Cursor or IBM Bob:

```
Create a Python file called db.py using only the built-in sqlite3 module.

It must have these functions:
1. init_db() — creates a file called medchart.db with this single table:
   results(id INTEGER PRIMARY KEY AUTOINCREMENT, member_id TEXT, filename TEXT,
   decision TEXT, confidence REAL, gap_score REAL, disc_count INTEGER,
   flags TEXT, reasoning TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)

2. save_result(member_id, filename, decision, confidence, gap_score, disc_count, flags_list, reasoning_dict)
   — inserts a row; flags_list joined with " | "; reasoning_dict stored as JSON string

3. get_all_results() — returns all rows as list of dicts (use row_factory = sqlite3.Row)

4. get_summary() — returns dict: {total, approved, rejected, manual_review}

---

Create a Python file called agents.py with exactly 4 functions:

run_extract_agent(text: str) -> dict
  Uses regex only (no external libraries). Extracts:
  member_id (pattern: "Member ID: VALUE")
  visit_date (pattern: "Visit Date: YYYY-MM-DD")
  npi (pattern: "Provider NPI: DIGITS")
  icd_codes — split from "Diagnosis Codes: A, B, C", validate each against this set:
    {"Z00.00","Z12.31","E11.9","Z23","Z79.4","Z13.1","E11.65"}
  hba1c — float from "HbA1c: NUMBER"
  Returns dict with all fields. Missing fields = None.

run_gap_match_agent(extracted: dict, gap_row: dict) -> dict
  gap_row has keys: required_icd_codes (comma-separated), window_start, window_end
  R1 ICD match (weight 0.5): 1.0 if any required code in extracted icd_codes else 0.0
  R2 Date in window (weight 0.4): 1.0 if visit_date between window_start and window_end else 0.0
  R3 NPI present (weight 0.1): 1.0 if npi not None else 0.0
  composite = R1*0.5 + R2*0.4 + R3*0.1
  Returns {"composite": float, "per_rule": {icd_match, date_in_window, provider_npi}}

run_discrepancy_agent(extracted: dict) -> list
  Returns list of {"severity": "high"|"medium"|"low", "msg": str}
  Check D1: HbA1c > 15 or < 2 → high flag
  Check D2: find date after "HbA1c: X on DATE" in raw text, if gap > 365 days from visit_date → high; if > 180 days → medium
  Check D3: codes in all_codes not in icd_codes → low flag "Unrecognized codes: ..."
  Check D4: member_id is None → high flag "Member ID not found"

run_decision_agent(gap_result: dict, flags: list, extracted: dict) -> dict
  base = gap_result["composite"]
  penalty = (count of high flags * 0.20) + (medium * 0.10) + (low * 0.03)
  score = max(0.0, min(1.0, base - penalty)), rounded to 2 decimals
  Hard override rules (check in order, return immediately):
    - member_id is None → rejected, reason "Missing member ID"
    - any high severity flag → manual_review, reason "High severity flag found"
    - icd_match == 0.0 → rejected, reason "Required diagnosis not found"
  Threshold: score >= 0.85 → approved; score <= 0.40 → rejected; else → manual_review
  Return {"decision": str, "score": float, "reason": str}

---

Also create these sample files:

sample_data/gap_report.csv:
member_id,gap_id,gap_description,required_icd_codes,window_start,window_end
MBR001,G1,Annual wellness visit,Z00.00,2024-01-01,2024-12-31
MBR002,G2,Breast cancer screening,Z12.31,2024-01-01,2024-12-31
MBR003,G3,Diabetes HbA1c check,E11.9,2024-07-01,2024-12-31

sample_data/chart_MBR001.txt:
Member ID: MBR001
Visit Date: 2024-09-15
Provider NPI: 1234567890
Diagnosis Codes: Z00.00, Z23
Medications: Lisinopril 10mg daily
Lab Results: HbA1c: 6.8 on 2024-09-15, BP: 118/76
Notes: Annual wellness completed. Preventive care up to date.

sample_data/chart_MBR002.txt:
Member ID: MBR002
Visit Date: 2024-11-20
Provider NPI: 9876543210
Diagnosis Codes: E11.9, Z79.4
Medications: Metformin 500mg twice daily
Lab Results: HbA1c: 7.9 on 2024-11-20
Notes: Diabetes management follow-up. No screening performed.

sample_data/chart_MBR003.txt:
Member ID: MBR003
Visit Date: 2024-12-01
Provider NPI: 5551234567
Diagnosis Codes: E11.9, Z13.1
Medications: Metformin 1000mg daily, Jardiance 10mg
Lab Results: HbA1c: 8.2 on 2023-03-10
Notes: Diabetes monitoring visit.
```

---

### Prompt B — `app.py` Tab 1: Upload + Agent Progress (45 min)

```
Create a Streamlit app in app.py. Import db and agents modules.

At the top: call db.init_db() on startup.

The app has 3 tabs: "Validate", "Results", "Dashboard".

Build Tab 1: Validate

Layout — two columns:
Left column:
  - st.file_uploader for chart file (accepts txt, pdf)
  - OR st.selectbox "Use sample chart:" with options: chart_MBR001.txt, chart_MBR002.txt, chart_MBR003.txt
  - When sample selected, read text from sample_data/ folder
  - If PDF uploaded, use pdfplumber to extract text (pip import pdfplumber)
  - If txt uploaded, decode as utf-8

Right column:
  - st.file_uploader for gap report CSV (accepts csv)
  - OR checkbox "Use bundled gap_report.csv" — reads from sample_data/gap_report.csv
  - Parse CSV with pandas, show st.dataframe of gap report rows

Below both columns: st.button("Run Validation") — full width

When button clicked:
  Run all 4 agents in sequence. Show progress using 4 separate st.status() blocks.
  Each st.status() shows:
    - Label: "Extract Agent", "Gap Match Agent", "Discrepancy Agent", "Decision Agent"
    - State: "running" while executing, "complete" or "error" after
    - Inside each block, show the output as st.json() or st.write() after completion

  After all 4 complete:
    Show a result banner:
      - If approved: st.success("APPROVED — Confidence: XX%")
      - If rejected: st.error("REJECTED — Reason: ...")
      - If manual_review: st.warning("MANUAL REVIEW — Reason: ...")

  Save result to DB via db.save_result(...)

Match chart to gap report by member_id extracted from chart.
If member_id not found in gap report, show st.warning and use first gap row as fallback.
```

---

### Prompt C — `app.py` Tab 2 + Tab 3: Results + Dashboard (30 min)

```
In the same app.py, build Tab 2 and Tab 3:

Tab 2: Results
  Call db.get_all_results() at top of tab.
  Filter row: st.selectbox "Filter by decision" — options: All, approved, rejected, manual_review
  Show results as st.dataframe with these columns:
    member_id, decision (with emoji: ✅ approved, ❌ rejected, ⚠️ manual_review),
    confidence (as % string), disc_count, flags, created_at
  Each row: clicking "View Detail" (use st.expander per row) shows:
    - Per-rule scores from reasoning JSON
    - Full flags list
    - Raw chart text preview (first 300 chars)

Tab 3: Dashboard
  Call db.get_summary() for the 4 metric cards.
  Show 4 st.metric() in a 4-column layout:
    Total Processed, Approved (green delta), Rejected (red delta), Manual Review (orange delta)

  Below metrics, show a bar chart using st.bar_chart:
    Group results by decision, count per day
    Use pandas to pivot: created_at date as index, decision counts as columns

  Below chart: st.caption("All decisions are algorithmic — zero LLM used for routing.")
```

---

## 30-Minute Block Schedule

| Block | Task | Time |
|-------|------|------|
| Block 1 | Run Prompt A in Cursor · verify sample data files · python db.py test | 0:00–0:30 |
| Block 2 | Run Prompt B in Cursor · streamlit run app.py · test Tab 1 with sample MBR001 | 0:30–1:15 |
| Block 3 | Run Prompt C in Cursor · test Tab 2 + Tab 3 · run all 3 samples to populate DB | 1:15–1:45 |
| Block 4 | Demo polish: fix any UI quirks · write requirements.txt · do a dry run demo walkthrough | 1:45–2:00 |

---

## `requirements.txt`

```
streamlit
pdfplumber
pandas
```

---

## Demo Script (5-minute walkthrough)

1. Open `Tab 3: Dashboard` — show empty state (0 processed). "This is where the report lives."
2. Go to `Tab 1: Validate` — select `chart_MBR001.txt` + bundled gap report. Hit "Run Validation."
3. Watch 4 agent status blocks animate live. "Each agent is a Python function. No LLM."
4. APPROVED banner appears. Jump to Tab 3 — dashboard updates.
5. Repeat with MBR002 (rejected) and MBR003 (manual review) — dashboard fills to 3 records.
6. Go to `Tab 2: Results` — show the table, expand a row to show score breakdown.
7. Close: "In production this runs in 10 seconds per chart. Today's demo was 3 charts in 2 minutes."

---

## What to Say When Asked "Why No LLM for Decision?"

> "The decision is purely arithmetic — a weighted score minus penalties for flags. This is intentional. Every approval or rejection is 100% auditable: you can see exactly which rule fired, what the score was, and why it routed the way it did. An LLM decision is a black box. A human reviewer needs to trust the system, and that trust requires explainability."

---

## Post-Demo Upgrade Path

If stakeholders are impressed and want to take it further:

| Addition | Effort | What it adds |
|---------|--------|--------------|
| Real PDF chart parsing via pdfplumber | +2 hours | Handle real hospital chart PDFs |
| FastAPI backend + React UI | +3 days | Proper multi-user web app |
| NPI Luhn validation | +1 hour | Stronger provider check |
| Human reviewer override in UI | +2 hours | PATCH result with reviewer name |
| CSV export button | +30 min | Download results table |
| Auth (login page) | +1 day | Protect the UI |
