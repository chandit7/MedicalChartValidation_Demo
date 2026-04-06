# 🏥 Medical Chart Validation System

A zero-LLM algorithmic decision engine for medical chart validation and care gap closure.

## 🎯 Overview

This system validates medical charts against care gap requirements using a deterministic, rule-based approach. Every decision is 100% auditable and explainable - no AI/ML black boxes.

## ✨ Features

- **4-Agent Pipeline**: Extract → Gap Match → Discrepancy → Decision
- **3 Decision Types**: Approved, Rejected, Manual Review
- **Real-time Dashboard**: Track validation metrics and trends
- **SQLite Database**: Persistent storage of all validation results
- **PDF Support**: Extract text from PDF and TXT files
- **Zero-LLM Core**: All decisions are deterministic and auditable

## 📊 System Architecture

```
User → Streamlit UI → 4 Agents → Decision → Database → Dashboard
```

### Agent Pipeline

1. **Extract Agent**: Parse chart data using regex
2. **Gap Match Agent**: Calculate weighted gap closure score
3. **Discrepancy Agent**: Detect anomalies and flags
4. **Decision Agent**: Route based on score and rules

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (tested with 3.11, 3.12)
- pip package manager

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Agentic_AI_Demo_Challenge

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
cd medchart_demo
pip install -r requirements.txt

# Initialize database
python -c "import db; db.init_db()"

# Run the application
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📁 Project Structure

```
Agentic_AI_Demo_Challenge/
├── medchart_demo/
│   ├── app.py                      # Streamlit UI (3 tabs)
│   ├── db.py                       # Database layer
│   ├── agents.py                   # 4 validation agents
│   ├── check_db.py                 # Database utility
│   ├── requirements.txt            # Python dependencies
│   ├── medchart.db                 # SQLite database (auto-created)
│   ├── sample_data/
│   │   ├── gap_report.csv          # Care gap definitions
│   │   ├── chart_MBR001.txt        # Test case 1 (Approved)
│   │   ├── chart_MBR002.txt        # Test case 2 (Rejected)
│   │   ├── chart_MBR003.txt        # Test case 3 (Manual Review)
│   │   ├── chart_MBR004.txt        # Test case 4 (Approved)
│   │   └── chart_MBR005.txt        # Test case 5 (Approved with flag)
│   ├── FLOW_DIAGRAM.md             # System architecture diagrams
│   ├── LLM_ANALYTICS_PLAN.md       # Optional LLM enhancement plan
│   └── TEST_CASES.md               # Detailed test documentation
├── MedicalChartAgentFlow/
│   ├── IMPLEMENTATION_GUIDE.md     # Step-by-step implementation
│   ├── QUICK_START.md              # Quick reference
│   └── TROUBLESHOOTING.md          # Common issues
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## 🧪 Test Cases

The system includes 5 pre-configured test cases:

| Case | Member | Decision | Score | Description |
|------|--------|----------|-------|-------------|
| 1 | MBR001 | ✅ Approved | 1.00 | Perfect match, no flags |
| 2 | MBR002 | ❌ Rejected | 0.50 | ICD code mismatch |
| 3 | MBR003 | ⚠️ Manual Review | 0.80 | High severity flag (date >365 days) |
| 4 | MBR004 | ✅ Approved | 1.00 | Immunization case |
| 5 | MBR005 | ✅ Approved | 0.90 | Medium flag, still approved |

See `medchart_demo/TEST_CASES.md` for detailed analysis.

## 📈 Scoring System

### Base Score Calculation

- **ICD Code Match**: 50% weight
- **Date in Window**: 40% weight
- **Provider NPI Present**: 10% weight

### Penalty System

- **High Severity**: -0.20 per flag
- **Medium Severity**: -0.10 per flag
- **Low Severity**: -0.03 per flag

### Decision Thresholds

- **Approved**: Score ≥ 0.85
- **Rejected**: Score ≤ 0.40
- **Manual Review**: 0.40 < Score < 0.85

### Hard Override Rules (Priority)

1. Missing Member ID → **REJECTED**
2. High Severity Flags > 0 → **MANUAL REVIEW**
3. ICD Match = 0.0 → **REJECTED**

## 🎨 User Interface

### Tab 1: Validate
- Upload charts (TXT/PDF) or use sample data
- Load gap report (CSV)
- Run 4-agent validation pipeline
- View real-time agent execution
- See final decision with reasoning

### Tab 2: Results
- View all validation history
- Filter by decision type
- Expand for detailed scores and flags
- See per-rule score breakdown

### Tab 3: Dashboard
- Summary metrics (Total, Approved, Rejected, Manual Review)
- Decisions over time chart
- Decision distribution chart
- Real-time updates

## 🔧 Configuration

### Database
- Location: `medchart_demo/medchart.db`
- Type: SQLite
- Schema: Single `results` table with 10 columns

### Known ICD-10 Codes
Edit `agents.py` to add/remove codes:
```python
KNOWN_ICD = {"Z00.00", "Z12.31", "E11.9", "Z23", "Z79.4", "Z13.1", "E11.65"}
```

### Scoring Weights
Edit `agents.py` in `run_gap_match_agent()`:
```python
composite = scores["icd_match"] * 0.5 + \
            scores["date_in_window"] * 0.4 + \
            scores["provider_npi"] * 0.1
```

## 🤖 Optional: LLM Analytics

The system supports optional LLM-powered analytics that provide insights WITHOUT affecting validation decisions.

See `medchart_demo/LLM_ANALYTICS_PLAN.md` for:
- Trend analysis
- Natural language queries
- Root cause analysis
- Automated alerts
- Decision explanations

## 📊 Performance

- **Processing Time**: <10 seconds per chart
- **Throughput**: 100+ charts/day
- **Database**: Handles 10,000+ results efficiently
- **Memory**: ~50MB typical usage

## 🔒 Security & Privacy

- No external API calls (core system)
- Local SQLite database
- No PII sent to external services
- Optional LLM analytics can use local models

## 🐛 Troubleshooting

### Common Issues

**"Module not found: db"**
- Run from `medchart_demo` directory
- Ensure virtual environment is activated

**"Sample file not found"**
- Verify `sample_data/` folder exists
- Check all 5 chart files are present

**Database locked**
- Close all Python processes
- Delete `medchart.db` and reinitialize

**Streamlit won't start**
- Check port 8501 availability
- Try: `streamlit run app.py --server.port 8502`

See `MedicalChartAgentFlow/TROUBLESHOOTING.md` for more.

## 📚 Documentation

- **Implementation Guide**: `MedicalChartAgentFlow/IMPLEMENTATION_GUIDE.md`
- **Flow Diagrams**: `medchart_demo/FLOW_DIAGRAM.md`
- **Test Cases**: `medchart_demo/TEST_CASES.md`
- **LLM Analytics**: `medchart_demo/LLM_ANALYTICS_PLAN.md`

## 🎯 Success Metrics

- ✅ All 5 test cases validate correctly
- ✅ Dashboard shows accurate metrics
- ✅ Results persist after app restart
- ✅ Demo completes in <5 minutes

## 🚀 Future Enhancements

1. **Real PDF Parsing** - Handle actual hospital PDFs
2. **FastAPI Backend** - Multi-user web application
3. **NPI Validation** - Luhn algorithm check
4. **Reviewer Override** - Manual decision changes
5. **CSV Export** - Download results table
6. **Authentication** - User login system
7. **LLM Analytics** - Optional AI-powered insights

## 📝 License

This is a demonstration project for educational purposes.

## 👥 Contributing

This is a demo project. For production use, consider:
- Adding comprehensive error handling
- Implementing user authentication
- Adding audit logging
- Scaling database for production
- Adding API endpoints

## 📧 Contact

For questions or issues, please refer to the documentation or create an issue in the repository.

---

**Built with:** Python, Streamlit, SQLite, Pandas, PDFPlumber

**Key Principle:** Zero-LLM core for 100% auditable, deterministic decisions
