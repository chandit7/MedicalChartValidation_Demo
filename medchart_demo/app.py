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

# Made with Bob
