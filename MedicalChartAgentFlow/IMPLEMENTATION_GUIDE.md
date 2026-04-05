# Medical Chart Validation - Implementation Guide

## 🎯 Overview
Build a working medical chart validation demo in 2 hours using Streamlit, SQLite, and pure Python (no LLM).

**Python Version**: 3.8+ (tested with 3.11, 3.12)
**Timeline**: 4 blocks × 30 minutes = 2 hours
**Files to create**: 4 Python files + 4 sample data files
**Dependencies**: 3 packages (streamlit, pdfplumber, pandas)

---

## 📋 Pre-Implementation Setup (5 minutes)

### Step 1: Create Project Structure
```bash
cd c:/Ramesh_Learning/Agentic_AI_Demo_Challenge
mkdir medchart_demo
cd medchart_demo
mkdir sample_data
```

### Step 2: Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 3: Create requirements.txt
```bash
# Create file: medchart_demo/requirements.txt
```

**Content**:
```txt
streamlit>=1.28.0
pdfplumber>=0.10.0
pandas>=2.0.0
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔧 Block 1: Core Logic (30 minutes)

### File 1: `db.py` (Database Layer)

**Create**: `medchart_demo/db.py`

```python
import sqlite3
import json
from datetime import datetime

DB_PATH = "medchart.db"

def init_db():
    """Initialize database with results table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id   TEXT NOT NULL,
            filename    TEXT NOT NULL,
            decision    TEXT NOT NULL,
            confidence  REAL NOT NULL,
            gap_score   REAL,
            disc_count  INTEGER DEFAULT 0,
            flags       TEXT,
            reasoning   TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def save_result(member_id, filename, decision, confidence, gap_score, disc_count, flags_list, reasoning_dict):
    """Save validation result to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    flags_str = " | ".join([f["msg"] for f in flags_list]) if flags_list else ""
    reasoning_str = json.dumps(reasoning_dict)
    
    cursor.execute("""
        INSERT INTO results (member_id, filename, decision, confidence, gap_score, disc_count, flags, reasoning)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (member_id, filename, decision, confidence, gap_score, disc_count, flags_str, reasoning_str))
    
    conn.commit()
    conn.close()

def get_all_results():
    """Fetch all results as list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM results ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_summary():
    """Get summary counts by decision type."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM results")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM results WHERE decision = 'approved'")
    approved = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM results WHERE decision = 'rejected'")
    rejected = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM results WHERE decision = 'manual_review'")
    manual_review = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "manual_review": manual_review
    }
```

**Test**:
```bash
python -c "import db; db.init_db()"
# Should see: ✅ Database initialized
```

---

### File 2: `agents.py` (Agent Logic)

**Create**: `medchart_demo/agents.py`

```python
import re
from datetime import date

# Known ICD-10 codes for validation
KNOWN_ICD = {"Z00.00", "Z12.31", "E11.9", "Z23", "Z79.4", "Z13.1", "E11.65"}

def run_extract_agent(text: str) -> dict:
    """Extract structured data from chart text using regex."""
    member_id = re.search(r"Member ID:\s*(\S+)", text)
    visit_date = re.search(r"Visit Date:\s*([\d-]+)", text)
    npi = re.search(r"Provider NPI:\s*(\d+)", text)
    icd_line = re.search(r"Diagnosis Codes:\s*(.+)", text)
    
    # Extract all codes and validate against known set
    raw_codes = [c.strip() for c in icd_line.group(1).split(",")] if icd_line else []
    valid_codes = [c for c in raw_codes if c in KNOWN_ICD]
    
    # Extract HbA1c value
    hba1c = re.search(r"HbA1c:\s*([\d.]+)", text)
    
    return {
        "member_id": member_id.group(1) if member_id else None,
        "visit_date": visit_date.group(1) if visit_date else None,
        "npi": npi.group(1) if npi else None,
        "icd_codes": valid_codes,
        "all_codes": raw_codes,
        "hba1c": float(hba1c.group(1)) if hba1c else None,
        "raw_text": text
    }

def run_gap_match_agent(extracted: dict, gap_row: dict) -> dict:
    """Calculate gap closure score based on chart data."""
    scores = {}
    
    # R1: ICD code match (weight 0.5)
    # FIXED: Changed from split("|") to split(",")
    required = [c.strip() for c in gap_row["required_icd_codes"].split(",")]
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
    
    # Calculate composite score
    composite = scores["icd_match"] * 0.5 + scores["date_in_window"] * 0.4 + scores["provider_npi"] * 0.1
    
    return {
        "composite": round(composite, 2),
        "per_rule": scores
    }

def run_discrepancy_agent(extracted: dict) -> list:
    """Detect discrepancies and anomalies in chart data."""
    flags = []
    
    # D1: HbA1c physiologically impossible
    if extracted.get("hba1c") and (extracted["hba1c"] > 15 or extracted["hba1c"] < 2):
        flags.append({
            "severity": "high",
            "msg": f"HbA1c={extracted['hba1c']} is outside physiological range"
        })
    
    # D2: Lab date vs visit date gap
    lab_dates = re.findall(r"HbA1c:.*?on\s*([\d-]+)", extracted.get("raw_text", ""))
    if lab_dates and extracted.get("visit_date"):
        try:
            vd = date.fromisoformat(extracted["visit_date"])
            ld = date.fromisoformat(lab_dates[0])
            gap_days = abs((vd - ld).days)
            if gap_days > 365:
                flags.append({
                    "severity": "high",
                    "msg": f"Lab date {lab_dates[0]} is {gap_days} days from visit"
                })
            elif gap_days > 180:
                flags.append({
                    "severity": "medium",
                    "msg": f"Lab date {lab_dates[0]} is {gap_days} days from visit"
                })
        except:
            pass
    
    # D3: Unknown ICD codes (potential typos)
    unknown = [c for c in extracted.get("all_codes", []) if c not in extracted.get("icd_codes", [])]
    if unknown:
        flags.append({
            "severity": "low",
            "msg": f"Unrecognized codes: {', '.join(unknown)}"
        })
    
    # D4: Missing member ID
    if not extracted.get("member_id"):
        flags.append({
            "severity": "high",
            "msg": "Member ID not found in chart"
        })
    
    return flags

def run_decision_agent(gap_result: dict, flags: list, extracted: dict) -> dict:
    """Make final routing decision based on score and flags."""
    base = gap_result["composite"]
    
    # Calculate penalties
    high = sum(1 for f in flags if f["severity"] == "high")
    medium = sum(1 for f in flags if f["severity"] == "medium")
    low = sum(1 for f in flags if f["severity"] == "low")
    penalty = (high * 0.20) + (medium * 0.10) + (low * 0.03)
    
    score = round(max(0.0, min(1.0, base - penalty)), 2)
    
    # Hard override rules (checked in order)
    if not extracted.get("member_id"):
        return {
            "decision": "rejected",
            "score": score,
            "reason": "Missing member ID (hard reject)"
        }
    
    if high > 0:
        return {
            "decision": "manual_review",
            "score": score,
            "reason": f"{high} high-severity flag(s) found"
        }
    
    if gap_result["per_rule"]["icd_match"] == 0.0:
        return {
            "decision": "rejected",
            "score": score,
            "reason": "Required diagnosis code not in chart"
        }
    
    # Threshold-based routing
    if score >= 0.85:
        decision = "approved"
    elif score <= 0.40:
        decision = "rejected"
    else:
        decision = "manual_review"
    
    return {
        "decision": decision,
        "score": score,
        "reason": f"Score {score} (base {base} - penalty {round(penalty, 2)})"
    }
```

**Test**:
```bash
python -c "import agents; print(agents.KNOWN_ICD)"
# Should see: {'Z00.00', 'Z12.31', 'E11.9', ...}
```

---

### File 3-6: Sample Data Files

**Create**: `medchart_demo/sample_data/gap_report.csv`
```csv
member_id,gap_id,gap_description,required_icd_codes,window_start,window_end
MBR001,G1,Annual wellness visit,Z00.00,2024-01-01,2024-12-31
MBR002,G2,Breast cancer screening,Z12.31,2024-01-01,2024-12-31
MBR003,G3,Diabetes HbA1c check,E11.9,2024-07-01,2024-12-31
```

**Create**: `medchart_demo/sample_data/chart_MBR001.txt`
```
Member ID: MBR001
Visit Date: 2024-09-15
Provider NPI: 1234567890
Diagnosis Codes: Z00.00, Z23
Medications: Lisinopril 10mg daily
Lab Results: HbA1c: 6.8 on 2024-09-15, BP: 118/76
Notes: Annual wellness completed. Preventive care up to date.
```

**Create**: `medchart_demo/sample_data/chart_MBR002.txt`
```
Member ID: MBR002
Visit Date: 2024-11-20
Provider NPI: 9876543210
Diagnosis Codes: E11.9, Z79.4
Medications: Metformin 500mg twice daily
Lab Results: HbA1c: 7.9 on 2024-11-20
Notes: Diabetes management follow-up. No screening performed.
```

**Create**: `medchart_demo/sample_data/chart_MBR003.txt`
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

## 🎨 Block 2: Streamlit UI - Tab 1 (45 minutes)

### File 7: `app.py` (Streamlit Application)

**Create**: `medchart_demo/app.py`

```python
import streamlit as st
import pandas as pd
import pdfplumber
from pathlib import Path
import db
import agents

# Initialize database on startup
db.init_db()

# Page config
st.set_page_config(
    page_title="Medical Chart Validation",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Medical Chart Validation System")
st.caption("Zero-LLM algorithmic decision engine for care gap closure")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📋 Validate", "📊 Results", "📈 Dashboard"])

# ============================================================================
# TAB 1: VALIDATE
# ============================================================================
with tab1:
    st.header("Validate Medical Chart")
    
    col1, col2 = st.columns(2)
    
    # Left column: Chart upload
    with col1:
        st.subheader("📄 Medical Chart")
        
        upload_method = st.radio(
            "Choose input method:",
            ["Upload file", "Use sample data"],
            horizontal=True
        )
        
        chart_text = None
        filename = None
        
        if upload_method == "Upload file":
            uploaded_file = st.file_uploader(
                "Upload chart file",
                type=["txt", "pdf"],
                help="Accepts .txt or .pdf files (max 5MB)"
            )
            
            if uploaded_file:
                # Check file size
                if uploaded_file.size > 5_000_000:
                    st.error("❌ File too large. Maximum size is 5MB.")
                else:
                    filename = uploaded_file.name
                    
                    if uploaded_file.name.endswith(".pdf"):
                        try:
                            with pdfplumber.open(uploaded_file) as pdf:
                                chart_text = "\n".join([page.extract_text() for page in pdf.pages])
                            st.success(f"✅ PDF loaded: {len(chart_text)} characters")
                        except Exception as e:
                            st.error(f"❌ PDF extraction failed: {str(e)}")
                    else:
                        chart_text = uploaded_file.read().decode("utf-8")
                        st.success(f"✅ Text file loaded: {len(chart_text)} characters")
        
        else:  # Use sample data
            sample_options = [
                "chart_MBR001.txt",
                "chart_MBR002.txt",
                "chart_MBR003.txt"
            ]
            selected_sample = st.selectbox("Select sample chart:", sample_options)
            
            sample_path = Path("sample_data") / selected_sample
            if sample_path.exists():
                chart_text = sample_path.read_text()
                filename = selected_sample
                st.success(f"✅ Sample loaded: {selected_sample}")
            else:
                st.error(f"❌ Sample file not found: {sample_path}")
    
    # Right column: Gap report
    with col2:
        st.subheader("📋 Gap Report")
        
        use_bundled = st.checkbox("Use bundled gap_report.csv", value=True)
        
        gap_df = None
        
        if use_bundled:
            gap_path = Path("sample_data/gap_report.csv")
            if gap_path.exists():
                gap_df = pd.read_csv(gap_path)
                st.success("✅ Bundled gap report loaded")
                st.dataframe(gap_df, use_container_width=True)
            else:
                st.error("❌ Bundled gap report not found")
        else:
            gap_file = st.file_uploader("Upload gap report CSV", type=["csv"])
            if gap_file:
                gap_df = pd.read_csv(gap_file)
                st.success("✅ Gap report uploaded")
                st.dataframe(gap_df, use_container_width=True)
    
    # Validation button
    st.divider()
    
    if st.button("🚀 Run Validation", type="primary", use_container_width=True):
        if not chart_text:
            st.error("❌ Please provide a chart file")
        elif gap_df is None or gap_df.empty:
            st.error("❌ Please provide a gap report")
        else:
            # Run validation pipeline
            st.subheader("🔄 Agent Pipeline")
            
            # Agent 1: Extract
            with st.status("🔍 Extract Agent", expanded=True) as status1:
                try:
                    extracted = agents.run_extract_agent(chart_text)
                    st.json(extracted)
                    status1.update(label="✅ Extract Agent", state="complete")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    status1.update(label="❌ Extract Agent", state="error")
                    st.stop()
            
            # Match member to gap report
            member_id = extracted.get("member_id")
            gap_row = None
            
            if member_id:
                matching_gaps = gap_df[gap_df["member_id"] == member_id]
                if not matching_gaps.empty:
                    gap_row = matching_gaps.iloc[0].to_dict()
                else:
                    st.warning(f"⚠️ Member {member_id} not found in gap report. Using first gap as fallback.")
                    gap_row = gap_df.iloc[0].to_dict()
            else:
                st.warning("⚠️ Member ID not extracted. Using first gap as fallback.")
                gap_row = gap_df.iloc[0].to_dict()
            
            # Agent 2: Gap Match
            with st.status("🎯 Gap Match Agent", expanded=True) as status2:
                try:
                    gap_result = agents.run_gap_match_agent(extracted, gap_row)
                    st.json(gap_result)
                    status2.update(label="✅ Gap Match Agent", state="complete")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    status2.update(label="❌ Gap Match Agent", state="error")
                    st.stop()
            
            # Agent 3: Discrepancy
            with st.status("🔎 Discrepancy Agent", expanded=True) as status3:
                try:
                    flags = agents.run_discrepancy_agent(extracted)
                    if flags:
                        st.json(flags)
                    else:
                        st.info("No discrepancies found")
                    status3.update(label="✅ Discrepancy Agent", state="complete")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    status3.update(label="❌ Discrepancy Agent", state="error")
                    st.stop()
            
            # Agent 4: Decision
            with st.status("⚖️ Decision Agent", expanded=True) as status4:
                try:
                    decision_result = agents.run_decision_agent(gap_result, flags, extracted)
                    st.json(decision_result)
                    status4.update(label="✅ Decision Agent", state="complete")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    status4.update(label="❌ Decision Agent", state="error")
                    st.stop()
            
            # Display final result
            st.divider()
            decision = decision_result["decision"]
            score = decision_result["score"]
            reason = decision_result["reason"]
            
            if decision == "approved":
                st.success(f"✅ **APPROVED** — Confidence: {score*100:.0f}%")
                st.info(f"Reason: {reason}")
            elif decision == "rejected":
                st.error(f"❌ **REJECTED** — Score: {score*100:.0f}%")
                st.info(f"Reason: {reason}")
            else:  # manual_review
                st.warning(f"⚠️ **MANUAL REVIEW REQUIRED** — Score: {score*100:.0f}%")
                st.info(f"Reason: {reason}")
            
            # Save to database
            try:
                db.save_result(
                    member_id=extracted.get("member_id", "UNKNOWN"),
                    filename=filename,
                    decision=decision,
                    confidence=score,
                    gap_score=gap_result["composite"],
                    disc_count=len(flags),
                    flags_list=flags,
                    reasoning_dict=gap_result["per_rule"]
                )
                st.success("💾 Result saved to database")
            except Exception as e:
                st.error(f"❌ Failed to save result: {str(e)}")

# ============================================================================
# TAB 2: RESULTS (Placeholder for Block 3)
# ============================================================================
with tab2:
    st.header("📊 Validation Results")
    st.info("🚧 This tab will be implemented in Block 3")

# ============================================================================
# TAB 3: DASHBOARD (Placeholder for Block 3)
# ============================================================================
with tab3:
    st.header("📈 Dashboard")
    st.info("🚧 This tab will be implemented in Block 3")
```

**Test**:
```bash
streamlit run app.py
```

Expected behavior:
- App opens in browser
- Tab 1 shows upload interface
- Select "chart_MBR001.txt" sample
- Click "Run Validation"
- Should see 4 agent status blocks execute
- Final result: ✅ APPROVED

---

## 📊 Block 3: Results & Dashboard (30 minutes)

### Update `app.py` - Add Tab 2 & Tab 3

Replace the placeholder Tab 2 and Tab 3 sections with:

```python
# ============================================================================
# TAB 2: RESULTS
# ============================================================================
with tab2:
    st.header("📊 Validation Results")
    
    # Fetch all results
    results = db.get_all_results()
    
    if not results:
        st.info("No validation results yet. Run a validation in Tab 1 to see results here.")
    else:
        # Filter controls
        col1, col2 = st.columns([1, 3])
        
        with col1:
            filter_decision = st.selectbox(
                "Filter by decision:",
                ["All", "approved", "rejected", "manual_review"]
            )
        
        # Apply filter
        if filter_decision != "All":
            filtered_results = [r for r in results if r["decision"] == filter_decision]
        else:
            filtered_results = results
        
        st.caption(f"Showing {len(filtered_results)} of {len(results)} results")
        
        # Display results
        for result in filtered_results:
            # Decision emoji
            if result["decision"] == "approved":
                emoji = "✅"
            elif result["decision"] == "rejected":
                emoji = "❌"
            else:
                emoji = "⚠️"
            
            # Create expander for each result
            with st.expander(
                f"{emoji} {result['member_id']} — {result['decision'].upper()} ({result['confidence']*100:.0f}%) — {result['created_at']}"
            ):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Confidence", f"{result['confidence']*100:.0f}%")
                    st.metric("Gap Score", f"{result['gap_score']:.2f}" if result['gap_score'] else "N/A")
                
                with col2:
                    st.metric("Flags", result['disc_count'])
                    st.metric("Filename", result['filename'])
                
                with col3:
                    st.metric("Decision", result['decision'])
                    st.metric("Created", result['created_at'][:10])
                
                # Show detailed scores
                if result['reasoning']:
                    st.subheader("Per-Rule Scores")
                    import json
                    reasoning = json.loads(result['reasoning'])
                    st.json(reasoning)
                
                # Show flags
                if result['flags']:
                    st.subheader("Flags")
                    st.warning(result['flags'])

# ============================================================================
# TAB 3: DASHBOARD
# ============================================================================
with tab3:
    st.header("📈 Dashboard")
    
    # Get summary
    summary = db.get_summary()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Processed",
            summary["total"],
            help="Total number of charts validated"
        )
    
    with col2:
        st.metric(
            "✅ Approved",
            summary["approved"],
            delta=f"{summary['approved']/summary['total']*100:.0f}%" if summary['total'] > 0 else "0%",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "❌ Rejected",
            summary["rejected"],
            delta=f"{summary['rejected']/summary['total']*100:.0f}%" if summary['total'] > 0 else "0%",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "⚠️ Manual Review",
            summary["manual_review"],
            delta=f"{summary['manual_review']/summary['total']*100:.0f}%" if summary['total'] > 0 else "0%",
            delta_color="off"
        )
    
    st.divider()
    
    # Get all results for charting
    results = db.get_all_results()
    
    if results:
        # Convert to DataFrame
        df = pd.DataFrame(results)
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        
        # Group by date and decision
        chart_data = df.groupby(['date', 'decision']).size().unstack(fill_value=0)
        
        st.subheader("Decisions Over Time")
        st.bar_chart(chart_data)
        
        # Decision distribution pie chart
        st.subheader("Decision Distribution")
        decision_counts = df['decision'].value_counts()
        st.bar_chart(decision_counts)
    else:
        st.info("No data to display yet. Run validations in Tab 1 to see charts here.")
    
    st.divider()
    st.caption("💡 All decisions are algorithmic — zero LLM used for routing.")
```

**Test**:
```bash
streamlit run app.py
```

Test workflow:
1. Go to Tab 1, validate all 3 samples (MBR001, MBR002, MBR003)
2. Go to Tab 2, verify all 3 results appear
3. Go to Tab 3, verify metrics show: Total=3, Approved=1, Rejected=1, Manual Review=1

---

## ✨ Block 4: Polish & Final Testing (15 minutes)

### Checklist

- [ ] **Test all 3 sample charts**
  - MBR001 → Should be APPROVED (score ~1.0)
  - MBR002 → Should be REJECTED (ICD mismatch)
  - MBR003 → Should be MANUAL REVIEW (date flag)

- [ ] **Verify database persistence**
  - Close and reopen app
  - Results should still be visible in Tab 2 & Tab 3

- [ ] **Test error handling**
  - Try uploading a large file (>5MB) - should show error
  - Try running validation without selecting a chart - should show error

- [ ] **UI polish**
  - Check all emojis render correctly
  - Verify all status blocks show green checkmarks
  - Ensure metrics display properly

- [ ] **Practice demo walkthrough** (5 minutes)
  1. Open Tab 3 (empty state)
  2. Go to Tab 1, validate MBR001
  3. Show Tab 3 updates
  4. Validate MBR002 and MBR003
  5. Show Tab 2 results table
  6. Expand a row to show details

---

## 🎬 Demo Script (5 minutes)

### Opening (30 seconds)
"This is a medical chart validation system that routes charts to approved, rejected, or manual review. The key differentiator: zero LLM. Every decision is 100% auditable."

### Walkthrough (4 minutes)

1. **Tab 3 - Dashboard** (30 sec)
   - "Here's our dashboard. Currently empty because we haven't processed any charts yet."

2. **Tab 1 - Validate MBR001** (1 min)
   - Select chart_MBR001.txt
   - Click "Run Validation"
   - "Watch the 4 agents execute in sequence. Each is a pure Python function."
   - Result: APPROVED
   - "Jump back to Tab 3..."
   - Dashboard now shows: Total=1, Approved=1

3. **Validate MBR002** (1 min)
   - Select chart_MBR002.txt
   - Click "Run Validation"
   - Result: REJECTED (diagnosis mismatch)
   - Dashboard updates: Total=2, Approved=1, Rejected=1

4. **Validate MBR003** (1 min)
   - Select chart_MBR003.txt
   - Click "Run Validation"
   - Result: MANUAL REVIEW (date anomaly)
   - Dashboard updates: Total=3, Approved=1, Rejected=1, Manual Review=1

5. **Tab 2 - Results** (30 sec)
   - Show results table
   - Expand MBR003 row
   - "Here's the score breakdown. You can see exactly why it was routed to manual review."

### Closing (30 seconds)
"In production, this processes a chart in under 10 seconds. Today we validated 3 charts in 2 minutes. Every decision is explainable, auditable, and deterministic. No black box."

---

## 🚀 Quick Start Commands

```bash
# Setup
cd c:/Ramesh_Learning/Agentic_AI_Demo_Challenge
mkdir medchart_demo
cd medchart_demo
mkdir sample_data

# Install
pip install streamlit>=1.28.0 pdfplumber>=0.10.0 pandas>=2.0.0

# Create files (use content from sections above)
# - db.py
# - agents.py
# - app.py
# - requirements.txt
# - sample_data/gap_report.csv
# - sample_data/chart_MBR001.txt
# - sample_data/chart_MBR002.txt
# - sample_data/chart_MBR003.txt

# Initialize database
python -c "import db; db.init_db()"

# Run app
streamlit run app.py
```

---

## 🐛 Troubleshooting

### Issue: "Module not found: db"
**Solution**: Make sure you're running `streamlit run app.py` from the `medchart_demo` directory.

### Issue: "Sample file not found"
**Solution**: Verify `sample_data/` folder exists and contains all 4 files.

### Issue: Database locked
**Solution**: Close all Python processes and delete `medchart.db`, then run `db.init_db()` again.

### Issue: Streamlit won't start
**Solution**: Check if port 8501 is already in use. Try: `streamlit run app.py --server.port 8502`

---

## 📦 Deliverables

After completing all blocks, you should have:

✅ 4 Python files (db.py, agents.py, app.py, requirements.txt)  
✅ 4 sample data files (1 CSV + 3 TXT)  
✅ Working Streamlit app with 3 tabs  
✅ SQLite database with results table  
✅ 3 validated test cases in database  
✅ 5-minute demo script ready  

**Total time**: ~2 hours  
**Total lines of code**: ~430 lines  
**Dependencies**: 3 packages  
**LLM usage**: 0  

---

## 🎯 Success Criteria

- [ ] All 3 sample charts validate correctly
- [ ] MBR001 → APPROVED (score ~1.0)
- [ ] MBR002 → REJECTED (ICD mismatch)
- [ ] MBR003 → MANUAL REVIEW (date flag)
- [ ] Dashboard shows correct metrics
- [ ] Results persist after app restart
- [ ] Demo completes in under 5 minutes

---

## 📚 Next Steps (Post-Demo)

If stakeholders want to expand:

1. **Real PDF parsing** (+2 hours) - Handle actual hospital PDFs
2. **FastAPI backend** (+3 days) - Multi-user web app
3. **NPI validation** (+1 hour) - Luhn algorithm check
4. **Reviewer override** (+2 hours) - Allow manual decision changes
5. **CSV export** (+30 min) - Download results table
6. **Authentication** (+1 day) - Login system

---

**Ready to implement? Start with Block 1!** 🚀