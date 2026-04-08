import streamlit as st
import pandas as pd
import pdfplumber
from pathlib import Path
import os
from dotenv import load_dotenv
import db
import agents
from llm_service import LLMAnalytics

# Load environment variables
load_dotenv()

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
tab1, tab2, tab3, tab4 = st.tabs(["📋 Validate", "📊 Results", "📈 Dashboard", "🤖 AI Insights"])

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
                "chart_MBR003.txt",
                "chart_MBR004.txt",
                "chart_MBR005.txt"
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
                
                # Add AI explanation button
                if 'llm_service' in st.session_state:
                    if st.button(f"🤖 AI Explanation", key=f"explain_{result['id']}"):
                        with st.spinner("Generating explanation..."):
                            explanation = st.session_state.llm_service.explain_decision(result)
                            st.info(explanation)
                else:
                    st.caption("💡 Enable AI Insights in Tab 4 to get detailed explanations")

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
    
    # Add AI-powered alerts section
    if 'llm_service' in st.session_state:
        st.subheader("🚨 AI-Detected Alerts")
        st.caption("Automated anomaly detection powered by Groq (Llama 3.1)")
        
        if st.button("🔄 Refresh Alerts"):
            with st.spinner("Analyzing for anomalies..."):
                current = db.get_daily_summary()
                historical = db.get_30day_average()
                alerts_text = st.session_state.llm_service.generate_alerts(current, historical)
                st.markdown(alerts_text)
        
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

# ============================================================================
# TAB 4: AI INSIGHTS
# ============================================================================
with tab4:
    st.header("🤖 AI-Powered Analytics")
    st.caption("Powered by Groq's free tier (Llama 3.3) - Does not affect validation decisions")
    
    # Initialize LLM service from environment variable
    try:
        if 'llm_service' not in st.session_state:
            st.session_state.llm_service = LLMAnalytics()
        llm = st.session_state.llm_service
        st.success("✅ Connected to Groq (Llama 3.3 70B)")
    except Exception as e:
        st.error(f"❌ Failed to connect to Groq: {str(e)}")
        st.info("""
        ### 🔑 How to Set Up Groq API Key:
        
        1. **Get your FREE API key** from [Groq Console](https://console.groq.com)
           - No credit card required
           - 6000 requests/minute free tier
        
        2. **Create a `.env` file** in the `medchart_demo` directory:
        ```
        GROQ_API_KEY=gsk_your_api_key_here
        ```
        
        3. **Restart the application** to load the environment variable
        
        ### 🎯 What You'll Get Once Configured:
        - **📈 Trend Analysis**: Identify patterns in validation history
        - **💬 Natural Language Queries**: Ask questions in plain English
        - **🔍 Root Cause Analysis**: Understand why cases are rejected/flagged
        - **🚨 Automated Alerts**: Proactive notifications about anomalies
        
        ### 🎁 Why Groq?
        - ✅ **100% FREE** - No credit card required
        - ✅ **Fast** - 10x faster than typical APIs
        - ✅ **Generous limits** - 6000 requests/minute
        - ✅ **Llama 3.3 70B** - Latest state-of-the-art model
        """)
        st.stop()
    
    # Create sub-tabs for AI features
    ai_tab1, ai_tab2, ai_tab3 = st.tabs(["💬 Ask Questions", "📈 Trend Analysis", "🔍 Root Cause"])
    
    # Sub-tab 1: Ask Questions
    with ai_tab1:
        st.subheader("💬 Natural Language Queries")
        st.caption("Ask questions about your validation data in plain English")
        
        question = st.text_input(
            "Your question:",
            placeholder="e.g., What's the rejection rate this week? Which member has the most manual reviews?",
            key="nl_query"
        )
        
        if question:
            with st.spinner("🤔 Thinking..."):
                results_df = db.get_all_results()
                if len(results_df) > 0:
                    results_df = pd.DataFrame(results_df)
                    answer = llm.natural_language_query(question, results_df)
                    st.info(answer)
                else:
                    st.warning("⚠️ No validation data available yet. Run some validations first!")
        
        # Show example questions
        with st.expander("💡 Example Questions"):
            st.markdown("""
            - What's the approval rate this month?
            - Which members have the most flags?
            - How many charts were manually reviewed today?
            - What's the average confidence score?
            - Show me the rejection trend over time
            - Which gap types are most common?
            """)
    
    # Sub-tab 2: Trend Analysis
    with ai_tab2:
        st.subheader("📈 Trend Analysis with Charts")
        st.caption("Analyze patterns in validation history with AI insights")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            days = st.slider("Analysis period (days)", 7, 90, 30, key="trend_days")
        with col2:
            analyze_btn = st.button("🔍 Analyze", use_container_width=True, type="primary")
        
        if analyze_btn:
            with st.spinner("📊 Analyzing validation patterns..."):
                results_df = db.get_results_for_analysis(days=days)
                
                if len(results_df) > 0:
                    # Show charts first
                    st.subheader("📊 Visual Trends")
                    
                    # Decision distribution over time
                    df_chart = results_df.copy()
                    df_chart['date'] = pd.to_datetime(df_chart['created_at']).dt.date
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Decision Distribution**")
                        decision_counts = df_chart['decision'].value_counts()
                        st.bar_chart(decision_counts)
                    
                    with col2:
                        st.markdown("**Confidence Score Distribution**")
                        st.line_chart(df_chart.set_index('date')['confidence'])
                    
                    st.divider()
                    
                    # AI Insights
                    st.subheader("🤖 AI Insights")
                    insights = llm.analyze_trends(results_df, days=days)
                    st.markdown(insights)
                else:
                    st.warning(f"⚠️ No data available for the last {days} days")
    
    # Sub-tab 3: Root Cause Analysis
    with ai_tab3:
        st.subheader("🔍 Root Cause Analysis")
        st.caption("Understand why certain patterns occur in your validation data")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            analysis_type = st.selectbox(
                "Select case type to analyze:",
                ["Rejected Cases", "Manual Review Cases", "All Flagged Cases"],
                key="root_cause_type"
            )
        with col2:
            analyze_root_btn = st.button("🔬 Analyze", use_container_width=True, type="primary")
        
        if analyze_root_btn:
            with st.spinner("🔎 Identifying patterns..."):
                all_results = db.get_all_results()
                
                if len(all_results) > 0:
                    all_results_df = pd.DataFrame(all_results)
                    
                    # Filter based on selection
                    if analysis_type == "Rejected Cases":
                        filtered = all_results_df[all_results_df['decision'] == 'rejected']
                        filter_desc = "rejected cases"
                    elif analysis_type == "Manual Review Cases":
                        filtered = all_results_df[all_results_df['decision'] == 'manual_review']
                        filter_desc = "manual review cases"
                    else:
                        filtered = all_results_df[all_results_df['flags'].notna()]
                        filter_desc = "flagged cases"
                    
                    if len(filtered) > 0:
                        # Show summary stats
                        st.metric("Cases Found", len(filtered))
                        
                        # Show flag distribution if available
                        if 'flags' in filtered.columns:
                            st.markdown("**Most Common Flags:**")
                            # Split pipe-separated flags and count individual flags
                            all_flags = []
                            for flag_str in filtered['flags'].dropna():
                                if flag_str and str(flag_str).strip():
                                    # Split by pipe and clean each flag
                                    flags = [f.strip() for f in str(flag_str).split('|')]
                                    all_flags.extend(flags)
                            
                            if all_flags:
                                # Create DataFrame for proper type handling
                                flag_df = pd.DataFrame({'flag': all_flags})
                                flag_counts = flag_df['flag'].value_counts().head(5)
                                st.bar_chart(flag_counts)
                            else:
                                st.info("No flags found in the selected cases")
                        
                        st.divider()
                        
                        # AI Analysis
                        st.subheader("🤖 AI Root Cause Analysis")
                        analysis = llm.root_cause_analysis(filtered)
                        st.markdown(analysis)
                    else:
                        st.warning(f"⚠️ No {filter_desc} found in the database")
                else:
                    st.warning("⚠️ No validation data available yet. Run some validations first!")

# Made with Bob
