import streamlit as st
import pandas as pd
import utils

def generate_analysis_report(kpis, insights, ml_results, forecast):
    report = "# Zero Click Analytics - Executive Report\n\n"
    if kpis:
        report += "## Key Performance Indicators\n"
        for name, val, delta in kpis:
            report += f"- **{name}**: {val} (Trend: {delta})\n"
        report += "\n"
    if insights:
        report += "## AI Insights\n"
        report += f"{insights}\n\n"
    if ml_results:
        report += "## Machine Learning Opportunities\n"
        for res in ml_results:
            report += f"- **{res['title']}**: {res['metric_name']} = {res['metric_value']} ({res['extra']})\n"
        report += "\n"
    if forecast:
        report += "## Time Series Forecasting\n"
        report += "A forecasting model was successfully generated and applied to predict upcoming trends.\n"
    return report

def render_dashboard(df, cleaned_df, kpis, charts, ml_results, forecast, insights, chat_callback):
    """
    Main dashboard layout.
    """
    st.markdown('''
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        .stApp {
            background-color: #f8f9fa;
            font-family: 'Inter', sans-serif;
            color: #212529;
        }
        
        /* Hide Default Streamlit Clutter for Premium Look */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        p, div, span, h1, h2, h3, h4 {
            font-family: 'Inter', sans-serif;
        }
        
        /* Premium Sidebar */
        [data-testid="stSidebar"] {
            background-color: #121217;
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h3 {
            color: #adb5bd;
            font-size: 15px;
        }
        
        /* Elegant KPI Metrics Typography */
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(0,0,0,0.04);
            box-shadow: 0 4px 16px rgba(0,0,0,0.05);
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 24px rgba(115, 103, 240, 0.15);
            border-color: rgba(115, 103, 240, 0.3);
        }
        div[data-testid="stMetricValue"] {
            font-size: 38px;
            font-weight: 800;
            color: #1e1e24;
            letter-spacing: -1px;
            line-height: 1.2;
            margin-top: 5px;
        }
        div[data-testid="stMetricLabel"] p {
            font-size: 15px !important;
            font-weight: 800 !important;
            color: #7367f0 !important;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 5px;
        }
        div[data-testid="stMetricDelta"] {
            font-size: 15px;
            font-weight: 600;
            margin-top: 5px;
        }
        
        /* Sophisticated Glass/Soft Shadow Cards */
        [data-testid="column"] {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(0,0,0,0.03);
            box-shadow: 0 4px 16px rgba(0,0,0,0.02);
            transition: all 0.3s ease;
            margin-bottom: 24px;
        }
        [data-testid="column"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 24px rgba(0,0,0,0.06);
            border: 1px solid rgba(115, 103, 240, 0.2);
        }
        
        /* Sleeker Expanders */
        .streamlit-expanderHeader {
            background-color: #ffffff;
            border-radius: 12px;
            border: 1px solid rgba(0,0,0,0.03) !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.02);
            font-weight: 600;
            font-size: 16px;
            color: #212529;
            padding: 1rem;
        }
        
        /* Refined Tabs */
        button[data-baseweb="tab"] {
            font-size: 15px;
            font-weight: 600;
            color: #6c757d;
            padding-bottom: 12px;
            margin-right: 24px;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #7367f0 !important;
        }
        
        /* Floating Popover Chat styling */
        div[data-testid="stPopover"] {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 1000;
        }
        div[data-testid="stPopover"] button {
            border-radius: 50%;
            width: 72px;
            height: 72px;
            background: linear-gradient(135deg, #7367f0 0%, #a59bfa 100%);
            color: white;
            font-size: 32px;
            box-shadow: 0 8px 24px rgba(115, 103, 240, 0.4);
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s cubic-bezier(0.68, -0.55, 0.27, 1.55);
        }
        div[data-testid="stPopover"] button:hover {
            transform: scale(1.1);
            box-shadow: 0 12px 32px rgba(115, 103, 240, 0.5);
        }
        
        /* Spacing */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 4rem;
        }
        </style>
    ''', unsafe_allow_html=True)
    
    # 1. KPIs Layer
    if kpis:
        st.markdown("### 📈 Key Metrics")
        # Display all KPIs in a 4-column grid
        num_kpis = len(kpis)
        for i in range(0, num_kpis, 4):
            cols = st.columns(4)
            for j in range(4):
                if i + j < num_kpis:
                    name, val, delta = kpis[i + j]
                    with cols[j]:
                        st.metric(label=name, value=val, delta=delta)
                
    st.markdown("<br>", unsafe_allow_html=True)

    # Generate report text once
    report_text = generate_analysis_report(kpis, insights, ml_results, forecast)

    # 2. Top-level Dashboard Controls
    st.markdown("### 📋 Automated Analysis Dashboard")
    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Tabs
    t_analysis, t_ml, t_forecast = st.tabs(["📊 Executive Analysis", "🤖 Artificial Intelligence & ML", "🔮 Time Series Forecast"])

    # --- Analysis Tab ---
    with t_analysis:
        with st.expander("📝 Comprehensive Analysis Summary", expanded=False):
            st.markdown(report_text)
            
        with st.expander("💡 AI-Generated Business Insights", expanded=True):
            if insights:
                st.info(insights)
            else:
                st.write("No AI insights generated yet. (Ensure GEMINI_API_KEY is configured).")
                
        with st.expander("📉 Automated Visualizations", expanded=True):
            if charts:
                for i in range(0, len(charts), 2):
                    c1, c2 = st.columns(2)
                    with c1:
                        if i < len(charts):
                            st.plotly_chart(charts[i][1], use_container_width=True)
                    with c2:
                        if i+1 < len(charts):
                            st.plotly_chart(charts[i+1][1], use_container_width=True)
            else:
                st.write("No appropriate charts could be generated.")

    # --- ML Tab ---
    with t_ml:
        with st.expander("⚙️ Auto-Discovered Machine Learning Models", expanded=True):
            if not ml_results:
                st.info("No suitable ML opportunities found (e.g., insufficient numeric columns or rows).")
            else:
                for res in ml_results:
                    st.subheader(res['title'])
                    st.markdown(f"**{res['metric_name']}**: `{res['metric_value']}`")
                    st.caption(res['extra'])
                    if res['figure']:
                        st.plotly_chart(res['figure'], use_container_width=True)
                    st.divider()

    # --- Forecast Tab ---
    with t_forecast:
        with st.expander("📅 Prophet Forecasting Analysis", expanded=True):
            if forecast is None:
                st.info("No viable time series data detected for forecasting (requires a Date column and a Numeric format, with >=12 rows).")
            else:
                fig, f_df = forecast['figure'], forecast['forecast_df']
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**Predicted Data (Next Periods)**")
                st.dataframe(f_df, use_container_width=True)

    # --- Floating Chatbot ---
    with st.popover("💬", help="AI Data Assistant"):
        st.markdown("<h4 style='margin-bottom: 0px; color: #7367f0;'>🤖 Data Assistant</h4>", unsafe_allow_html=True)
        st.caption("Ask questions about patterns, averages, or request visualizations.")
        
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
            
        chat_container = st.container(height=350)
        with chat_container:
            for msg in st.session_state.chat_history:
                role = "user" if msg["is_user"] else "assistant"
                with st.chat_message(role):
                    st.write(msg["text"])
                    if "code" in msg and msg["code"]:
                        try:
                            import plotly.express as px
                            local_vars = {"df": cleaned_df, "px": px, "pd": pd}
                            exec(msg["code"], globals(), local_vars)
                            if "fig" in local_vars:
                                st.plotly_chart(local_vars["fig"], use_container_width=True)
                            else:
                                st.error("No figure named 'fig' was generated.")
                        except Exception as e:
                            st.error(f"Visualization generation failed: {e}")

        # Basic text input fallback since chat_input isn't supported inside popovers sometimes
        with st.form("chat_form", clear_on_submit=True):
            cols = st.columns([4, 1])
            with cols[0]:
                prompt = st.text_input("Ask a question:", label_visibility="collapsed", placeholder="E.g., Which region has highest sales?")
            with cols[1]:
                submit_chat = st.form_submit_button("Send")
                
        if submit_chat and prompt:
            st.session_state.chat_history.append({"text": prompt, "is_user": True})
            
            with st.spinner("Analyzing..."):
                resp = chat_callback(prompt)
                
            if isinstance(resp, dict):
                st.session_state.chat_history.append({"text": resp["text"], "is_user": False, "code": resp.get("code")})
            else:
                st.session_state.chat_history.append({"text": str(resp), "is_user": False})
            st.rerun()

    # Sidebar Download options
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Export Capabilities")
    
    # Download Analysis Report
    report_text = generate_analysis_report(kpis, insights, ml_results, forecast)
    pdf_bytes = utils.markdown_to_pdf_bytes(report_text)
    st.sidebar.download_button(
        label="📄 Download Executive Report (PDF)",
        data=pdf_bytes,
        file_name="executive_summary.pdf",
        mime="application/pdf",
        key='download-report',
        use_container_width=True # Make button full width in sidebar
    )
    
    # Download Cleaned Data
    csv = cleaned_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📊 Download Cleaned Data",
        data=csv,
        file_name="cleaned_data.csv",
        mime="text/csv",
        key='download-csv',
        use_container_width=True
    )

