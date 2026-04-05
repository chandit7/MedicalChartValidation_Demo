# Medical Chart Validation System - Flow Diagram

## System Architecture

```mermaid
graph TB
    subgraph "User Interface (Streamlit)"
        UI[User Interface]
        TAB1[Tab 1: Validate]
        TAB2[Tab 2: Results]
        TAB3[Tab 3: Dashboard]
    end
    
    subgraph "Data Sources"
        CHART[Medical Chart<br/>TXT or PDF]
        GAP[Gap Report<br/>CSV]
    end
    
    subgraph "Agent Pipeline"
        A1[Agent 1: Extract<br/>Parse chart data]
        A2[Agent 2: Gap Match<br/>Calculate score]
        A3[Agent 3: Discrepancy<br/>Detect anomalies]
        A4[Agent 4: Decision<br/>Route chart]
    end
    
    subgraph "Database Layer"
        DB[(SQLite DB<br/>medchart.db)]
    end
    
    subgraph "Decision Outcomes"
        APPROVED[✅ Approved<br/>Score ≥ 0.85]
        REJECTED[❌ Rejected<br/>Score ≤ 0.40]
        MANUAL[⚠️ Manual Review<br/>0.40 < Score < 0.85]
    end
    
    UI --> TAB1
    UI --> TAB2
    UI --> TAB3
    
    TAB1 --> CHART
    TAB1 --> GAP
    
    CHART --> A1
    GAP --> A2
    
    A1 -->|Extracted Data| A2
    A1 -->|Extracted Data| A3
    
    A2 -->|Gap Score| A4
    A3 -->|Flags| A4
    A1 -->|Extracted Data| A4
    
    A4 --> APPROVED
    A4 --> REJECTED
    A4 --> MANUAL
    
    APPROVED --> DB
    REJECTED --> DB
    MANUAL --> DB
    
    DB --> TAB2
    DB --> TAB3
    
    style A1 fill:#e1f5ff
    style A2 fill:#e1f5ff
    style A3 fill:#e1f5ff
    style A4 fill:#e1f5ff
    style APPROVED fill:#c8e6c9
    style REJECTED fill:#ffcdd2
    style MANUAL fill:#fff9c4
    style DB fill:#f3e5f5
```

## Detailed Validation Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant A1 as Extract Agent
    participant A2 as Gap Match Agent
    participant A3 as Discrepancy Agent
    participant A4 as Decision Agent
    participant DB as Database
    
    User->>UI: Upload Chart + Gap Report
    User->>UI: Click "Run Validation"
    
    UI->>A1: Send chart text
    activate A1
    A1->>A1: Extract using regex:<br/>- Member ID<br/>- Visit Date<br/>- Provider NPI<br/>- ICD Codes<br/>- HbA1c
    A1-->>UI: Return extracted data
    deactivate A1
    
    UI->>A2: Send extracted data + gap row
    activate A2
    A2->>A2: Calculate scores:<br/>- ICD match (50%)<br/>- Date in window (40%)<br/>- NPI present (10%)
    A2->>A2: Composite = Σ(score × weight)
    A2-->>UI: Return gap score
    deactivate A2
    
    UI->>A3: Send extracted data
    activate A3
    A3->>A3: Check for:<br/>- Invalid HbA1c<br/>- Date gaps<br/>- Unknown codes<br/>- Missing fields
    A3-->>UI: Return flags list
    deactivate A3
    
    UI->>A4: Send gap score + flags + data
    activate A4
    A4->>A4: Apply penalties:<br/>- High: -0.20<br/>- Medium: -0.10<br/>- Low: -0.03
    A4->>A4: Check hard rules:<br/>1. Missing Member ID?<br/>2. High severity flags?<br/>3. No ICD match?
    A4->>A4: Apply thresholds:<br/>≥0.85 → Approved<br/>≤0.40 → Rejected<br/>Else → Manual Review
    A4-->>UI: Return decision
    deactivate A4
    
    UI->>DB: Save result
    DB-->>UI: Confirm saved
    UI->>User: Display decision
```

## Agent Logic Details

```mermaid
flowchart TD
    START([Start Validation])
    
    subgraph "Agent 1: Extract"
        E1[Parse chart text]
        E2{All fields<br/>found?}
        E3[Extract:<br/>Member ID, Date,<br/>NPI, ICD codes,<br/>HbA1c]
        E4[Mark missing fields]
    end
    
    subgraph "Agent 2: Gap Match"
        G1[Load gap requirements]
        G2[Check ICD match<br/>Weight: 0.5]
        G3[Check date in window<br/>Weight: 0.4]
        G4[Check NPI present<br/>Weight: 0.1]
        G5[Calculate composite<br/>score]
    end
    
    subgraph "Agent 3: Discrepancy"
        D1{HbA1c > 15<br/>or < 2?}
        D2{Lab date<br/>> 365 days?}
        D3{Unknown<br/>ICD codes?}
        D4{Missing<br/>Member ID?}
        D5[Add HIGH flag]
        D6[Add MEDIUM flag]
        D7[Add LOW flag]
    end
    
    subgraph "Agent 4: Decision"
        DC1[Base score = composite]
        DC2[Apply penalties]
        DC3{Missing<br/>Member ID?}
        DC4{High severity<br/>flags > 0?}
        DC5{ICD match<br/>= 0?}
        DC6{Score<br/>≥ 0.85?}
        DC7{Score<br/>≤ 0.40?}
        
        R1[REJECTED]
        R2[MANUAL REVIEW]
        R3[APPROVED]
    end
    
    START --> E1
    E1 --> E2
    E2 -->|Yes| E3
    E2 -->|No| E4
    E3 --> G1
    E4 --> G1
    
    G1 --> G2
    G2 --> G3
    G3 --> G4
    G4 --> G5
    
    G5 --> D1
    D1 -->|Yes| D5
    D1 -->|No| D2
    D2 -->|Yes| D5
    D2 -->|No| D3
    D3 -->|Yes| D7
    D3 -->|No| D4
    D4 -->|Yes| D5
    D5 --> DC1
    D6 --> DC1
    D7 --> DC1
    D4 -->|No| DC1
    
    DC1 --> DC2
    DC2 --> DC3
    DC3 -->|Yes| R1
    DC3 -->|No| DC4
    DC4 -->|Yes| R2
    DC4 -->|No| DC5
    DC5 -->|Yes| R1
    DC5 -->|No| DC6
    DC6 -->|Yes| R3
    DC6 -->|No| DC7
    DC7 -->|Yes| R1
    DC7 -->|No| R2
    
    R1 --> SAVE[(Save to DB)]
    R2 --> SAVE
    R3 --> SAVE
    
    style E3 fill:#e1f5ff
    style G5 fill:#e1f5ff
    style D5 fill:#ffcdd2
    style D6 fill:#fff9c4
    style D7 fill:#e8f5e9
    style R1 fill:#ffcdd2
    style R2 fill:#fff9c4
    style R3 fill:#c8e6c9
```

## Scoring System

```mermaid
graph LR
    subgraph "Base Score Calculation"
        ICD[ICD Match<br/>Weight: 0.5]
        DATE[Date in Window<br/>Weight: 0.4]
        NPI[NPI Present<br/>Weight: 0.1]
        BASE[Base Score<br/>= Σ weights]
    end
    
    subgraph "Penalty System"
        HIGH[High Severity<br/>-0.20 each]
        MED[Medium Severity<br/>-0.10 each]
        LOW[Low Severity<br/>-0.03 each]
        PENALTY[Total Penalty]
    end
    
    subgraph "Final Score"
        FINAL[Final Score<br/>= Base - Penalty<br/>Range: 0.0 - 1.0]
    end
    
    ICD --> BASE
    DATE --> BASE
    NPI --> BASE
    
    HIGH --> PENALTY
    MED --> PENALTY
    LOW --> PENALTY
    
    BASE --> FINAL
    PENALTY --> FINAL
    
    style BASE fill:#e1f5ff
    style PENALTY fill:#ffcdd2
    style FINAL fill:#c8e6c9
```

## Decision Thresholds

```mermaid
graph TD
    SCORE[Final Score]
    
    SCORE -->|≥ 0.85| APPROVED[✅ APPROVED<br/>Auto-process]
    SCORE -->|0.40 - 0.85| MANUAL[⚠️ MANUAL REVIEW<br/>Human review needed]
    SCORE -->|≤ 0.40| REJECTED[❌ REJECTED<br/>Do not process]
    
    OVERRIDE1{Hard Override:<br/>Missing Member ID?}
    OVERRIDE2{Hard Override:<br/>High Severity Flags?}
    OVERRIDE3{Hard Override:<br/>No ICD Match?}
    
    OVERRIDE1 -->|Yes| REJECTED
    OVERRIDE2 -->|Yes| MANUAL
    OVERRIDE3 -->|Yes| REJECTED
    
    style APPROVED fill:#c8e6c9
    style MANUAL fill:#fff9c4
    style REJECTED fill:#ffcdd2
    style OVERRIDE1 fill:#ffebee
    style OVERRIDE2 fill:#ffebee
    style OVERRIDE3 fill:#ffebee
```

## Example: MBR001 Validation Flow

```mermaid
graph TD
    START([MBR001 Chart])
    
    E[Extract Agent:<br/>✓ Member ID: MBR001<br/>✓ Date: 2024-09-15<br/>✓ NPI: 1234567890<br/>✓ ICD: Z00.00, Z23<br/>✓ HbA1c: 6.8]
    
    G[Gap Match Agent:<br/>✓ ICD match: 1.0 × 0.5 = 0.5<br/>✓ Date in window: 1.0 × 0.4 = 0.4<br/>✓ NPI present: 1.0 × 0.1 = 0.1<br/>Composite: 1.0]
    
    D[Discrepancy Agent:<br/>✓ HbA1c valid: 6.8<br/>✓ Lab date: same day<br/>✓ All codes known<br/>✓ Member ID present<br/>Flags: 0]
    
    DC[Decision Agent:<br/>Base: 1.0<br/>Penalty: 0.0<br/>Final: 1.0<br/>No overrides triggered]
    
    RESULT[✅ APPROVED<br/>Confidence: 100%]
    
    START --> E
    E --> G
    E --> D
    G --> DC
    D --> DC
    DC --> RESULT
    
    style E fill:#e1f5ff
    style G fill:#e1f5ff
    style D fill:#e1f5ff
    style DC fill:#e1f5ff
    style RESULT fill:#c8e6c9
```

## Database Schema

```mermaid
erDiagram
    RESULTS {
        int id PK
        string member_id
        string filename
        string decision
        float confidence
        float gap_score
        int disc_count
        string flags
        string reasoning
        datetime created_at
    }
    
    RESULTS ||--o{ DECISIONS : has
    
    DECISIONS {
        string approved
        string rejected
        string manual_review
    }
```

## Key Features

### ✅ Zero-LLM Design
- All decisions made by deterministic algorithms
- No AI/ML models involved
- 100% explainable and auditable

### 🎯 4-Agent Pipeline
1. **Extract Agent**: Regex-based data extraction
2. **Gap Match Agent**: Weighted scoring system
3. **Discrepancy Agent**: Rule-based anomaly detection
4. **Decision Agent**: Threshold-based routing with overrides

### 📊 Scoring Weights
- ICD Code Match: 50%
- Date in Window: 40%
- Provider NPI: 10%

### 🚨 Severity Levels
- **High**: -0.20 penalty (triggers manual review)
- **Medium**: -0.10 penalty
- **Low**: -0.03 penalty

### 🎚️ Decision Thresholds
- **Approved**: Score ≥ 0.85
- **Manual Review**: 0.40 < Score < 0.85
- **Rejected**: Score ≤ 0.40

### 🔒 Hard Override Rules (Priority Order)
1. Missing Member ID → REJECTED
2. High Severity Flags → MANUAL REVIEW
3. No ICD Match → REJECTED