# System Architecture: Medical Chart Validation with Gemini Analytics

## 🏗️ High-Level Architecture

```mermaid
graph TB
    subgraph "User Interface - Streamlit"
        TAB1[Tab 1: Validate]
        TAB2[Tab 2: Results]
        TAB3[Tab 3: Dashboard]
        TAB4[Tab 4: AI Insights]
    end
    
    subgraph "Core Validation System - Deterministic"
        EXTRACT[Extract Agent]
        GAPMATCH[Gap Match Agent]
        DISC[Discrepancy Agent]
        DECISION[Decision Agent]
        
        EXTRACT --> GAPMATCH
        GAPMATCH --> DISC
        DISC --> DECISION
    end
    
    subgraph "Data Layer"
        DB[(SQLite Database)]
        CACHE[(Response Cache)]
    end
    
    subgraph "AI Analytics Layer - Optional"
        LLMSVC[LLM Service]
        PROMPTS[Prompt Templates]
        GEMINI[Gemini 1.5 Pro API]
        
        LLMSVC --> PROMPTS
        LLMSVC --> CACHE
        LLMSVC --> GEMINI
    end
    
    TAB1 --> EXTRACT
    DECISION --> DB
    DB --> TAB2
    DB --> TAB3
    DB --> LLMSVC
    LLMSVC --> TAB4
    LLMSVC --> TAB2
    LLMSVC --> TAB3
    
    style TAB1 fill:#e3f2fd
    style TAB2 fill:#e3f2fd
    style TAB3 fill:#e3f2fd
    style TAB4 fill:#fff9c4
    style EXTRACT fill:#c8e6c9
    style GAPMATCH fill:#c8e6c9
    style DISC fill:#c8e6c9
    style DECISION fill:#c8e6c9
    style DB fill:#f3e5f5
    style LLMSVC fill:#ffecb3
    style GEMINI fill:#fff9c4
```

---

## 🔄 Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant Core as Validation Pipeline
    participant DB as Database
    participant LLM as Gemini Service
    participant API as Gemini API
    
    Note over User,API: Standard Validation Flow (No LLM)
    User->>UI: Upload chart + gap report
    UI->>Core: Run validation
    Core->>Core: Extract → Match → Check → Decide
    Core->>DB: Save result
    DB->>UI: Return decision
    UI->>User: Display result
    
    Note over User,API: AI Analytics Flow (Optional)
    User->>UI: Request AI insights
    UI->>LLM: Query with context
    LLM->>LLM: Check cache
    alt Cache hit
        LLM->>UI: Return cached response
    else Cache miss
        LLM->>API: Send prompt
        API->>LLM: Generate response
        LLM->>LLM: Cache response
        LLM->>UI: Return response
    end
    UI->>User: Display insights
```

---

## 📊 Component Interaction Matrix

| Component | Reads From | Writes To | Dependencies |
|-----------|------------|-----------|--------------|
| **Extract Agent** | Chart text | - | regex, datetime |
| **Gap Match Agent** | Extracted data, Gap report | - | datetime |
| **Discrepancy Agent** | Extracted data | - | regex, datetime |
| **Decision Agent** | Gap result, Flags | - | - |
| **Database** | - | SQLite file | sqlite3, pandas |
| **LLM Service** | Database, Cache | Cache | google-generativeai |
| **Prompt Templates** | - | - | - |
| **Streamlit UI** | All components | Database | streamlit |

---

## 🎯 Feature Dependency Map

```mermaid
graph LR
    subgraph "Core Features - Always Available"
        V[Validation]
        R[Results View]
        D[Dashboard]
    end
    
    subgraph "AI Features - Optional"
        T[Trend Analysis]
        N[NL Queries]
        RC[Root Cause]
        E[Explanations]
        A[Alerts]
    end
    
    subgraph "Requirements"
        API[Gemini API Key]
        DATA[Validation Data]
    end
    
    API --> T
    API --> N
    API --> RC
    API --> E
    API --> A
    
    DATA --> T
    DATA --> N
    DATA --> RC
    DATA --> E
    DATA --> A
    
    V --> DATA
    
    style V fill:#c8e6c9
    style R fill:#c8e6c9
    style D fill:#c8e6c9
    style T fill:#fff9c4
    style N fill:#fff9c4
    style RC fill:#fff9c4
    style E fill:#fff9c4
    style A fill:#fff9c4
```

---

## 🔐 Security & Privacy Architecture

```mermaid
graph TB
    subgraph "User Environment"
        USER[User]
        ENV[.env File]
        SESSION[Session State]
    end
    
    subgraph "Application Layer"
        APP[Streamlit App]
        LLM[LLM Service]
    end
    
    subgraph "Data Storage"
        DB[(Local Database)]
        CACHE[(Local Cache)]
    end
    
    subgraph "External Services"
        GEMINI[Gemini API]
    end
    
    USER -->|Enters API Key| SESSION
    ENV -->|Loads API Key| SESSION
    SESSION -->|Provides Key| LLM
    
    APP -->|Reads Data| DB
    DB -->|Member IDs Included| LLM
    LLM -->|Anonymized Summaries| GEMINI
    GEMINI -->|Insights| LLM
    LLM -->|Stores| CACHE
    
    style USER fill:#e3f2fd
    style ENV fill:#fff3e0
    style SESSION fill:#fff3e0
    style DB fill:#f3e5f5
    style CACHE fill:#f3e5f5
    style GEMINI fill:#fff9c4
    
    Note1[API Key never stored permanently]
    Note2[Member IDs kept in prompts]
    Note3[All data stays local except API calls]
```

---

## 💾 Database Schema

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
        text flags
        text reasoning
        datetime created_at
    }
    
    RESULTS ||--o{ ANALYTICS : "analyzed by"
    
    ANALYTICS {
        string cache_key PK
        text prompt
        text response
        datetime timestamp
        int ttl_hours
    }
```

---

## 🚀 Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        DEV[Local Machine]
        DEVDB[(Dev Database)]
        DEVENV[.env.development]
    end
    
    subgraph "Production"
        PROD[Production Server]
        PRODDB[(Prod Database)]
        PRODENV[.env.production]
    end
    
    subgraph "External"
        GEMINI[Gemini API]
    end
    
    DEV --> DEVDB
    DEV --> DEVENV
    DEV --> GEMINI
    
    PROD --> PRODDB
    PROD --> PRODENV
    PROD --> GEMINI
    
    style DEV fill:#e3f2fd
    style PROD fill:#c8e6c9
    style GEMINI fill:#fff9c4
```

---

## 📈 Performance Optimization Strategy

```mermaid
graph LR
    subgraph "Request Flow"
        REQ[User Request]
        CHECK{Cache Hit?}
        CACHE[Return Cached]
        API[Call Gemini API]
        STORE[Store in Cache]
        RESP[Return Response]
    end
    
    REQ --> CHECK
    CHECK -->|Yes| CACHE
    CHECK -->|No| API
    CACHE --> RESP
    API --> STORE
    STORE --> RESP
    
    style CHECK fill:#fff9c4
    style CACHE fill:#c8e6c9
    style API fill:#ffecb3
```

**Cache Strategy:**
- TTL: 24 hours
- Key: MD5 hash of prompt
- Storage: In-memory dictionary
- Invalidation: Automatic on expiry

**Expected Performance:**
- First call: 2-5 seconds
- Cached call: <100ms
- Cache hit rate: >80%

---

## 🔄 Error Handling Flow

```mermaid
graph TB
    START[User Action]
    VALIDATE{Valid Input?}
    APIKEY{API Key Valid?}
    NETWORK{Network OK?}
    QUOTA{Within Quota?}
    SUCCESS[Success]
    
    ERROR1[Show Input Error]
    ERROR2[Show API Key Error]
    ERROR3[Show Network Error]
    ERROR4[Show Quota Error]
    
    START --> VALIDATE
    VALIDATE -->|No| ERROR1
    VALIDATE -->|Yes| APIKEY
    APIKEY -->|No| ERROR2
    APIKEY -->|Yes| NETWORK
    NETWORK -->|No| ERROR3
    NETWORK -->|Yes| QUOTA
    QUOTA -->|No| ERROR4
    QUOTA -->|Yes| SUCCESS
    
    ERROR1 --> START
    ERROR2 --> START
    ERROR3 --> START
    ERROR4 --> START
    
    style SUCCESS fill:#c8e6c9
    style ERROR1 fill:#ffcdd2
    style ERROR2 fill:#ffcdd2
    style ERROR3 fill:#ffcdd2
    style ERROR4 fill:#ffcdd2
```

---

## 📊 Monitoring & Observability

```mermaid
graph TB
    subgraph "Metrics"
        M1[API Calls Count]
        M2[Cache Hit Rate]
        M3[Response Time]
        M4[Error Rate]
    end
    
    subgraph "Logs"
        L1[Request Logs]
        L2[Error Logs]
        L3[Cache Logs]
    end
    
    subgraph "Alerts"
        A1[High Error Rate]
        A2[Low Cache Hit]
        A3[Slow Response]
    end
    
    M1 --> L1
    M2 --> L3
    M3 --> L1
    M4 --> L2
    
    M4 --> A1
    M2 --> A2
    M3 --> A3
    
    style M1 fill:#e3f2fd
    style M2 fill:#e3f2fd
    style M3 fill:#e3f2fd
    style M4 fill:#e3f2fd
```

---

## 🎯 Key Architectural Principles

### 1. **Separation of Concerns**
- Core validation logic is completely independent
- AI layer is a separate, optional module
- Clear boundaries between components

### 2. **Non-Invasive Design**
- AI never modifies validation decisions
- AI features can be disabled without affecting core functionality
- All AI interactions are clearly labeled

### 3. **Performance First**
- Aggressive caching reduces API calls
- Async operations where possible
- Minimal impact on core validation speed

### 4. **Security by Design**
- API keys never stored permanently
- Data stays local except for API calls
- Clear privacy boundaries

### 5. **Fail-Safe Operation**
- Core system works without AI
- Graceful degradation on API failures
- Clear error messages for users

---

## 📝 Implementation Phases

### Phase 1: Foundation ✅
- Set up Gemini SDK
- Create LLM service module
- Implement caching
- Extend database functions

### Phase 2: Core Features ⏳
- Trend analysis
- Natural language queries
- Root cause analysis
- Decision explanations
- Automated alerts

### Phase 3: UI Integration ⏳
- Add Tab 4
- Integrate with existing tabs
- Add API key management
- Polish user experience

### Phase 4: Testing & Docs ⏳
- Comprehensive testing
- User documentation
- Performance optimization
- Security review

---

**This architecture ensures:**
- ✅ Core validation remains deterministic and reliable
- ✅ AI features enhance without interfering
- ✅ System is maintainable and extensible
- ✅ Performance is optimized through caching
- ✅ Security and privacy are maintained