# Medical Chart Validation System - Design Documentation

## 📋 Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Design](#2-architecture-design)
3. [Data Flow](#3-data-flow)
4. [Agent Design](#4-agent-design)
5. [Decision Logic](#5-decision-logic)
6. [Database Schema](#6-database-schema)
7. [UI/UX Design](#7-uiux-design)
8. [Scoring Algorithm](#8-scoring-algorithm)
9. [Error Handling](#9-error-handling)
10. [Security Considerations](#10-security-considerations)
11. [Performance Characteristics](#11-performance-characteristics)
12. [Extensibility](#12-extensibility)

---

## 1. System Overview

### 1.1 Purpose
The Medical Chart Validation System is a deterministic, rule-based engine that validates medical charts against care gap requirements. It routes charts to one of three outcomes: **Approved**, **Rejected**, or **Manual Review**.

### 1.2 Key Principles

**Zero-LLM Design**
- All decisions are algorithmic and deterministic
- 100% auditable and explainable
- No black-box AI decision-making
- Reproducible results for the same input

**Simplicity First**
- Minimal dependencies (3 packages)
- Single-file modules
- No complex frameworks
- Easy to understand and maintain

**Demo-Optimized**
- 2-hour implementation timeline
- Visual progress tracking
- Real-time feedback
- Sample data included

### 1.3 Technology Stack

```
┌─────────────────────────────────────────┐
│           Streamlit UI Layer            │
│  (Upload, Progress, Results, Dashboard) │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Agent Processing Layer          │
│  (Extract → Gap Match → Discrepancy →   │
│              Decision)                   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│        Data Persistence Layer           │
│         (SQLite Database)               │
└─────────────────────────────────────────┘
```

**Components:**
- **Frontend**: Streamlit (Python-based web framework)
- **Backend**: Pure Python functions (no API layer)
- **Database**: SQLite3 (built-in, file-based)
- **Text Processing**: Regex (no NLP libraries)
- **PDF Parsing**: pdfplumber + Groq LLM (intelligent extraction)
- **AI Analytics**: Groq Llama 3.3 70B (free tier, optional)
- **Data Protocol**: MCP (Model Context Protocol, optional)
- **PDF Parsing**: pdfplumber (optional, demo uses .txt)

---

## 2. Architecture Design

### 2.1 System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Streamlit App                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │  Validate  │  │  Results   │  │ Dashboard  │        │
│  │    Tab     │  │    Tab     │  │    Tab     │        │
│  └────────────┘  └────────────┘  └────────────┘        │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│                   Agent Pipeline                         │
│                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐           │
│  │ Extract  │ → │ Gap Match│ → │Discrepancy│           │
│  │  Agent   │   │  Agent   │   │  Agent    │           │
│  └──────────┘   └──────────┘   └──────────┘           │
│                         ↓                                │
│                  ┌──────────┐                           │
│                  │ Decision │                           │
│                  │  Agent   │                           │
│                  └──────────┘                           │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│                  Database Layer                          │
│  ┌────────────────────────────────────────────────┐     │
│  │              SQLite Database                   │     │
│  │  ┌──────────────────────────────────────┐     │     │
│  │  │         results table                │     │     │
│  │  │  - id, member_id, filename           │     │     │
│  │  │  - decision, confidence, gap_score   │     │     │
│  │  │  - disc_count, flags, reasoning      │     │     │
│  │  └──────────────────────────────────────┘     │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
```

### 2.2 Module Structure

```
medchart_demo/
│
├── app.py                    # Streamlit UI (220 lines)
│   ├── Tab 1: Validate       # Upload + agent execution
│   ├── Tab 2: Results        # Historical results table
│   └── Tab 3: Dashboard      # Metrics + charts
│
├── agents.py                 # Agent logic (150 lines)
│   ├── run_extract_agent()   # Regex-based extraction
│   ├── run_gap_match_agent() # Scoring logic
│   ├── run_discrepancy_agent() # Flag detection
│   └── run_decision_agent()  # Final routing
│
├── db.py                     # Database layer (60 lines)
│   ├── init_db()             # Schema creation
│   ├── save_result()         # Insert validation result
│   ├── get_all_results()     # Fetch all records
│   └── get_summary()         # Aggregate metrics
│
└── sample_data/              # Test data
    ├── gap_report.csv        # Gap requirements
    ├── chart_MBR001.txt      # Test case: Approved
    ├── chart_MBR002.txt      # Test case: Rejected
    └── chart_MBR003.txt      # Test case: Manual Review
```

### 2.3 Design Patterns

**1. Pipeline Pattern**
- Sequential agent execution
- Each agent transforms data for the next
- Clear separation of concerns

**2. Strategy Pattern**
- Different validation strategies per agent
- Pluggable scoring rules
- Easy to add new checks

**3. Repository Pattern**
- Database abstraction in `db.py`

### 2.4 Enhanced Architecture with Groq LLM and MCP

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Streamlit App (Enhanced)                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │  Validate  │  │  Results   │  │ Dashboard  │  │AI Insights │   │
│  │    Tab     │  │    Tab     │  │    Tab     │  │    Tab     │   │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
         ↓                                                    ↓
┌─────────────────────────┐                    ┌──────────────────────┐
│   PDF Input Processing  │                    │   AI Analytics Layer │
│  ┌──────────────────┐   │                    │  ┌────────────────┐  │
│  │   pdfplumber     │   │                    │  │  Groq Llama    │  │
│  │  (Text Extract)  │   │                    │  │  3.3 70B       │  │
│  └────────┬─────────┘   │                    │  │  (Free Tier)   │  │
│           ↓              │                    │  └────────────────┘  │
│  ┌──────────────────┐   │                    │         ↕             │
│  │  Groq Extractor  │   │                    │  ┌────────────────┐  │
│  │  (LLM-powered)   │   │                    │  │  llm_service   │  │
│  │  ✓ Smart parsing │   │                    │  │  - Trends      │  │
│  │  ✓ Fallback to   │   │                    │  │  - NL Queries  │  │
│  │    regex         │   │                    │  │  - Root Cause  │  │
│  └──────────────────┘   │                    │  └────────────────┘  │
└─────────────────────────┘                    └──────────────────────┘
         ↓                                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│                      Agent Pipeline (Core)                           │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │ Extract  │ → │ Gap Match│ → │Discrepancy│ → │ Decision │        │
│  │  Agent   │   │  Agent   │   │  Agent    │   │  Agent   │        │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘        │
└──────────────────────────────────────────────────────────────────────┘
         ↓                                                    ↓
┌─────────────────────────┐                    ┌──────────────────────┐
│   Database Layer        │                    │   MCP Protocol Layer │
│  ┌──────────────────┐   │                    │  ┌────────────────┐  │
│  │  SQLite DB       │   │                    │  │  MCP Server    │  │
│  │  - results       │   │◄───────────────────┤  │  (Optional)    │  │
│  │  - validation    │   │   Standardized     │  │  ✓ Resources   │  │
│  │    history       │   │   Data Access      │  │  ✓ Tools       │  │
│  └──────────────────┘   │                    │  │  ✓ Auditable   │  │
└─────────────────────────┘                    │  └────────────────┘  │
                                               └──────────────────────┘
```

### 2.5 Groq LLM Integration for PDF Extraction

**Purpose:** Intelligent extraction from PDF medical charts with automatic fallback

**Architecture:**
```
PDF File Input
     ↓
pdfplumber (Text Extraction)
     ↓
Raw Text
     ↓
┌─────────────────────────────────┐
│   Groq PDF Extractor            │
│   (groq_extractor.py)           │
│                                 │
│   Model: Llama 3.3 70B          │
│   Temperature: 0.1 (precise)    │
│   Max Tokens: 1200              │
│                                 │
│   ┌─────────────────────────┐   │
│   │  Structured Prompt      │   │
│   │  - Extract member_id    │   │
│   │  - Extract visit_date   │   │
│   │  - Extract NPI          │   │
│   │  - Extract ICD codes    │   │
│   │  - Extract lab values   │   │
│   └─────────────────────────┘   │
│            ↓                    │
│   ┌─────────────────────────┐   │
│   │  JSON Response          │   │
│   │  Validation & Cleanup   │   │
│   └─────────────────────────┘   │
└─────────────────────────────────┘
     ↓
Structured Data
     ↓
┌─────────────────────────────────┐
│   Fallback on Error             │
│   → Regex Extraction            │
│   → Ensures system reliability  │
└─────────────────────────────────┘
```

**Key Features:**
1. **Smart Extraction:** LLM understands context and variations in PDF format
2. **Automatic Fallback:** Falls back to regex if LLM fails
3. **Caching:** MD5-based caching prevents redundant API calls
4. **Free Tier:** Groq provides 6000 requests/minute free
5. **Fast:** 10x faster than typical LLM APIs

**Implementation Details:**
```python
class GroqPDFExtractor:
    def __init__(self, api_key, model="llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.cache = {}  # MD5-based response cache
    
    def extract_from_text(self, chart_text):
        # Check cache first
        cache_key = self._get_cache_key(chart_text)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Build structured prompt
        prompt = self._build_extraction_prompt(chart_text)
        
        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[...],
            temperature=0.1,  # Precise extraction
            max_tokens=1200
        )
        
        # Parse and validate JSON response
        extracted_data = json.loads(response.content)
        validated = self._validate_extraction(extracted_data)
        
        # Cache result
        self.cache[cache_key] = validated
        return validated
```

**Extraction Prompt Structure:**
```
Extract structured information from this medical chart text.
Return ONLY valid JSON.

Chart Text:
{chart_text}

Return JSON with exactly these keys:
{
  "member_id": string or null,
  "visit_date": string (YYYY-MM-DD) or null,
  "npi": string or null,
  "icd_codes": array of strings,
  "all_codes": array of strings,
  "hba1c": number or null,
  "lab_date": string (YYYY-MM-DD) or null
}

Rules:
- Return only JSON
- Use null for missing scalar fields
- Use [] for missing arrays
- Convert dates to YYYY-MM-DD
- Include diagnosis codes in both icd_codes and all_codes
- hba1c must be numeric only
```

**Fallback Strategy:**
```python
def run_extract_agent(text, file_type="txt", use_groq_for_pdf=True):
    if file_type == "pdf" and use_groq_for_pdf:
        try:
            # Try Groq LLM extraction
            extractor = GroqPDFExtractor(api_key=groq_api_key)
            result = extractor.extract_from_text(text)
            result["_extraction_meta"] = {
                "method_used": "groq_pdf",
                "llm_status": "passed"
            }
            return result
        except Exception as e:
            # Fallback to regex
            result = _regex_extract_fallback(text)
            result["_extraction_meta"] = {
                "method_used": "regex_fallback",
                "llm_status": "failed",
                "llm_error": str(e)
            }
            return result
    else:
        # Use regex for TXT files
        return _regex_extract_fallback(text)
```

### 2.6 MCP (Model Context Protocol) Integration

**Purpose:** Standardized protocol for AI to access validation data

**Architecture:**
```
┌──────────────────────────────────────────────────────────┐
│                    MCP Server                            │
│                  (mcp_server.py)                         │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │              Resources (Read-Only)             │     │
│  │                                                │     │
│  │  1. medchart://results/all                    │     │
│  │     → All validation results                  │     │
│  │                                                │     │
│  │  2. medchart://results/summary                │     │
│  │     → Aggregate metrics                       │     │
│  │                                                │     │
│  │  3. medchart://results/recent?days=30         │     │
│  │     → Recent results with date filter         │     │
│  │                                                │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │              Tools (Dynamic Queries)           │     │
│  │                                                │     │
│  │  1. filter_by_decision(decision: str)         │     │
│  │     → Filter results by approval status       │     │
│  │                                                │     │
│  │  2. filter_by_member(member_id: str)          │     │
│  │     → Get all results for a member            │     │
│  │                                                │     │
│  │  3. get_trend_data(days: int)                 │     │
│  │     → Time-series data for analysis           │     │
│  │                                                │     │
│  │  4. get_daily_metrics()                       │     │
│  │     → Last 24 hours summary                   │     │
│  │                                                │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
                         ↕
┌──────────────────────────────────────────────────────────┐
│              LLM Service with MCP Client                 │
│              (llm_service_mcp.py)                        │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │         MCP Client Session                     │     │
│  │  - Connects to MCP server                      │     │
│  │  - Reads resources via URIs                    │     │
│  │  - Calls tools with parameters                 │     │
│  │  - Automatic fallback to direct DB access      │     │
│  └────────────────────────────────────────────────┘     │
│                         ↓                                │
│  ┌────────────────────────────────────────────────┐     │
│  │         AI Analytics Functions                 │     │
│  │  - analyze_trends_mcp(days)                    │     │
│  │  - natural_language_query(question, df)        │     │
│  │  - root_cause_analysis(filtered_df)            │     │
│  │  - explain_decision(result)                    │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│                   Groq Llama 3.3 70B                     │
│                   (Free Tier API)                        │
│  - 6000 requests/minute                                  │
│  - No credit card required                               │
│  - 10x faster than typical APIs                          │
└──────────────────────────────────────────────────────────┘
```

**MCP Benefits:**

1. **Standardization:**
   - Consistent data access pattern
   - Well-defined resource URIs
   - Typed tool parameters

2. **Security:**
   - Read-only resources
   - Auditable access logs
   - No direct database manipulation

3. **Extensibility:**
   - Easy to add new resources
   - Simple tool registration
   - Can connect to multiple data sources

4. **AI-Friendly:**
   - LLMs understand MCP protocol
   - Self-documenting resources
   - Clear tool descriptions

**MCP Resource Examples:**

```python
# Resource 1: All Results
@server.list_resources()
async def list_resources():
    return [
        Resource(
            uri="medchart://results/all",
            name="All Validation Results",
            description="Complete history of chart validations",
            mimeType="application/json"
        )
    ]

# Resource 2: Summary
@server.read_resource()
async def read_resource(uri: str):
    if uri == "medchart://results/summary":
        summary = db.get_summary()
        return json.dumps(summary, indent=2)
```

**MCP Tool Examples:**

```python
# Tool 1: Filter by Decision
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="filter_by_decision",
            description="Filter validation results by decision type",
            inputSchema={
                "type": "object",
                "properties": {
                    "decision": {
                        "type": "string",
                        "enum": ["approved", "rejected", "manual_review"],
                        "description": "Decision type to filter by"
                    }
                },
                "required": ["decision"]
            }
        )
    ]

# Tool 2: Get Trend Data
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_trend_data":
        days = arguments.get("days", 30)
        results = db.get_results_for_analysis(days=days)
        return json.dumps(results, indent=2)
```

**MCP Client Usage in LLM Service:**

```python
class LLMAnalyticsMCP(LLMAnalytics):
    def __init__(self, use_mcp=True):
        super().__init__()
        self.use_mcp = use_mcp
        self.mcp_available = False
        
        if use_mcp:
            try:
                # Initialize MCP client
                self.mcp_client = self._init_mcp_client()
                self.mcp_available = True
            except Exception as e:
                # Fallback to direct access
                self.mcp_available = False
    
    async def analyze_trends_mcp(self, days=30):
        """Analyze trends using MCP protocol"""
        if self.mcp_available:
            # Read data via MCP
            async with self.mcp_client:
                # Read recent results resource
                uri = f"medchart://results/recent?days={days}"
                response = await self.mcp_client.read_resource(uri)
                data = json.loads(response.content)
                
                # Generate insights with Groq
                insights = self.generate(
                    prompt=self._build_trend_prompt(data),
                    max_tokens=800
                )
                return insights
        else:
            # Fallback to direct database access
            return self.analyze_trends(
                db.get_results_for_analysis(days=days),
                days=days
            )
```

**MCP vs Direct Access Comparison:**

| Aspect | MCP Protocol | Direct Database |
|--------|-------------|-----------------|
| **Data Access** | Via standardized URIs | Direct SQL queries |
| **Security** | Read-only resources | Full database access |
| **Auditability** | All access logged | Limited logging |
| **Extensibility** | Easy to add sources | Requires code changes |
| **Performance** | Slight overhead | Direct, fastest |
| **AI Integration** | Native LLM support | Manual integration |
| **Complexity** | Requires MCP server | Simple, direct |
| **Use Case** | Production, multi-source | Development, single DB |

**When to Use MCP:**
- ✅ Production environments
- ✅ Multiple data sources
- ✅ Need audit trails
- ✅ AI-first architecture
- ✅ Team collaboration

**When to Use Direct Access:**
- ✅ Development/testing
- ✅ Single database
- ✅ Maximum performance
- ✅ Simple deployments
- ✅ Quick prototypes

### 2.7 AI Analytics Layer Architecture

**Purpose:** Provide intelligent insights without affecting core validation

**Key Principle:** AI analytics are **completely separate** from validation decisions

```
┌──────────────────────────────────────────────────────────┐
│              Core Validation Pipeline                    │
│         (100% Deterministic, No AI)                      │
│                                                          │
│  Extract → Gap Match → Discrepancy → Decision           │
│                                                          │
│  ✓ Rule-based                                           │
│  ✓ Reproducible                                         │
│  ✓ Auditable                                            │
│  ✓ No LLM involvement                                   │
└──────────────────────────────────────────────────────────┘
                         ↓
                   [Saves to DB]
                         ↓
┌──────────────────────────────────────────────────────────┐
│              AI Analytics Layer                          │
│         (Optional, Post-Processing Only)                 │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │  Trend Analysis                                │     │
│  │  - Identify patterns in validation history    │     │
│  │  - Predict future trends                      │     │
│  │  - Recommend improvements                     │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │  Natural Language Queries                      │     │
│  │  - "What's the rejection rate this week?"     │     │
│  │  - "Which member has most manual reviews?"    │     │
│  │  - "Show me approval trends"                  │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │  Root Cause Analysis                           │     │
│  │  - Why are charts being rejected?             │     │
│  │  - Common flag patterns                       │     │
│  │  - Data quality issues                        │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │  Decision Explanations                         │     │
│  │  - Human-friendly explanations                │     │
│  │  - Clinical perspective                       │     │
│  │  - Compliance perspective                     │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
```

**AI Analytics Features:**

1. **Trend Analysis:**
   ```python
   def analyze_trends(self, results_df, days=30):
       """Analyze validation trends over time"""
       summary = {
           'total': len(results_df),
           'approved': decision_counts.get('approved', 0),
           'rejected': decision_counts.get('rejected', 0),
           'manual_review': decision_counts.get('manual_review', 0),
           'avg_confidence': results_df['confidence'].mean(),
           'common_flags': results_df['flags'].value_counts().head(5)
       }
       
       prompt = f"""
       Analyze these medical chart validation results:
       {json.dumps(summary, indent=2)}
       
       Provide:
       1. Key Trends
       2. Potential Issues
       3. Recommendations
       4. Predictions
       """
       
       return self.generate(prompt, max_tokens=800)
   ```

2. **Natural Language Queries:**
   ```python
   def natural_language_query(self, question, results_df):
       """Answer questions about validation data"""
       stats = {
           'total': len(results_df),
           'decisions': results_df['decision'].value_counts().to_dict(),
           'avg_confidence': results_df['confidence'].mean()
       }
       
       prompt = f"""
       Question: {question}
       
       Available Data:
       {json.dumps(stats, indent=2)}
       
       Provide a clear, concise answer with specific numbers.
       """
       
       return self.generate(prompt, max_tokens=400)
   ```

3. **Root Cause Analysis:**
   ```python
   def root_cause_analysis(self, filtered_results):
       """Identify root causes for patterns"""
       summary = {
           'count': len(filtered_results),
           'common_flags': filtered_results['flags'].value_counts().head(5),
           'avg_confidence': filtered_results['confidence'].mean()
       }
       
       prompt = f"""
       Perform root cause analysis on these flagged charts:
       {json.dumps(summary, indent=2)}
       
       Identify:
       1. Root Causes
       2. Preventable Issues
       3. Data Quality Problems
       4. Training Needs
       """
       
       return self.generate(prompt, max_tokens=700)
   ```

**AI Analytics Guarantees:**

✅ **Never modifies validation decisions**
✅ **Operates only on historical data**
✅ **Can be disabled without affecting core system**
✅ **Provides insights, not decisions**
✅ **Fully optional feature**

- Clean separation of data access
- Easy to swap SQLite for PostgreSQL

---

## 3. Data Flow

### 3.1 High-Level Flow

```
┌─────────────┐
│   User      │
│  Uploads    │
│   Chart     │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────────┐
│  1. EXTRACT AGENT                       │
│  Input:  Raw chart text                 │
│  Output: Structured data                │
│    {member_id, visit_date, npi,         │
│     icd_codes, hba1c, raw_text}         │
└──────┬──────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────┐
│  2. GAP MATCH AGENT                     │
│  Input:  Extracted data + gap_row       │
│  Output: Composite score + per-rule     │
│    {composite: 0.9,                     │
│     per_rule: {icd_match: 1.0,          │
│                date_in_window: 1.0,     │
│                provider_npi: 1.0}}      │
└──────┬──────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────┐
│  3. DISCREPANCY AGENT                   │
│  Input:  Extracted data                 │
│  Output: List of flags                  │
│    [{severity: "high",                  │
│      msg: "Lab date 631 days old"}]     │
└──────┬──────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────┐
│  4. DECISION AGENT                      │
│  Input:  Gap result + flags + extracted │
│  Output: Final decision                 │
│    {decision: "manual_review",          │
│     score: 0.80,                        │
│     reason: "1 high-severity flag"}     │
└──────┬──────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────┐
│  5. DATABASE SAVE                       │
│  Persist result to SQLite               │
└──────┬──────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────┐
│  6. UI UPDATE                           │
│  Show result banner + update dashboard  │
└─────────────────────────────────────────┘
```

### 3.2 Data Transformations

**Stage 1: Raw Text → Structured Data**
```
Input:
"Member ID: MBR001
Visit Date: 2024-09-15
Provider NPI: 1234567890
Diagnosis Codes: Z00.00, Z23
Lab Results: HbA1c: 6.8 on 2024-09-15"

Output:
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

**Stage 2: Structured Data → Scores**
```
Input: Extracted data + Gap requirement
{
  required_icd_codes: "Z00.00",
  window_start: "2024-01-01",
  window_end: "2024-12-31"
}

Output:
{
  "composite": 1.0,
  "per_rule": {
    "icd_match": 1.0,      # Weight: 0.5
    "date_in_window": 1.0, # Weight: 0.4
    "provider_npi": 1.0    # Weight: 0.1
  }
}
```

**Stage 3: Structured Data → Flags**
```
Input: Extracted data

Output:
[
  {
    "severity": "high",
    "msg": "Lab date 2023-03-10 is 631 days from visit"
  }
]
```

**Stage 4: Scores + Flags → Decision**
```
Input:
- Gap score: 1.0
- Flags: 1 high-severity flag

Calculation:
- Base score: 1.0
- Penalty: 1 × 0.20 = 0.20
- Final score: 1.0 - 0.20 = 0.80

Output:
{
  "decision": "manual_review",  # High flag triggers override
  "score": 0.80,
  "reason": "1 high-severity flag(s) found"
}
```

---

## 4. Agent Design

### 4.1 Agent 1: Extract Agent

**Purpose**: Parse unstructured chart text into structured data

**Input**: Raw chart text (string)

**Output**: Dictionary with extracted fields

**Algorithm**:
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

**Key Design Decisions**:
- **Regex over NLP**: Simpler, faster, deterministic
- **Known ICD set**: Validates codes without external API
- **Preserve raw text**: Needed for downstream agents
- **Separate valid/all codes**: Detect typos/unknown codes

**Error Handling**:
- Missing fields return `None`
- Invalid codes filtered out but preserved in `all_codes`
- Malformed dates/numbers return `None`

### 4.2 Agent 2: Gap Match Agent

**Purpose**: Calculate how well the chart closes the care gap

**Input**: 
- Extracted data (dict)
- Gap requirement row (dict)

**Output**: Composite score + per-rule breakdown

**Scoring Rules**:

| Rule | Weight | Logic | Score |
|------|--------|-------|-------|
| R1: ICD Match | 0.5 | Any required code in chart? | 1.0 or 0.0 |
| R2: Date in Window | 0.4 | Visit date within gap window? | 1.0 or 0.0 |
| R3: NPI Present | 0.1 | Provider NPI exists? | 1.0 or 0.0 |

**Composite Score Formula**:
```
composite = (R1 × 0.5) + (R2 × 0.4) + (R3 × 0.1)
```

**Examples**:
```
Case 1: All criteria met
R1=1.0, R2=1.0, R3=1.0 → composite = 1.0

Case 2: ICD mismatch
R1=0.0, R2=1.0, R3=1.0 → composite = 0.5

Case 3: Date outside window
R1=1.0, R2=0.0, R3=1.0 → composite = 0.6
```

**Key Design Decisions**:
- **Binary scoring**: Simplifies logic, clear pass/fail
- **Weighted rules**: ICD match most important (50%)
- **Date validation**: Uses Python's `date.fromisoformat()`
- **Graceful degradation**: Try-catch for date parsing

### 4.3 Agent 3: Discrepancy Agent

**Purpose**: Detect anomalies and data quality issues

**Input**: Extracted data (dict)

**Output**: List of flags with severity levels

**Checks**:

| Check | Severity | Condition | Example |
|-------|----------|-----------|---------|
| D1: HbA1c Range | High | Value > 15 or < 2 | HbA1c: 18.5 |
| D2: Lab Date Gap | High/Medium | Lab > 365 days old (high)<br>Lab > 180 days old (medium) | Lab: 2023-03-10<br>Visit: 2024-12-01 |
| D3: Unknown Codes | Low | Code not in KNOWN_ICD | Diagnosis: XYZ123 |
| D4: Missing Member ID | High | member_id is None | (no Member ID field) |

**Flag Structure**:
```python
{
  "severity": "high" | "medium" | "low",
  "msg": "Human-readable description"
}
```

**Key Design Decisions**:
- **Severity levels**: Enable graduated penalties
- **Physiological bounds**: HbA1c 2-15% is normal range
- **Date gap thresholds**: 180/365 days based on clinical guidelines
- **Preserve unknown codes**: Help identify data entry errors

### 4.4 Agent 4: Decision Agent

**Purpose**: Make final routing decision based on score and flags

**Input**:
- Gap result (dict with composite score)
- Flags (list)
- Extracted data (dict)

**Output**: Decision + score + reason

**Decision Logic**:

```
┌─────────────────────────────────────────┐
│  1. Calculate Penalties                 │
│     high_count × 0.20                   │
│     medium_count × 0.10                 │
│     low_count × 0.03                    │
└──────┬──────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────┐
│  2. Apply Penalties                     │
│     score = base - total_penalty        │
│     score = clamp(score, 0.0, 1.0)      │
└──────┬──────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────┐
│  3. Check Hard Overrides (in order)     │
│     ├─ Missing member_id? → REJECTED    │
│     ├─ Any high flags? → MANUAL_REVIEW  │
│     └─ ICD match = 0? → REJECTED        │
└──────┬──────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────┐
│  4. Apply Thresholds                    │
│     ├─ score ≥ 0.85 → APPROVED          │
│     ├─ score ≤ 0.40 → REJECTED          │
│     └─ else → MANUAL_REVIEW             │
└─────────────────────────────────────────┘
```

**Penalty Weights**:
- High severity: -0.20 (20% penalty)
- Medium severity: -0.10 (10% penalty)
- Low severity: -0.03 (3% penalty)

**Threshold Rationale**:
- **≥ 0.85**: High confidence, auto-approve
- **≤ 0.40**: Low confidence, auto-reject
- **0.41-0.84**: Uncertain, needs human review

**Hard Override Priority**:
1. Missing member ID (data integrity)
2. High-severity flags (safety)
3. ICD mismatch (requirement not met)

**Key Design Decisions**:
- **Penalties before overrides**: Calculate score first
- **Override hierarchy**: Safety > completeness > matching
- **Conservative thresholds**: Prefer manual review over errors
- **Explainable reasons**: Every decision has a reason string

---

## 5. Decision Logic

### 5.1 Decision Tree

```
                    ┌─────────────┐
                    │   Start     │
                    └──────┬──────┘
                           │
                           ↓
                  ┌────────────────┐
                  │ Member ID      │
                  │ present?       │
                  └────┬───────┬───┘
                       │       │
                   NO  │       │ YES
                       │       │
                       ↓       ↓
                  ┌────────┐  ┌────────────────┐
                  │REJECTED│  │ High severity  │
                  │        │  │ flags?         │
                  └────────┘  └────┬───────┬───┘
                                   │       │
                               YES │       │ NO
                                   │       │
                                   ↓       ↓
                          ┌────────────┐  ┌────────────────┐
                          │MANUAL      │  │ ICD match      │
                          │REVIEW      │  │ = 0?           │
                          └────────────┘  └────┬───────┬───┘
                                               │       │
                                           YES │       │ NO
                                               │       │
                                               ↓       ↓
                                          ┌────────┐  ┌────────────────┐
                                          │REJECTED│  │ Score ≥ 0.85?  │
                                          │        │  └────┬───────┬───┘
                                          └────────┘       │       │
                                                       YES │       │ NO
                                                           │       │
                                                           ↓       ↓
                                                      ┌────────┐  ┌────────────────┐
                                                      │APPROVED│  │ Score ≤ 0.40?  │
                                                      │        │  └────┬───────┬───┘
                                                      └────────┘       │       │
                                                                   YES │       │ NO
                                                                       │       │
                                                                       ↓       ↓
                                                                  ┌────────┐  ┌────────────┐
                                                                  │REJECTED│  │MANUAL      │
                                                                  │        │  │REVIEW      │
                                                                  └────────┘  └────────────┘
```

### 5.2 Test Case Analysis

**Test Case 1: MBR001 (Clean Chart)**

```
Input:
- Member ID: MBR001 ✓
- Visit Date: 2024-09-15 (within window) ✓
- ICD Codes: Z00.00 (matches requirement) ✓
- NPI: 1234567890 ✓
- HbA1c: 6.8 (normal range) ✓
- Lab Date: 2024-09-15 (same day) ✓

Processing:
1. Extract: All fields present
2. Gap Match: R1=1.0, R2=1.0, R3=1.0 → composite=1.0
3. Discrepancy: No flags
4. Decision:
   - Member ID present ✓
   - No high flags ✓
   - ICD match = 1.0 ✓
   - Score = 1.0 - 0 = 1.0
   - 1.0 ≥ 0.85 → APPROVED

Output: ✅ APPROVED (confidence: 100%)
```

**Test Case 2: MBR002 (ICD Mismatch)**

```
Input:
- Member ID: MBR002 ✓
- Visit Date: 2024-11-20 (within window) ✓
- ICD Codes: E11.9, Z79.4 (Z12.31 required) ✗
- NPI: 9876543210 ✓
- HbA1c: 7.9 (normal range) ✓

Processing:
1. Extract: All fields present
2. Gap Match: R1=0.0, R2=1.0, R3=1.0 → composite=0.5
3. Discrepancy: No flags
4. Decision:
   - Member ID present ✓
   - No high flags ✓
   - ICD match = 0.0 → HARD OVERRIDE: REJECTED

Output: ❌ REJECTED (reason: "Required diagnosis code not in chart")
```

**Test Case 3: MBR003 (Date Anomaly)**

```
Input:
- Member ID: MBR003 ✓
- Visit Date: 2024-12-01 (within window) ✓
- ICD Codes: E11.9 (matches requirement) ✓
- NPI: 5551234567 ✓
- HbA1c: 8.2 (normal range) ✓
- Lab Date: 2023-03-10 (631 days old) ✗

Processing:
1. Extract: All fields present
2. Gap Match: R1=1.0, R2=1.0, R3=1.0 → composite=1.0
3. Discrepancy: 1 high flag (lab date gap > 365 days)
4. Decision:
   - Member ID present ✓
   - High flag present → HARD OVERRIDE: MANUAL_REVIEW

Output: ⚠️ MANUAL REVIEW (reason: "1 high-severity flag(s) found")
```

---

## 6. Database Schema

### 6.1 Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      results                            │
├─────────────────────────────────────────────────────────┤
│ id          INTEGER PRIMARY KEY AUTOINCREMENT           │
│ member_id   TEXT NOT NULL                               │
│ filename    TEXT NOT NULL                               │
│ decision    TEXT NOT NULL                               │
│ confidence  REAL NOT NULL                               │
│ gap_score   REAL                                        │
│ disc_count  INTEGER DEFAULT 0                           │
│ flags       TEXT                                        │
│ reasoning   TEXT                                        │
│ created_at  DATETIME DEFAULT CURRENT_TIMESTAMP          │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Field Specifications

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique record identifier |
| `member_id` | TEXT | NOT NULL | Patient/member identifier |
| `filename` | TEXT | NOT NULL | Source chart filename |
| `decision` | TEXT | NOT NULL | One of: approved, rejected, manual_review |
| `confidence` | REAL | NOT NULL | Final score (0.0-1.0) |
| `gap_score` | REAL | NULL | Composite gap match score |
| `disc_count` | INTEGER | DEFAULT 0 | Number of discrepancy flags |
| `flags` | TEXT | NULL | Pipe-separated flag messages |
| `reasoning` | TEXT | NULL | JSON string of per-rule scores |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

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

**Get all results**:
```sql
SELECT * FROM results ORDER BY created_at DESC;
```

**Filter by decision**:
```sql
SELECT * FROM results WHERE decision = 'manual_review';
```

**Get summary counts**:
```sql
SELECT 
  COUNT(*) as total,
  SUM(CASE WHEN decision = 'approved' THEN 1 ELSE 0 END) as approved,
  SUM(CASE WHEN decision = 'rejected' THEN 1 ELSE 0 END) as rejected,
  SUM(CASE WHEN decision = 'manual_review' THEN 1 ELSE 0 END) as manual_review
FROM results;
```

**Get results by date**:
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

### 7.1 Tab 1: Validate

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  🏥 Medical Chart Validation System                     │
│  Zero-LLM algorithmic decision engine                   │
├─────────────────────────────────────────────────────────┤
│  [Validate] [Results] [Dashboard]                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐   │
│  │ 📄 Medical Chart     │  │ 📋 Gap Report        │   │
│  │                      │  │                      │   │
│  │ ○ Upload file        │  │ ☑ Use bundled CSV   │   │
│  │ ● Use sample data    │  │                      │   │
│  │                      │  │ [Gap Report Table]   │   │
│  │ [chart_MBR001.txt ▾] │  │                      │   │
│  │                      │  │                      │   │
│  └──────────────────────┘  └──────────────────────┘   │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         🚀 Run Validation                      │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ━━━━━━━━━━━━━━ Agent Progress ━━━━━━━━━━━━━━━━       │
│  ✅ Extract Agent      — MBR001 | 2 codes | 2024-09-15 │
│  ✅ Gap Match Agent    — Score: 1.0 | All criteria met │
│  ✅ Discrepancy Agent  — 0 flags found                 │
│  ✅ Decision Agent     — APPROVED (confidence: 100%)   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ ✅ APPROVED — Confidence: 100%                 │    │
│  │ Reason: Score 1.0 (base 1.0 - penalty 0.0)     │    │
│  │ 💾 Result saved to database                    │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

**User Flow**:
1. Select chart source (upload or sample)
2. Select gap report (upload or bundled)
3. Click "Run Validation"
4. Watch agents execute sequentially
5. See final decision banner
6. Result auto-saved to database

**Design Principles**:
- **Progressive disclosure**: Show results only after execution
- **Real-time feedback**: Status blocks update live
- **Clear outcomes**: Color-coded banners (green/red/yellow)
- **Minimal clicks**: Sample data pre-selected

### 7.2 Tab 2: Results

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  📊 Validation Results                                  │
├─────────────────────────────────────────────────────────┤
│  Filter: [All ▾]                                        │
│  Showing 3 of 3 results                                 │
│                                                          │
│  ▼ ✅ MBR001 — APPROVED (100%) — 2024-12-01 10:30      │
│     ┌─────────────────────────────────────────────┐    │
│     │ Confidence: 100%    Gap Score: 1.0          │    │
│     │ Flags: 0            Filename: chart_MBR001  │    │
│     │                                              │    │
│     │ Per-Rule Scores:                             │    │
│     │ • ICD Match: 1.0                             │    │
│     │ • Date in Window: 1.0                        │    │
│     │ • Provider NPI: 1.0                          │    │
│     └─────────────────────────────────────────────┘    │
│                                                          │
│  ▶ ❌ MBR002 — REJECTED (50%) — 2024-12-01 10:31       │
│                                                          │
│  ▶ ⚠️ MBR003 — MANUAL REVIEW (80%) — 2024-12-01 10:32  │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- Expandable rows for details
- Filter by decision type
- Per-rule score breakdown
- Flag details
- Timestamp tracking

### 7.3 Tab 3: Dashboard

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  📈 Dashboard                                           │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ Total: 3 │  │ ✅ 1     │  │ ❌ 1     │  │ ⚠️ 1     ││
│  │          │  │ (33%)    │  │ (33%)    │  │ (33%)    ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
│                                                          │
│  Decisions Over Time                                    │
│  ┌────────────────────────────────────────────────┐    │
│  │     ▇▇▇                                        │    │
│  │     ▇▇▇ ▇▇▇                                    │    │
│  │     ▇▇▇ ▇▇▇ ▇▇▇                                │    │
│  │  ───────────────────────────────────           │    │
│  │  12/01  12/02  12/03                           │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  💡 All decisions are algorithmic — zero LLM used      │
└─────────────────────────────────────────────────────────┘
```

**Metrics**:
- Total processed charts
- Approved count + percentage
- Rejected count + percentage
- Manual review count + percentage
- Time-series bar chart

---

## 8. Scoring Algorithm

### 8.1 Mathematical Model

**Base Score Calculation**:
```
S_base = Σ(w_i × r_i)

where:
  w_i = weight of rule i
  r_i = result of rule i (0.0 or 1.0)

Rules:
  R1: ICD Match        (w=0.5)
  R2: Date in Window   (w=0.4)
  R3: Provider NPI     (w=0.1)

Example:
  R1=1.0, R2=1.0, R3=1.0
  S_base = (0.5×1.0) + (0.4×1.0) + (0.1×1.0) = 1.0
```

**Penalty Calculation**:
```
P_total = Σ(c_s × p_s)

where:
  c_s = count of flags with severity s
  p_s = penalty for severity s

Penalties:
  High:   p_h = 0.20
  Medium: p_m = 0.10
  Low:    p_l = 0.03

Example:
  1 high flag, 2 medium flags, 1 low flag
  P_total = (1×0.20) + (2×0.10) + (1×0.03) = 0.43
```

**Final Score**:
```
S_final = clamp(S_base - P_total, 0.0, 1.0)

where:
  clamp(x, min, max) = max(min, min(x, max))

Example:
  S_base = 1.0, P_total = 0.43
  S_final = clamp(1.0 - 0.43, 0.0, 1.0) = 0.57
```

### 8.2 Score Interpretation

| Score Range | Interpretation | Typical Action |
|-------------|----------------|----------------|
| 0.85 - 1.00 | High confidence | Auto-approve |
| 0.70 - 0.84 | Moderate confidence | Manual review |
| 0.41 - 0.69 | Low confidence | Manual review |
| 0.00 - 0.40 | Very low confidence | Auto-reject |

### 8.3 Sensitivity Analysis

**Impact of Rule Weights**:
```
Scenario: All rules pass except one

ICD Match fails (R1=0):
  S = (0.5×0) + (0.4×1) + (0.1×1) = 0.5
  → Manual review (or rejected by override)

Date fails (R2=0):
  S = (0.5×1) + (0.4×0) + (0.1×1) = 0.6
  → Manual review

NPI fails (R3=0):
  S = (0.5×1) + (0.4×1) + (0.1×0) = 0.9
  → Approved (minimal impact)
```

**Impact of Penalties**:
```
Base score: 1.0

1 high flag:
  S = 1.0 - 0.20 = 0.80 → Manual review (override)

2 medium flags:
  S = 1.0 - 0.20 = 0.80 → Manual review

7 low flags:
  S = 1.0 - 0.21 = 0.79 → Manual review

Combination (1H + 2M + 1L):
  S = 1.0 - 0.43 = 0.57 → Manual review
```

---

## 9. Error Handling

### 9.1 Error Categories

**1. Input Validation Errors**
- File too large (>5MB)
- Invalid file format
- Empty file
- Malformed CSV

**2. Parsing Errors**
- PDF extraction failure
- Regex match failure
- Date parsing error
- Invalid ICD code format

**3. Data Integrity Errors**
- Missing member ID
- Missing required fields
- Duplicate records
- Invalid data types

**4. System Errors**
- Database connection failure
- File I/O error
- Memory overflow
- Unexpected exceptions

### 9.2 Error Handling Strategy

**Graceful Degradation**:
```python
# Example: Date parsing with fallback
try:
    vd = date.fromisoformat(extracted["visit_date"])
    ws = date.fromisoformat(gap_row["window_start"])
    we = date.fromisoformat(gap_row["window_end"])
    date_score = 1.0 if ws <= vd <= we else 0.0
except:
    date_score = 0.0  # Fail gracefully
```

**User Feedback**:
```python
# Example: File size validation
if uploaded_file.size > 5_000_000:
    st.error("❌ File too large. Maximum size is 5MB.")
    return
```

**Logging Strategy**:
- Log all exceptions to console
- Display user-friendly messages in UI
- Preserve stack traces for debugging
- Track error rates in production

### 9.3 Recovery Mechanisms

**Database Errors**:
```python
try:
    db.save_result(...)
    st.success("💾 Result saved to database")
except Exception as e:
    st.error(f"❌ Failed to save result: {str(e)}")
    # Continue execution, don't crash
```

**Agent Failures**:
```python
with st.status("🔍 Extract Agent") as status:
    try:
        extracted = agents.run_extract_agent(chart_text)
        st.json(extracted)
        status.update(label="✅ Extract Agent", state="complete")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        status.update(label="❌ Extract Agent", state="error")
        st.stop()  # Halt pipeline
```

---

## 10. Security Considerations

### 10.1 Data Privacy

**PHI Protection**:
- No external API calls (data stays local)
- SQLite database file-based (no network exposure)
- No logging of sensitive data
- Sample data uses synthetic identifiers

**Access Control**:
- Single-user demo (no authentication)
- File system permissions control database access
- Streamlit runs on localhost by default

### 10.2 Input Validation

**File Upload Restrictions**:
```python
# Size limit
if uploaded_file.size > 5_000_000:
    st.error("File too large")

# Type validation
if not uploaded_file.name.endswith(('.txt', '.pdf')):
    st.error("Invalid file type")
```

**SQL Injection Prevention**:
```python
# Parameterized queries
cursor.execute("""
    INSERT INTO results (member_id, filename, decision)
    VALUES (?, ?, ?)
""", (member_id, filename, decision))
# Never use string formatting for SQL
```

**Code Injection Prevention**:
- No `eval()` or `exec()` usage
- No dynamic code generation
- Regex patterns are static
- JSON parsing with built-in library

### 10.3 Production Hardening

**For Production Deployment**:
1. Add authentication (OAuth, SAML)
2. Implement role-based access control
3. Enable audit logging
4. Add rate limiting
5. Use HTTPS/TLS
6. Encrypt database at rest
7. Implement data retention policies
8. Add input sanitization
9. Enable CORS restrictions
10. Implement session management

---

## 11. Performance Characteristics

### 11.1 Time Complexity

**Agent Execution**:
```
Extract Agent:       O(n)  where n = chart text length
Gap Match Agent:     O(1)  constant time operations
Discrepancy Agent:   O(n)  where n = chart text length
Decision Agent:      O(m)  where m = number of flags

Total: O(n + m) ≈ O(n) for typical charts
```

**Database Operations**:
```
Insert:              O(1)  single row insert
Get all results:     O(r)  where r = number of results
Get summary:         O(r)  aggregate query
Filter by decision:  O(r)  full table scan (no index)
```

### 11.2 Space Complexity

**Memory Usage**:
```
Chart text:          ~5 KB (typical)
Extracted data:      ~1 KB
Gap report:          ~1 KB
Flags:               ~500 bytes
Database row:        ~2 KB

Total per validation: ~10 KB
```

**Database Growth**:
```
Per record:          ~2 KB
1000 records:        ~2 MB
10,000 records:      ~20 MB
100,000 records:     ~200 MB
```

### 11.3 Performance Benchmarks

**Expected Performance** (on typical hardware):
```
Chart validation:    <1 second
Database insert:     <10 ms
Dashboard load:      <500 ms (1000 records)
Results table:       <1 second (1000 records)
```

**Scalability Limits**:
```
Concurrent users:    1 (demo limitation)
Charts per hour:     ~3600 (1 per second)
Database size:       ~1 GB (500K records)
UI responsiveness:   Degrades after 10K records
```

### 11.4 Optimization Opportunities

**For Production**:
1. Add database indexes on `member_id`, `decision`, `created_at`
2. Implement pagination for results table
3. Cache gap report in memory
4. Use connection pooling for database
5. Implement async processing for batch uploads
6. Add result caching for duplicate charts
7. Optimize regex patterns
8. Use compiled regex objects

---

## 12. Extensibility

### 12.1 Adding New Agents

**Example: Add a "Medication Validation Agent"**

```python
# In agents.py
def run_medication_agent(extracted: dict) -> list:
    """Validate medication data."""
    flags = []
    
    # Check for drug interactions
    meds = extracted.get("medications", [])
    if "Warfarin" in meds and "Aspirin" in meds:
        flags.append({
            "severity": "high",
            "msg": "Potential drug interaction: Warfarin + Aspirin"
        })
    
    return flags

# In app.py, add to pipeline:
with st.status("💊 Medication Agent") as status:
    med_flags = agents.run_medication_agent(extracted)
    flags.extend(med_flags)
    status.update(label="✅ Medication Agent", state="complete")
```

### 12.2 Adding New Scoring Rules

**Example: Add "Lab Recency" rule**

```python
# In agents.py, modify run_gap_match_agent()
def run_gap_match_agent(extracted, gap_row):
    scores = {}
    
    # Existing rules...
    scores["icd_match"] = icd_score
    scores["date_in_window"] = date_score
    scores["provider_npi"] = npi_score
    
    # New rule: Lab recency (weight 0.1)
    lab_dates = re.findall(r"on\s*([\d-]+)", extracted.get("raw_text", ""))
    if lab_dates:
        try:
            ld = date.fromisoformat(lab_dates[0])
            vd = date.fromisoformat(extracted["visit_date"])
            days_old = (vd - ld).days
            lab_score = 1.0 if days_old <= 90 else 0.5
        except:
