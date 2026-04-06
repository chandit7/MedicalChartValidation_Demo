# 🚀 Groq Free Tier Setup Guide

## Overview

This guide shows how to set up **Groq's free tier** for LLM analytics in the Medical Chart Validation system. Groq provides **FREE access** to Llama 3.1 models with extremely fast inference.

---

## 🎯 Why Groq?

✅ **Completely FREE** - No credit card required  
✅ **Fast inference** - 10x faster than typical APIs  
✅ **Generous limits** - 6000 requests/minute on free tier  
✅ **Llama 3.1 70B** - State-of-the-art open-source model  
✅ **Easy integration** - Drop-in replacement for OpenAI API  

---

## 📝 Step 1: Get Your Free API Key

1. Visit: https://console.groq.com
2. Sign up with email (no credit card needed)
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy your key (starts with `gsk_...`)

---

## 🔧 Step 2: Install Dependencies

```bash
pip install groq
```

Or update your requirements:
```bash
pip install -r requirements.txt
```

---

## 💻 Step 3: Create LLM Service Module

Create `medchart_demo/llm_service.py`:

```python
# llm_service.py
import os
import json
from groq import Groq

class LLMAnalytics:
    """
    LLM-powered analytics using Groq's free tier.
    Provides insights without affecting core validation logic.
    """
    
    def __init__(self, api_key=None, model="llama-3.1-70b-versatile"):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key (or set GROQ_API_KEY env var)
            model: Model to use (default: llama-3.1-70b-versatile)
        
        Available models:
            - llama-3.1-70b-versatile: Best for complex analytics
            - llama-3.1-8b-instant: Faster, lighter tasks
            - mixtral-8x7b-32768: Alternative with large context
        """
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.model = model
        self.cache = {}  # Simple response cache
    
    def generate(self, prompt, max_tokens=500, temperature=0.7):
        """Generate LLM response with caching."""
        # Check cache
        cache_key = f"{prompt[:100]}_{max_tokens}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a healthcare analytics expert analyzing medical chart validation data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            result = response.choices[0].message.content
            
            # Cache result
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            return f"⚠️ Error: {str(e)}\n\nPlease check your API key and internet connection."
    
    def analyze_trends(self, results_df):
        """Analyze validation trends from historical data."""
        summary = {
            'total': len(results_df),
            'approved': len(results_df[results_df['decision'] == 'APPROVED']),
            'rejected': len(results_df[results_df['decision'] == 'REJECTED']),
            'manual_review': len(results_df[results_df['decision'] == 'MANUAL_REVIEW']),
            'avg_confidence': results_df['confidence'].mean(),
            'common_flags': results_df['flags'].value_counts().head(5).to_dict()
        }
        
        prompt = f"""
Analyze these medical chart validation results from the past 30 days:

**Summary Statistics:**
- Total charts: {summary['total']}
- Approved: {summary['approved']} ({summary['approved']/summary['total']*100:.1f}%)
- Rejected: {summary['rejected']} ({summary['rejected']/summary['total']*100:.1f}%)
- Manual Review: {summary['manual_review']} ({summary['manual_review']/summary['total']*100:.1f}%)
- Average confidence: {summary['avg_confidence']:.2f}

**Most Common Flags:**
{json.dumps(summary['common_flags'], indent=2)}

Provide:
1. **Key Trends**: What patterns do you see?
2. **Potential Issues**: Any concerning trends?
3. **Recommendations**: 3 actionable improvements
4. **Predictions**: What might happen next month?

Format as markdown with clear sections.
"""
        return self.generate(prompt, max_tokens=800)
    
    def explain_decision(self, result):
        """Generate human-friendly explanation of a validation decision."""
        prompt = f"""
Explain this medical chart validation decision in simple terms:

**Chart Details:**
- Member ID: {result.get('member_id', 'N/A')}
- Decision: {result['decision']}
- Confidence Score: {result['confidence']:.2f}
- Flags: {result.get('flags', 'None')}
- Reasoning: {result.get('reasoning', 'N/A')}

Provide 3 explanations for different audiences:

1. **For Healthcare Provider** (clinical perspective)
2. **For Quality Reviewer** (compliance perspective)  
3. **For Member Services** (patient-friendly language)

Keep each explanation to 2-3 sentences.
"""
        return self.generate(prompt, max_tokens=600)
    
    def root_cause_analysis(self, filtered_results):
        """Identify root causes for specific decision patterns."""
        if len(filtered_results) == 0:
            return "No results to analyze."
        
        # Summarize the filtered results
        summary = {
            'count': len(filtered_results),
            'common_flags': filtered_results['flags'].value_counts().head(5).to_dict(),
            'avg_confidence': filtered_results['confidence'].mean(),
            'decision_breakdown': filtered_results['decision'].value_counts().to_dict()
        }
        
        prompt = f"""
Perform root cause analysis on these {summary['count']} flagged/rejected charts:

**Common Flags:**
{json.dumps(summary['common_flags'], indent=2)}

**Decision Breakdown:**
{json.dumps(summary['decision_breakdown'], indent=2)}

**Average Confidence:** {summary['avg_confidence']:.2f}

Identify:
1. **Root Causes**: Why are these charts being flagged?
2. **Preventable Issues**: What could be fixed upstream?
3. **Data Quality**: Any data entry problems?
4. **Training Needs**: What staff training would help?

Provide specific, actionable insights.
"""
        return self.generate(prompt, max_tokens=700)
    
    def natural_language_query(self, question, results_df):
        """Answer questions about validation data in natural language."""
        # Get basic stats
        stats = {
            'total': len(results_df),
            'decisions': results_df['decision'].value_counts().to_dict(),
            'avg_confidence': results_df['confidence'].mean(),
            'date_range': f"{results_df['created_at'].min()} to {results_df['created_at'].max()}"
        }
        
        prompt = f"""
Answer this question about medical chart validation data:

**Question:** {question}

**Available Data:**
- Total records: {stats['total']}
- Date range: {stats['date_range']}
- Decisions: {json.dumps(stats['decisions'], indent=2)}
- Average confidence: {stats['avg_confidence']:.2f}

Provide a clear, concise answer with specific numbers where applicable.
"""
        return self.generate(prompt, max_tokens=400)
    
    def generate_alerts(self, current_summary, historical_summary):
        """Compare current vs historical metrics to find anomalies."""
        prompt = f"""
Compare current validation metrics against historical baseline:

**Current (Last 24 hours):**
{json.dumps(current_summary, indent=2)}

**Historical Baseline (Last 30 days):**
{json.dumps(historical_summary, indent=2)}

Identify:
1. **Critical Alerts** (>50% deviation)
2. **Warnings** (20-50% deviation)
3. **Insights** (emerging patterns)

For each alert, provide:
- Severity (🔴 Critical / 🟡 Warning / 🔵 Info)
- Description
- Recommended action

Format as a bulleted list.
"""
        return self.generate(prompt, max_tokens=600)
```

---

## 🎨 Step 4: Update Streamlit App

Add to your `app.py`:

```python
import streamlit as st
from llm_service import LLMAnalytics

# In your tabs section, add Tab 4
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Validate", 
    "📊 Results", 
    "📈 Dashboard",
    "🤖 AI Insights"  # NEW
])

with tab4:
    st.header("🤖 AI-Powered Analytics")
    st.caption("Powered by Groq's free tier (Llama 3.1) - Does not affect validation decisions")
    
    # API Key input
    col1, col2 = st.columns([3, 1])
    with col1:
        api_key = st.text_input(
            "Groq API Key (Free)", 
            type="password",
            help="Get your free key at https://console.groq.com"
        )
    with col2:
        st.markdown("[Get Free Key →](https://console.groq.com)")
    
    if not api_key:
        st.info("👆 Enter your free Groq API key above to unlock AI insights")
        st.markdown("""
        ### 🎁 Why Groq?
        - ✅ **100% FREE** - No credit card required
        - ✅ **Fast** - 10x faster than typical APIs
        - ✅ **Generous limits** - 6000 requests/minute
        - ✅ **Llama 3.1 70B** - State-of-the-art model
        """)
        st.stop()
    
    # Initialize LLM service
    try:
        llm = LLMAnalytics(api_key=api_key)
        st.success("✅ Connected to Groq")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")
        st.stop()
    
    # Trend Analysis Section
    st.subheader("📈 Trend Analysis")
    if st.button("🔍 Analyze Trends", use_container_width=True):
        with st.spinner("Analyzing validation patterns..."):
            results_df = db.get_results_for_analysis(days=30)
            if len(results_df) > 0:
                insights = llm.analyze_trends(results_df)
                st.markdown(insights)
            else:
                st.warning("No data available for analysis")
    
    st.divider()
    
    # Natural Language Query Section
    st.subheader("💬 Ask Questions")
    question = st.text_input("Ask about your validation data:", 
                            placeholder="e.g., What's the rejection rate this week?")
    if question:
        with st.spinner("Thinking..."):
            results_df = db.get_all_results()
            answer = llm.natural_language_query(question, results_df)
            st.info(answer)
    
    st.divider()
    
    # Root Cause Analysis Section
    st.subheader("🔍 Root Cause Analysis")
    analysis_type = st.selectbox(
        "Analyze:",
        ["Rejected Cases", "Manual Review Cases", "All Flagged Cases"]
    )
    if st.button("🔬 Analyze Root Causes", use_container_width=True):
        with st.spinner("Identifying patterns..."):
            # Filter results based on selection
            all_results = db.get_all_results()
            if analysis_type == "Rejected Cases":
                filtered = all_results[all_results['decision'] == 'REJECTED']
            elif analysis_type == "Manual Review Cases":
                filtered = all_results[all_results['decision'] == 'MANUAL_REVIEW']
            else:
                filtered = all_results[all_results['flags'].notna()]
            
            if len(filtered) > 0:
                analysis = llm.root_cause_analysis(filtered)
                st.markdown(analysis)
            else:
                st.warning(f"No {analysis_type.lower()} found")
```

---

## 🔐 Step 5: Set Environment Variable (Optional)

Instead of entering the API key each time, set it as an environment variable:

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY="gsk_your_key_here"
```

**Windows (Command Prompt):**
```cmd
set GROQ_API_KEY=gsk_your_key_here
```

**Linux/Mac:**
```bash
export GROQ_API_KEY="gsk_your_key_here"
```

**Permanent (add to .env file):**
```bash
GROQ_API_KEY=gsk_your_key_here
```

---

## 📊 Usage Examples

### Example 1: Trend Analysis
```python
llm = LLMAnalytics(api_key="gsk_...")
results_df = pd.read_csv("validation_results.csv")
insights = llm.analyze_trends(results_df)
print(insights)
```

### Example 2: Explain Decision
```python
result = {
    'member_id': 'MBR001',
    'decision': 'MANUAL_REVIEW',
    'confidence': 0.77,
    'flags': 'Lab date 631 days old',
    'reasoning': 'High severity flag detected'
}
explanation = llm.explain_decision(result)
print(explanation)
```

### Example 3: Natural Language Query
```python
answer = llm.natural_language_query(
    "What percentage of charts were approved this month?",
    results_df
)
print(answer)
```

---

## 🎯 Free Tier Limits

| Feature | Free Tier |
|---------|-----------|
| Requests/minute | 6,000 |
| Requests/day | 14,400 |
| Tokens/minute | 30,000 |
| Models | Llama 3.1 (8B, 70B), Mixtral |
| Cost | **$0** |

---

## 🔒 Privacy & Security

⚠️ **Important Considerations:**

1. **Data Privacy**: Groq is a cloud service - data is sent to external servers
2. **PHI Handling**: Remove Protected Health Information before sending
3. **Anonymization**: Replace member IDs with generic identifiers
4. **Compliance**: Ensure HIPAA compliance if handling real patient data

**For Maximum Privacy:** Use Ollama (local) instead:
```bash
# Install Ollama
ollama pull llama3.1

# Use local endpoint
llm = LLMAnalytics(base_url="http://localhost:11434")
```

---

## 🐛 Troubleshooting

### Error: "Invalid API key"
- Check your key starts with `gsk_`
- Verify at https://console.groq.com/keys
- Ensure no extra spaces

### Error: "Rate limit exceeded"
- Free tier: 6000 req/min (very generous)
- Implement caching (already included in code)
- Wait a minute and retry

### Error: "Model not found"
- Use: `llama-3.1-70b-versatile` (default)
- Or: `llama-3.1-8b-instant`
- Or: `mixtral-8x7b-32768`

---

## 📚 Additional Resources

- **Groq Console**: https://console.groq.com
- **API Documentation**: https://console.groq.com/docs
- **Model Comparison**: https://console.groq.com/docs/models
- **Python SDK**: https://github.com/groq/groq-python

---

## ✅ Quick Start Checklist

- [ ] Sign up at https://console.groq.com
- [ ] Get free API key
- [ ] Install: `pip install groq`
- [ ] Create `llm_service.py`
- [ ] Update `app.py` with Tab 4
- [ ] Test with sample data
- [ ] Set environment variable (optional)
- [ ] Review privacy considerations

---

**🎉 You're all set! Enjoy FREE AI-powered analytics with Groq!**