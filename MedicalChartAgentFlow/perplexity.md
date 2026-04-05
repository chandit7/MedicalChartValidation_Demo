# Medical Chart Validation System

Deterministic, rule-based validation engine for medical charts against care gap requirements.

## Document Purpose

This document describes the architecture, data flow, decision logic, database design, UI layout, scoring model, error handling, and security considerations for the Medical Chart Validation System.

## Table of Contents

1. System Overview
2. Architecture Design
3. Data Flow
4. Agent Design
5. Decision Logic
6. Database Schema
7. UI/UX Design
8. Scoring Algorithm
9. Error Handling
10. Security Considerations

---

## 1. System Overview

### 1.1 Purpose

The Medical Chart Validation System is a deterministic, rule-based engine that validates medical charts against care gap requirements. It routes charts to one of three outcomes:

- Approved
- Rejected
- Manual Review

### 1.2 Design Principles

#### Zero-LLM Design

- All decisions are algorithmic and deterministic.
- Every decision is auditable and explainable.
- No black-box AI decision-making is used.
- The same input always produces the same result.

#### Simplicity First

- Minimal dependencies.
- Single-file modules.
- No heavy framework dependency.
- Easy to understand, test, and maintain.

#### Demo-Optimized

- Designed for rapid implementation.
- Supports visual progress tracking.
- Provides real-time feedback.
- Includes sample data for demonstration.

### 1.3 Technology Stack

#### Layers

- UI Layer: Streamlit
- Processing Layer: Python agent pipeline
- Persistence Layer: SQLite

#### Components

- Frontend: Streamlit
- Backend: Pure Python functions
- Database: SQLite3
- Text Processing: Regular expressions
- PDF Parsing: pdfplumber (optional; demo uses `.txt` files)

### 1.4 High-Level Stack View

```text
Streamlit UI Layer
  -> Upload, Progress, Results, Dashboard

Agent Processing Layer
  -> Extract -> Gap Match -> Discrepancy -> Decision

Data Persistence Layer
  -> SQLite Database
```

---

## 2. Architecture Design

### 2.1 System Architecture

The system consists of three primary layers:

- Streamlit application layer with Validate, Results, and Dashboard tabs.
- Agent pipeline layer with Extract, Gap Match, Discrepancy, and Decision agents.
- Database layer backed by SQLite for result persistence.

### 2.2 Module Structure

```text
medchart_demo/
|
├── app.py
│   ├── Tab 1: Validate
│   ├── Tab 2: Results
│   └── Tab 3: Dashboard
|
├── agents.py
│   ├── run_extract_agent()
│   ├── run_gap_match_agent()
│   ├── run_discrepancy_agent()
│   └── run_decision_agent()
|
├── db.py
│   ├── init_db()
│   ├── save_result()
│   ├── get_all_results()
│   └── get_summary()
|
└── sample_data/
    ├── gap_report.csv
    ├── chart_MBR001.txt
    ├── chart_MBR002.txt
    └── chart_MBR003.txt
```

### 2.3 Design Patterns

#### Pipeline Pattern

- Sequential execution of agents.
- Each agent transforms data for the next stage.
- Clear separation of concerns.

#### Strategy Pattern

- Different validation strategies per agent.
- Pluggable scoring rules.
- Easy extension for new checks.

#### Repository Pattern

- Data access isolated in `db.py`.
- Clear separation between business logic and persistence.
- Easy migration path from SQLite to PostgreSQL.

---

## 3. Data Flow

### 3.1 High-Level Flow

1. User uploads or selects a chart.
2. Extract Agent converts raw chart text to structured data.
3. Gap Match Agent calculates a composite score and rule-level scores.
4. Discrepancy Agent detects anomalies and generates flags.
5. Decision Agent determines the final outcome.
6. Result is saved to SQLite.
7. UI updates with the result and dashboard metrics.

### 3.2 Data Transformation Stages

#### Stage 1: Raw Text to Structured Data

**Input**

```text
Member ID: MBR001
Visit Date: 2024-09-15
Provider NPI: 1234567890
Diagnosis Codes: Z00.00, Z23
Lab Results: HbA1c: 6.8 on 2024-09-15
```

**Output**

```json
{
  "member_id": "MBR001",
  "visit_date": "2024-09-15",
  "npi": "1234567890",
  "icd_codes": ["Z00.00", "Z23"],
  "all_codes": ["Z00.00", "Z23"],
  "hba1c": 6.8,
  "raw_text": "..."
}
```

#### Stage 2: Structured Data to Scores

**Input**

```json
{
  "required_icd_codes": "Z00.00",
  "window_start": "2024-01-01",
  "window_end": "2024-12-31"
}
```

**Output**

```json
{
  "composite": 1.0,
  "per_rule": {
    "icd_match": 1.0,
    "date_in_window": 1.0,
    "provider_npi": 1.0
  }
}
```

#### Stage 3: Structured Data to Flags

**Output**

```json
[
  {
    "severity": "high",
    "msg": "Lab date 2023-03-10 is 631 days from visit"
  }
]
```

#### Stage 4: Scores and Flags to Final Decision

**Input**

- Gap score: 1.0
- Flags: 1 high-severity flag

**Calculation**

- Base score: 1.0
- Penalty: 1 x 0.20 = 0.20
- Final score: 0.80

**Output**

```json
{
  "decision": "manual_review",
  "score": 0.80,
  "reason": "1 high-severity flag(s) found"
}
```

---

## 4. Agent Design

### 4.1 Extract Agent

**Purpose:** Parse unstructured chart text into structured data.

**Input:** Raw chart text.

**Output:** Dictionary of extracted fields.

#### Algorithm

```python
1. Use regex to find "Member ID: VALUE"
2. Use regex to find "Visit Date: YYYY-MM-DD"
3. Use regex to find "Provider NPI: DIGITS"
4. Use regex to find "Diagnosis Codes: A, B, C"
5. Split codes by comma
6. Validate each code against KNOWN_ICD set
7. Use regex to find "HbA1c: NUMBER"
8. Return structured dictionary
```

#### Design Decisions

- Regex instead of NLP for determinism and speed.
- Known ICD set for local validation.
- Preserve raw text for downstream agents.
- Separate valid codes from all codes to identify unknown values.

#### Error Handling

- Missing fields return `None`.
- Invalid codes are filtered from valid output but preserved in `all_codes`.
- Malformed dates or numbers return `None`.

### 4.2 Gap Match Agent

**Purpose:** Calculate how well the chart closes the care gap.

**Input:**

- Extracted data
- Gap requirement row

**Output:** Composite score and rule-level breakdown.

#### Scoring Rules

| Rule | Weight | Logic | Score |
|---|---:|---|---|
| ICD Match | 0.5 | Any required code present in chart | 1.0 or 0.0 |
| Date in Window | 0.4 | Visit date falls within the allowed window | 1.0 or 0.0 |
| NPI Present | 0.1 | Provider NPI exists | 1.0 or 0.0 |

#### Formula

```text
composite = (R1 x 0.5) + (R2 x 0.4) + (R3 x 0.1)
```

#### Examples

```text
Case 1: All criteria met
R1=1.0, R2=1.0, R3=1.0 -> composite = 1.0

Case 2: ICD mismatch
R1=0.0, R2=1.0, R3=1.0 -> composite = 0.5

Case 3: Date outside window
R1=1.0, R2=0.0, R3=1.0 -> composite = 0.6
```

### 4.3 Discrepancy Agent

**Purpose:** Detect anomalies and data quality issues.

**Input:** Extracted data.

**Output:** List of flags with severity.

#### Checks

| Check | Severity | Condition | Example |
|---|---|---|---|
| HbA1c Range | High | Value greater than 15 or less than 2 | HbA1c: 18.5 |
| Lab Date Gap | High or Medium | Greater than 365 days = high, greater than 180 days = medium | Old lab date |
| Unknown Codes | Low | Code not in `KNOWN_ICD` | Diagnosis: XYZ123 |
| Missing Member ID | High | `member_id` is `None` | Missing field |

#### Flag Structure

```python
{
  "severity": "high" | "medium" | "low",
  "msg": "Human-readable description"
}
```

### 4.4 Decision Agent

**Purpose:** Produce the final routing outcome.

**Input:**

- Gap result
- Flags
- Extracted data

**Output:** Decision, final score, and reason.

#### Decision Flow

1. Calculate penalties:
   - High count x 0.20
   - Medium count x 0.10
   - Low count x 0.03
2. Apply penalties to base score.
3. Evaluate hard overrides in priority order.
4. Apply threshold-based routing.

#### Penalty Weights

- High severity: -0.20
- Medium severity: -0.10
- Low severity: -0.03

#### Thresholds

- Score greater than or equal to 0.85 -> Approved
- Score less than or equal to 0.40 -> Rejected
- Score between 0.41 and 0.84 -> Manual Review

#### Hard Override Priority

1. Missing member ID
2. High-severity flags
3. ICD mismatch

---

## 5. Decision Logic

### 5.1 Decision Tree Summary

The decision tree follows this order:

1. Reject if Member ID is missing.
2. Route to Manual Review if any high-severity flag exists.
3. Reject if ICD match score is zero.
4. Approve if score is at least 0.85.
5. Reject if score is at most 0.40.
6. Otherwise route to Manual Review.

### 5.2 Test Case Analysis

#### Test Case 1: MBR001 (Clean Chart)

**Outcome:** Approved

- Member ID present
- Visit date within allowed window
- ICD code matches requirement
- Provider NPI present
- HbA1c within normal range
- No discrepancy flags
- Final score: 1.0

#### Test Case 2: MBR002 (ICD Mismatch)

**Outcome:** Rejected

- Member ID present
- Visit date within allowed window
- Required ICD code not found
- No discrepancy flags
- Hard override triggered due to ICD mismatch

#### Test Case 3: MBR003 (Date Anomaly)

**Outcome:** Manual Review

- Member ID present
- Visit date within allowed window
- ICD code matches requirement
- High-severity discrepancy due to stale lab date
- Hard override triggered for manual review

---

## 6. Database Schema

### 6.1 Results Table

```sql
CREATE TABLE results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id TEXT NOT NULL,
  filename TEXT NOT NULL,
  decision TEXT NOT NULL,
  confidence REAL NOT NULL,
  gap_score REAL,
  disc_count INTEGER DEFAULT 0,
  flags TEXT,
  reasoning TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 6.2 Field Specifications

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | Primary key, auto-increment | Unique record identifier |
| `member_id` | TEXT | Not null | Patient or member identifier |
| `filename` | TEXT | Not null | Source chart filename |
| `decision` | TEXT | Not null | approved, rejected, or manual_review |
| `confidence` | REAL | Not null | Final score from 0.0 to 1.0 |
| `gap_score` | REAL | Nullable | Composite gap score |
| `disc_count` | INTEGER | Default 0 | Number of discrepancy flags |
| `flags` | TEXT | Nullable | Pipe-separated flag messages |
| `reasoning` | TEXT | Nullable | JSON string of rule scores |
| `created_at` | DATETIME | Default current timestamp | Record creation time |

### 6.3 Sample Data

```sql
INSERT INTO results VALUES (
  1,
  'MBR001',
  'chart_MBR001.txt',
  'approved',
  1.0,
  1.0,
  0,
  '',
  '{"icd_match": 1.0, "date_in_window": 1.0, "provider_npi": 1.0}',
  '2024-12-01 10:30:00'
);

INSERT INTO results VALUES (
  2,
  'MBR002',
  'chart_MBR002.txt',
  'rejected',
  0.5,
  0.5,
  0,
  '',
  '{"icd_match": 0.0, "date_in_window": 1.0, "provider_npi": 1.0}',
  '2024-12-01 10:31:00'
);

INSERT INTO results VALUES (
  3,
  'MBR003',
  'chart_MBR003.txt',
  'manual_review',
  0.8,
  1.0,
  1,
  'Lab date 2023-03-10 is 631 days from visit',
  '{"icd_match": 1.0, "date_in_window": 1.0, "provider_npi": 1.0}',
  '2024-12-01 10:32:00'
);
```

### 6.4 Query Patterns

#### Get all results

```sql
SELECT * FROM results ORDER BY created_at DESC;
```

#### Filter by decision

```sql
SELECT * FROM results WHERE decision = 'manual_review';
```

#### Get summary counts

```sql
SELECT
  COUNT(*) as total,
  SUM(CASE WHEN decision = 'approved' THEN 1 ELSE 0 END) as approved,
  SUM(CASE WHEN decision = 'rejected' THEN 1 ELSE 0 END) as rejected,
  SUM(CASE WHEN decision = 'manual_review' THEN 1 ELSE 0 END) as manual_review
FROM results;
```

#### Get results by date

```sql
SELECT
  DATE(created_at) as date,
  decision,
  COUNT(*) as count
FROM results
GROUP BY DATE(created_at), decision;
```

---

## 7. UI/UX Design

### 7.1 Validate Tab

#### User Flow

1. Select chart source, either uploaded file or sample data.
2. Select gap report source, either upload or bundled CSV.
3. Click **Run Validation**.
4. Watch the agents execute sequentially.
5. Review the final decision banner.
6. Save the result to the database automatically.

#### Design Principles

- Progressive disclosure
- Real-time feedback
- Clear outcome banners
- Minimal-click demo experience

### 7.2 Results Tab

#### Features

- Expandable result rows
- Filter by decision type
- Per-rule score breakdown
- Flag details
- Timestamp visibility

### 7.3 Dashboard Tab

#### Metrics

- Total processed charts
- Approved count and percentage
- Rejected count and percentage
- Manual review count and percentage
- Time-series decision chart

#### Dashboard Note

All decisions are algorithmic and do not use an LLM.

---

## 8. Scoring Algorithm

### 8.1 Mathematical Model

#### Base Score

```text
S_base = sum(w_i x r_i)

where:
  w_i = weight of rule i
  r_i = result of rule i

Rules:
  R1: ICD Match      (w = 0.5)
  R2: Date in Window (w = 0.4)
  R3: Provider NPI   (w = 0.1)
```

#### Penalty Score

```text
P_total = sum(c_s x p_s)

where:
  c_s = count of flags with severity s
  p_s = penalty for severity s

Penalties:
  High   = 0.20
  Medium = 0.10
  Low    = 0.03
```

#### Final Score

```text
S_final = clamp(S_base - P_total, 0.0, 1.0)
```

### 8.2 Score Interpretation

| Score Range | Interpretation | Typical Action |
|---|---|---|
| 0.85 - 1.00 | High confidence | Auto-approve |
| 0.70 - 0.84 | Moderate confidence | Manual review |
| 0.41 - 0.69 | Low confidence | Manual review |
| 0.00 - 0.40 | Very low confidence | Auto-reject |

### 8.3 Sensitivity Analysis

#### Rule Weight Impact

```text
If ICD Match fails:
  Score = 0.5 -> Manual review or rejected by override

If Date in Window fails:
  Score = 0.6 -> Manual review

If NPI fails:
  Score = 0.9 -> Approved
```

#### Penalty Impact

```text
Base score: 1.0

1 high flag:
  Score = 0.80 -> Manual review

2 medium flags:
  Score = 0.80 -> Manual review

7 low flags:
  Score = 0.79 -> Manual review

1 high + 2 medium + 1 low:
  Score = 0.57 -> Manual review
```

---

## 9. Error Handling

### 9.1 Error Categories

#### Input Validation Errors

- File too large
- Invalid file format
- Empty file
- Malformed CSV

#### Parsing Errors

- PDF extraction failure
- Regex match failure
- Date parsing error
- Invalid ICD code format

#### Data Integrity Errors

- Missing member ID
- Missing required fields
- Duplicate records
- Invalid data types

#### System Errors

- Database connection failure
- File I/O error
- Memory overflow
- Unexpected exceptions

### 9.2 Error Handling Strategy

#### Graceful Degradation

```python
try:
    vd = date.fromisoformat(extracted["visit_date"])
    ws = date.fromisoformat(gap_row["window_start"])
    we = date.fromisoformat(gap_row["window_end"])
    date_score = 1.0 if ws <= vd <= we else 0.0
except:
    date_score = 0.0
```

#### User Feedback

```python
if uploaded_file.size > 5_000_000:
    st.error("File too large. Maximum size is 5MB.")
    return
```

#### Logging Strategy

- Log all exceptions to console.
- Show user-friendly error messages.
- Preserve stack traces for debugging.
- Track error rates in production.

### 9.3 Recovery Mechanisms

#### Database Errors

```python
try:
    db.save_result(...)
    st.success("Result saved to database")
except Exception as e:
    st.error(f"Failed to save result: {str(e)}")
```

#### Agent Failures

```python
with st.status("Extract Agent") as status:
    try:
        extracted = agents.run_extract_agent(chart_text)
        st.json(extracted)
        status.update(label="Extract Agent completed", state="complete")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        status.update(label="Extract Agent failed", state="error")
        st.stop()
```

---

## 10. Security Considerations

### 10.1 Data Privacy

#### PHI Protection

- No external API calls.
- Data remains local.
- SQLite is file-based with no network dependency.
- Sensitive data is not logged.
- Sample data uses synthetic identifiers.

#### Access Control

- Single-user demo without authentication.
- File system permissions control database access.
- Streamlit runs on localhost by default.

### 10.2 Input Validation

#### File Upload Restrictions

```python
if uploaded_file.size > 5_000_000:
    st.error("File too large")

if not uploaded_file.name.endswith((".txt", ".pdf")):
    st.error("Invalid file type")
```