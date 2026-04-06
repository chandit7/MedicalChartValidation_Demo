"""Structured prompt templates for Gemini 1.5 Pro analytics."""

def get_trend_analysis_prompt(summary: dict, flag_counts: list) -> str:
    """Generate prompt for trend analysis."""
    return f"""You are a healthcare analytics expert analyzing medical chart validation data.

**Validation Summary:**
- Total Charts: {summary['total']}
- Approved: {summary['approved']} ({summary['approved']/summary['total']*100:.1f}%)
- Rejected: {summary['rejected']} ({summary['rejected']/summary['total']*100:.1f}%)
- Manual Review: {summary['manual_review']} ({summary['manual_review']/summary['total']*100:.1f}%)
- Average Confidence: {summary['avg_confidence']:.2f}
- Average Gap Score: {summary['avg_gap_score']:.2f}
- Total Flags: {summary['total_flags']}
- Date Range: {summary['date_range']}

**Most Common Flags:**
{chr(10).join([f"{i+1}. {flag} ({count} occurrences)" for i, (flag, count) in enumerate(flag_counts)])}

**Analysis Required:**
1. **Key Trends**: Identify notable patterns in approval/rejection rates
2. **Flag Analysis**: What do the most common flags tell us about data quality?
3. **Performance Insights**: Is the system performing well? Any concerns?
4. **Actionable Recommendations**: Provide 2-3 specific actions to improve outcomes

Format your response with clear sections using markdown headers (##).
Be concise but insightful. Focus on actionable intelligence."""


def get_decision_explanation_prompt(result: dict) -> str:
    """Generate prompt for decision explanation."""
    return f"""You are a medical chart validation expert. Explain this validation decision in clear, professional language.

**Validation Result:**
- Member ID: {result['member_id']}
- Decision: {result['decision'].upper()}
- Confidence Score: {result['confidence']*100:.0f}%
- Gap Score: {result.get('gap_score', 'N/A')}
- Flags: {result.get('disc_count', 0)}
- Flag Details: {result.get('flags', 'None')}
- Reasoning: {result.get('reasoning', 'N/A')}

**Explanation Required:**
Provide a clear, professional explanation suitable for:
1. **Healthcare Provider**: Clinical perspective on why this decision was made
2. **Quality Reviewer**: Compliance and process perspective
3. **Next Steps**: What actions should be taken based on this decision

Keep explanations concise (2-3 sentences each). Use professional medical terminology but remain accessible."""


def get_root_cause_prompt(filtered_results: list, analysis_type: str) -> str:
    """Generate prompt for root cause analysis."""
    # Prepare summary of filtered results
    total = len(filtered_results)
    common_flags = {}
    for result in filtered_results:
        if result.get('flags'):
            for flag in result['flags'].split(' | '):
                common_flags[flag] = common_flags.get(flag, 0) + 1
    
    top_flags = sorted(common_flags.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return f"""You are a healthcare quality analyst investigating {analysis_type.lower()}.

**Analysis Scope:**
- Total Cases: {total}
- Analysis Type: {analysis_type}

**Common Flags in These Cases:**
{chr(10).join([f"- {flag}: {count} cases ({count/total*100:.1f}%)" for flag, count in top_flags])}

**Root Cause Analysis Required:**
1. **Primary Root Causes**: What are the 2-3 main reasons these cases ended up in this category?
2. **Preventable Issues**: Which issues could be prevented with better data quality or processes?
3. **Training Opportunities**: What training or education could reduce these cases?
4. **System Improvements**: What system changes would help?

Provide specific, actionable insights. Focus on root causes, not symptoms."""


def get_nl_query_prompt(question: str, data_summary: dict) -> str:
    """Generate prompt for natural language query."""
    return f"""You are a data analyst for a medical chart validation system. Answer the user's question using the available data.

**User Question:** {question}

**Available Data:**
- Total Records: {data_summary['total_records']}
- Date Range: {data_summary['date_range']}
- Decision Distribution: {data_summary['decision_counts']}
- Available Fields: {', '.join(data_summary['columns'])}

**Sample Data:**
{data_summary['sample_data']}

**Instructions:**
1. Answer the question directly and concisely
2. Use specific numbers and percentages from the data
3. If the data doesn't contain the answer, say so clearly
4. Provide context to make the answer meaningful

Format your response in clear, professional language."""


def get_alerts_prompt(current_summary: dict, historical_summary: dict) -> str:
    """Generate prompt for automated alerts."""
    return f"""You are a healthcare analytics monitoring system. Compare current metrics against historical baseline to identify anomalies.

**Current Metrics (Last 24 Hours):**
- Total: {current_summary.get('total', 0)}
- Approved: {current_summary.get('approved', 0)}
- Rejected: {current_summary.get('rejected', 0)}
- Manual Review: {current_summary.get('manual_review', 0)}

**Historical Baseline (Last 30 Days Average):**
- Total: {historical_summary.get('avg_total', 0):.0f}
- Approved: {historical_summary.get('avg_approved', 0):.0f}
- Rejected: {historical_summary.get('avg_rejected', 0):.0f}
- Manual Review: {historical_summary.get('avg_manual_review', 0):.0f}

**Alert Generation:**
Identify significant deviations (>20% change) and generate alerts using this format:
- 🔴 High severity: Critical issues requiring immediate attention
- 🟡 Medium severity: Notable changes worth investigating
- 🟢 Low severity: Minor observations or positive trends

Provide 2-4 specific alerts. Be concise and actionable."""

# Made with Bob
