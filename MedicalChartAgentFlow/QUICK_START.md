# 🚀 Quick Start Guide - Medical Chart Validation Demo

## ⏱️ Time Required: 2 hours

Follow these steps in order. Each block builds on the previous one.

---

## 📋 Prerequisites

- **Python 3.8+ installed** (tested with 3.11, 3.12)
- Terminal/Command Prompt access
- Text editor or IDE (VS Code recommended)

### ✅ Python 3.11 Compatibility
All dependencies are fully compatible with Python 3.11:
- ✅ Streamlit 1.28+ supports Python 3.8-3.12
- ✅ pdfplumber 0.10+ supports Python 3.8-3.12
- ✅ pandas 2.0+ supports Python 3.9-3.12
- ✅ sqlite3 is built-in (all Python versions)

---

## 🎯 Step-by-Step Implementation

### **STEP 1: Project Setup (5 minutes)**

```bash
# Navigate to your workspace
cd c:/Ramesh_Learning/Agentic_AI_Demo_Challenge

# Create project directory
mkdir medchart_demo
cd medchart_demo

# Create sample data directory
mkdir sample_data

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

---

### **STEP 2: Install Dependencies (2 minutes)**

Create `requirements.txt`:
```txt
streamlit>=1.28.0
pdfplumber>=0.10.0
pandas>=2.0.0
```

Install packages:
```bash
pip install -r requirements.txt
```

---

### **STEP 3: Create Database Layer (10 minutes)**

Create `db.py` - Copy the complete code from [`IMPLEMENTATION_GUIDE.md`](IMPLEMENTATION_GUIDE.md) Block 1, File 1.

**Test it:**
```bash
python -c "import db; db.init_db()"
```

Expected output: `✅ Database initialized`

---

### **STEP 4: Create Agent Logic (15 minutes)**

Create `agents.py` - Copy the complete code from [`IMPLEMENTATION_GUIDE.md`](IMPLEMENTATION_GUIDE.md) Block 1, File 2.

**Key fix applied**: Line 162 uses `split(",")` instead of `split("|")`

**Test it:**
```bash
python -c "import agents; print(agents.KNOWN_ICD)"
```

Expected output: `{'Z00.00', 'Z12.31', 'E11.9', 'Z23', 'Z79.4', 'Z13.1', 'E11.65'}`

---

### **STEP 5: Create Sample Data (5 minutes)**

Create these 4 files in `sample_data/` directory:

1. **`sample_data/gap_report.csv`**
```csv
member_id,gap_id,gap_description,required_icd_codes,window_start,window_end
MBR001,G1,Annual wellness visit,Z00.00,2024-01-01,2024-12-31
MBR002,G2,Breast cancer screening,Z12.31,2024-01-01,2024-12-31
MBR003,G3,Diabetes HbA1c check,E11.9,2024-07-01,2024-12-31
```

2. **`sample_data/chart_MBR001.txt`**
```
Member ID: MBR001
Visit Date: 2024-09-15
Provider NPI: 1234567890
Diagnosis Codes: Z00.00, Z23
Medications: Lisinopril 10mg daily
Lab Results: HbA1c: 6.8 on 2024-09-15, BP: 118/76
Notes: Annual wellness completed. Preventive care up to date.
```

3. **`sample_data/chart_MBR002.txt`**
```
Member ID: MBR002
Visit Date: 2024-11-20
Provider NPI: 9876543210
Diagnosis Codes: E11.9, Z79.4
Medications: Metformin 500mg twice daily
Lab Results: HbA1c: 7.9 on 2024-11-20
Notes: Diabetes management follow-up. No screening performed.
```

4. **`sample_data/chart_MBR003.txt`**
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

### **STEP 6: Create Streamlit App - Tab 1 (40 minutes)**

Create `app.py` - Copy the complete code from [`IMPLEMENTATION_GUIDE.md`](IMPLEMENTATION_GUIDE.md) Block 2.

This includes:
- Database initialization
- Tab 1: Validate (complete)
- Tab 2: Results (placeholder)
- Tab 3: Dashboard (placeholder)

**Test it:**
```bash
streamlit run app.py
```

**Expected behavior:**
- Browser opens at http://localhost:8501
- You see 3 tabs
- Tab 1 has upload interface
- Select "chart_MBR001.txt" from sample dropdown
- Click "Run Validation"
- See 4 agent status blocks execute
- Final result: ✅ APPROVED (Confidence: 100%)

---

### **STEP 7: Complete Tabs 2 & 3 (25 minutes)**

Update `app.py` - Replace the placeholder Tab 2 and Tab 3 sections with the complete code from [`IMPLEMENTATION_GUIDE.md`](IMPLEMENTATION_GUIDE.md) Block 3.

**Test it:**
```bash
streamlit run app.py
```

**Test workflow:**
1. Go to Tab 1
2. Validate all 3 samples one by one:
   - chart_MBR001.txt → Should show ✅ APPROVED
   - chart_MBR002.txt → Should show ❌ REJECTED
   - chart_MBR003.txt → Should show ⚠️ MANUAL REVIEW
3. Go to Tab 2 → Should show all 3 results in table
4. Go to Tab 3 → Should show metrics: Total=3, Approved=1, Rejected=1, Manual Review=1

---

### **STEP 8: Final Testing (10 minutes)**

Run through this checklist:

- [ ] **MBR001 validation**
  - Result: APPROVED
  - Confidence: ~100%
  - Reason: All criteria met

- [ ] **MBR002 validation**
  - Result: REJECTED
  - Reason: "Required diagnosis code not in chart"
  - ICD mismatch: Chart has E11.9, gap requires Z12.31

- [ ] **MBR003 validation**
  - Result: MANUAL REVIEW
  - Reason: "1 high-severity flag(s) found"
  - Flag: Lab date 2023-03-10 is 631 days from visit

- [ ] **Database persistence**
  - Close app (Ctrl+C)
  - Restart: `streamlit run app.py`
  - Go to Tab 2 → Results should still be there

- [ ] **Dashboard metrics**
  - Total Processed: 3
  - Approved: 1 (33%)
  - Rejected: 1 (33%)
  - Manual Review: 1 (33%)

---

### **STEP 9: Practice Demo (5 minutes)**

Follow this script:

1. **Open Tab 3** - "This is our dashboard. Currently shows 3 processed charts."

2. **Go to Tab 1** - "Let me show you how validation works."
   - Select chart_MBR001.txt
   - Click "Run Validation"
   - "Watch the 4 agents execute. Each is a pure Python function, no LLM."
   - Result appears: APPROVED

3. **Back to Tab 3** - "Dashboard updates in real-time."

4. **Go to Tab 2** - "Here's our results table."
   - Expand MBR003 row
   - "You can see exactly why it was routed to manual review."

5. **Closing** - "Every decision is 100% auditable. No black box."

---

## 📁 Final File Structure

```
medchart_demo/
├── app.py                      # Streamlit UI (all 3 tabs)
├── agents.py                   # 4 agent functions
├── db.py                       # Database layer
├── requirements.txt            # Dependencies
├── medchart.db                 # SQLite database (auto-created)
└── sample_data/
    ├── gap_report.csv          # Gap requirements
    ├── chart_MBR001.txt        # Test case 1 (approved)
    ├── chart_MBR002.txt        # Test case 2 (rejected)
    └── chart_MBR003.txt        # Test case 3 (manual review)
```

---

## ✅ Success Checklist

Before considering the demo complete, verify:

- [ ] All 3 sample charts validate correctly
- [ ] MBR001 → APPROVED (score 1.0)
- [ ] MBR002 → REJECTED (ICD mismatch)
- [ ] MBR003 → MANUAL REVIEW (date flag)
- [ ] Dashboard shows correct metrics (3 total, 1 each category)
- [ ] Results persist after app restart
- [ ] Can complete demo walkthrough in under 5 minutes
- [ ] All agent status blocks show green checkmarks
- [ ] No errors in terminal/console

---

## 🐛 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'db'"
**Solution**: Make sure you're in the `medchart_demo` directory when running `streamlit run app.py`

### Issue: "FileNotFoundError: sample_data/gap_report.csv"
**Solution**: Verify the `sample_data/` folder exists and contains all 4 files

### Issue: "Database is locked"
**Solution**: 
```bash
# Close all Python processes
# Delete the database
rm medchart.db  # Mac/Linux
del medchart.db  # Windows
# Reinitialize
python -c "import db; db.init_db()"
```

### Issue: "Port 8501 is already in use"
**Solution**: 
```bash
streamlit run app.py --server.port 8502
```

### Issue: MBR002 shows "MANUAL REVIEW" instead of "REJECTED"
**Solution**: This is actually correct! The hard override at line 241 in agents.py catches the ICD mismatch and forces REJECTED. If you're seeing MANUAL REVIEW, check that the ICD code matching logic is working correctly.

---

## 🎯 What You've Built

- ✅ **4-agent validation pipeline** (Extract → Gap Match → Discrepancy → Decision)
- ✅ **Zero-LLM decision engine** (100% algorithmic, fully auditable)
- ✅ **3-tab Streamlit UI** (Validate, Results, Dashboard)
- ✅ **SQLite persistence** (Results saved across sessions)
- ✅ **3 test cases** (Covering all decision paths)
- ✅ **Real-time progress tracking** (Status blocks for each agent)
- ✅ **Comprehensive metrics** (Dashboard with charts)

**Total time**: ~2 hours  
**Total code**: ~430 lines  
**Dependencies**: 3 packages  
**LLM usage**: 0  

---

## 🚀 Next Steps

**For Demo:**
- Practice the 5-minute walkthrough
- Prepare to explain the "Why no LLM?" question
- Have the dashboard open before starting

**For Production:**
- Add real PDF parsing (pdfplumber already installed)
- Implement FastAPI backend for multi-user support
- Add authentication/authorization
- Expand ICD-10 code validation set
- Add NPI Luhn validation
- Implement reviewer override functionality
- Add CSV export for results

---

## 📚 Reference Documents

- [`draft.md`](draft.md) - Original plan with detailed specifications
- [`IMPLEMENTATION_GUIDE.md`](IMPLEMENTATION_GUIDE.md) - Complete code and detailed explanations

---

**Ready to start? Begin with STEP 1!** 🎉