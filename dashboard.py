"""
MODULE 4 — Visualization & Dashboard System
Genesis AI Chatbot — Company Data Analysis Platform

Advanced Features:
  1. Advanced Data Visualization Layer
  2. Interactive Dashboard Builder
  3. Real-Time Dashboard Refresh
  4. Automated Report Generator (with AI narrative)

Integrates outputs from:
  - Module 1 (data_quality, dataset_profiling, file_upload)  → session_state["uploaded_df"]
  - Module 2 (nlp_processor, data_processor, response_generator) → generate_suggestions, process_query, execute_query
  - Module 3 (RetailDataAnalyzer, SalesPredictiveEngine, generate_ai_insights, generate_smart_recommendations)

Author   : NK (Team Lead) + Yusuf, Naheen
Module   : 4 — Dashboard & Visualization
Phase    : 2 (Advanced Features)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import time
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────
# SAFE IMPORTS FROM OTHER MODULES
# (wrapped so dashboard still runs even if a module is missing)
# ─────────────────────────────────────────────────────────────

def _try_import_module2():
    try:
        import sys, os
        sys.path.append(os.path.join(os.path.dirname(__file__), "nlp"))
        from nlp_processor import process_query
        from data_processor import execute_query
        from response_generator import generate_response
        # generate_suggestions lives in Module 2's app.py — we replicate
        # the logic here so we don't depend on that app's entry point
        return process_query, execute_query, generate_response
    except Exception:
        return None, None, None

def _try_import_module3():
    try:
        import sys, os
        sys.path.append(os.path.join(os.path.dirname(__file__), "analytics"))
        from analysis import RetailDataAnalyzer
        from insights import generate_ai_insights
        from my_recommendations import generate_smart_recommendations
        from predictive_engine import SalesPredictiveEngine
        return RetailDataAnalyzer, generate_ai_insights, generate_smart_recommendations, SalesPredictiveEngine
    except Exception:
        return None, None, None, None

process_query, execute_query, generate_response = _try_import_module2()
RetailDataAnalyzer, generate_ai_insights, generate_smart_recommendations, SalesPredictiveEngine = _try_import_module3()

# ─────────────────────────────────────────────────────────────
# THEME & CSS
# ─────────────────────────────────────────────────────────────

THEME = {
    "primary"    : "#7C3AED",
    "secondary"  : "#A855F7",
    "accent"     : "#C084FC",
    "bg_dark"    : "#0E1117",
    "bg_card"    : "#1A1D24",
    "bg_sidebar" : "#12151B",
    "text_main"  : "#E2E8F0",
    "text_muted" : "#94A3B8",
    "success"    : "#22C55E",
    "warning"    : "#F59E0B",
    "danger"     : "#EF4444",
    "info"       : "#3B82F6",
}

def apply_dashboard_css():
    st.markdown(f"""
    <style>
    /* ── Global ─────────────────────────────── */
    .stApp {{ background-color: {THEME['bg_dark']} !important; }}
    p, div, span, label {{ color: {THEME['text_main']}; }}
    h1, h2, h3 {{ color: {THEME['secondary']} !important; }}

    /* ── Sidebar ─────────────────────────────── */
    [data-testid="stSidebar"] {{ background-color: {THEME['bg_sidebar']} !important; }}
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{ color: {THEME['accent']} !important; }}
    [data-testid="stMetricValue"] {{ color: {THEME['secondary']} !important; }}

    /* ── KPI Card ────────────────────────────── */
    .kpi-card {{
        background: linear-gradient(135deg, {THEME['bg_card']}, #1e2130);
        border: 1px solid {THEME['primary']}44;
        border-left: 4px solid {THEME['primary']};
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 4px 20px rgba(124,58,237,0.15);
        transition: transform 0.2s ease;
    }}
    .kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 28px rgba(124,58,237,0.25); }}
    .kpi-label {{ font-size: 0.78rem; color: {THEME['text_muted']}; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.35rem; }}
    .kpi-value {{ font-size: 1.9rem; font-weight: 800; color: {THEME['secondary']}; line-height: 1; }}
    .kpi-delta-pos {{ font-size: 0.82rem; color: {THEME['success']}; margin-top: 0.3rem; }}
    .kpi-delta-neg {{ font-size: 0.82rem; color: {THEME['danger']}; margin-top: 0.3rem; }}
    .kpi-delta-neu {{ font-size: 0.82rem; color: {THEME['text_muted']}; margin-top: 0.3rem; }}

    /* ── Insight Banner ──────────────────────── */
    .insight-banner {{
        background: linear-gradient(135deg, #1e1040, #2d1b69);
        border: 1px solid {THEME['primary']}66;
        border-left: 5px solid {THEME['secondary']};
        border-radius: 12px;
        padding: 1rem 1.4rem;
        margin: 0.8rem 0 1.2rem 0;
        animation: slideIn 0.5s ease;
    }}
    @keyframes slideIn {{ from {{ opacity:0; transform:translateY(-8px); }} to {{ opacity:1; transform:translateY(0); }} }}
    .insight-title {{ font-size: 0.85rem; color: {THEME['accent']}; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.5rem; }}
    .insight-item {{ font-size: 0.92rem; color: {THEME['text_main']}; margin: 0.25rem 0; }}

    /* ── Section Headers ─────────────────────── */
    .section-title {{
        font-size: 1.05rem; font-weight: 700;
        color: {THEME['accent']}; letter-spacing: 0.04em;
        border-bottom: 1px solid {THEME['primary']}44;
        padding-bottom: 0.4rem; margin: 1.2rem 0 0.8rem 0;
    }}

    /* ── Suggest Button ──────────────────────── */
    .stButton > button {{
        background: linear-gradient(135deg, {THEME['primary']}, {THEME['secondary']}) !important;
        color: white !important; border: none !important;
        border-radius: 8px !important; padding: 0.35rem 0.8rem !important;
        font-size: 0.82rem !important; transition: opacity 0.2s;
    }}
    .stButton > button:hover {{ opacity: 0.85; }}

    /* ── Tabs ────────────────────────────────── */
    [data-testid="stTab"] {{ color: {THEME['text_muted']} !important; }}
    [aria-selected="true"] {{ color: {THEME['secondary']} !important; border-bottom: 2px solid {THEME['secondary']} !important; }}

    /* ── Expander ────────────────────────────── */
    [data-testid="stExpander"] {{
        background-color: {THEME['bg_card']} !important;
        border: 1px solid {THEME['primary']}33 !important;
        border-radius: 10px !important;
    }}

    /* ── Refresh Indicator ───────────────────── */
    .refresh-dot {{
        display: inline-block; width: 8px; height: 8px;
        background: {THEME['success']}; border-radius: 50%;
        animation: pulse 1.5s ease-in-out infinite;
        margin-right: 6px;
    }}
    @keyframes pulse {{
        0%,100% {{ opacity: 1; transform: scale(1); }}
        50%      {{ opacity: 0.4; transform: scale(0.8); }}
    }}

    /* ── Report card ─────────────────────────── */
    .report-box {{
        background: {THEME['bg_card']}; border: 1px solid {THEME['primary']}33;
        border-radius: 12px; padding: 1.2rem; margin: 0.5rem 0;
    }}

    /* ── Hide Streamlit chrome ───────────────── */
    #MainMenu {{ visibility: hidden; }}
    footer    {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────

def init_session_state():
    defaults = {
        "uploaded_df"        : None,
        "file_name"          : "",
        "chat_history"       : [],
        "queued_query"       : None,
        "dashboard_layouts"  : {},          # saved custom layouts
        "active_layout"      : "default",
        "auto_refresh"       : False,
        "refresh_interval"   : 30,
        "last_refresh"       : time.time(),
        "chat_input_trigger" : None,        # chat→dashboard sync
        "kpis_cache"         : None,
        "insights_cache"     : None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────────────────────
# HELPER: COMPUTE KPIs FROM ANY DATAFRAME
# ─────────────────────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Compute KPIs dynamically from whatever dataset is uploaded.
    Tries to detect Sales / Profit / Revenue / Quantity columns.
    Falls back gracefully for non-retail datasets.
    """
    kpis = {}
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    def find_col(*candidates):
        for c in candidates:
            for col in df.columns:
                if col.lower() == c.lower():
                    return col
        return None

    sales_col   = find_col("Sales", "Revenue", "Amount", "Total")
    profit_col  = find_col("Profit", "Net Profit", "Net Income")
    qty_col     = find_col("Quantity", "Qty", "Units", "Volume")
    order_col   = find_col("Order ID", "OrderID", "Transaction ID", "ID")
    cust_col    = find_col("Customer ID", "CustomerID", "Customer", "Client ID")

    kpis["total_rows"]   = len(df)
    kpis["total_cols"]   = len(df.columns)

    if sales_col:
        kpis["total_sales"]     = df[sales_col].sum()
        kpis["avg_sale"]        = df[sales_col].mean()
        kpis["max_sale"]        = df[sales_col].max()
        kpis["sales_col"]       = sales_col
    else:
        # Use first numeric col as proxy
        if numeric_cols:
            kpis["total_sales"] = df[numeric_cols[0]].sum()
            kpis["avg_sale"]    = df[numeric_cols[0]].mean()
            kpis["max_sale"]    = df[numeric_cols[0]].max()
            kpis["sales_col"]   = numeric_cols[0]
        else:
            kpis["total_sales"] = kpis["avg_sale"] = kpis["max_sale"] = 0
            kpis["sales_col"]   = None

    if profit_col:
        kpis["total_profit"] = df[profit_col].sum()
        kpis["profit_margin"] = (kpis["total_profit"] / kpis["total_sales"] * 100) if kpis["total_sales"] else 0
        kpis["profit_col"]   = profit_col
    else:
        kpis["total_profit"] = kpis["profit_margin"] = 0
        kpis["profit_col"]   = None

    if qty_col:
        kpis["total_qty"] = int(df[qty_col].sum())
    else:
        kpis["total_qty"] = 0

    kpis["total_orders"]    = df[order_col].nunique() if order_col else len(df)
    kpis["unique_customers"] = df[cust_col].nunique() if cust_col else 0
    kpis["avg_order_value"] = kpis["total_sales"] / kpis["total_orders"] if kpis["total_orders"] else 0

    # Discount
    disc_col = find_col("Discount")
    kpis["avg_discount"] = df[disc_col].mean() if disc_col else 0

    # Shipping delay
    ship_col = find_col("shipping_delay_days", "Shipping Delay", "Delay")
    kpis["avg_shipping_delay"] = df[ship_col].mean() if ship_col else 0

    return kpis


# ─────────────────────────────────────────────────────────────
# HELPER: RULE-BASED INSIGHTS (fallback when Module 3 absent)
# ─────────────────────────────────────────────────────────────

def local_insights(kpis: dict) -> list:
    insights = []
    if kpis.get("total_profit", 0) < 0:
        insights.append("⚠️ The business is currently running at a loss.")
    elif kpis.get("total_profit", 0) > 0:
        insights.append("✅ The business is profitable overall.")
    if kpis.get("avg_discount", 0) > 0.2:
        insights.append("⚠️ High discounting (>20%) is compressing profit margins.")
    elif kpis.get("avg_discount", 0) > 0.1:
        insights.append("📉 Moderate discounting detected — monitor impact on margins.")
    if kpis.get("avg_shipping_delay", 0) > 5:
        insights.append("🚚 Shipping delays exceed 5 days — logistics optimization needed.")
    if kpis.get("unique_customers", 0) > 500:
        insights.append("📈 Strong and diverse customer base contributing to revenue.")
    if kpis.get("avg_order_value", 0) > 400:
        insights.append("💰 High average order value indicates strong sales performance.")
    if not insights:
        insights.append("📊 Dataset loaded successfully. Run analysis for deeper insights.")
    return insights

def local_recommendations(kpis: dict) -> list:
    recs = []
    if kpis.get("avg_discount", 0) > 0.2:
        recs.append("Reduce discount levels to improve profitability.")
    if kpis.get("avg_shipping_delay", 0) > 5:
        recs.append("Optimise logistics to reduce shipping delays below 5 days.")
    if kpis.get("total_profit", 0) > 0:
        recs.append("Scale high-performing product categories to boost revenue.")
    if kpis.get("avg_order_value", 0) > 400:
        recs.append("Introduce premium product bundles to increase revenue further.")
    if kpis.get("unique_customers", 0) > 500:
        recs.append("Leverage customer loyalty programmes to improve retention.")
    return recs


# ─────────────────────────────────────────────────────────────
# HELPER: SMART QUERY SUGGESTIONS (replicated from Module 2)
# ─────────────────────────────────────────────────────────────

def generate_suggestions(df: pd.DataFrame, chat_history=None) -> list:
    suggestions = []
    numeric_cols     = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    time_cols = [c for c in df.columns if any(k in c.lower() for k in ["year","date","time","month"])]

    metrics    = [c for c in numeric_cols     if c not in time_cols][:3]
    categories = [c for c in categorical_cols if c not in time_cols][:3]

    if not metrics:
        return ["Show all data points"]

    primary = metrics[0]

    if chat_history:
        for msg in reversed(chat_history):
            if msg.get("role") == "assistant" and msg.get("parsed_query"):
                last = msg["parsed_query"]
                intent = last.get("intent")
                metric = last.get("metric") or primary
                if intent == "trend":
                    suggestions += [f"Compare {metric.lower()} across categories",
                                    f"Which category has the highest {metric.lower()}?"]
                elif intent == "comparison":
                    suggestions += [f"Show historical trend for {metric.lower()}"]
                    if len(metrics) > 1:
                        suggestions.append(f"How does {metric.lower()} compare to {metrics[1].lower()}?")
                elif intent in ["profiling", "quality", "summary"]:
                    suggestions.append(f"Show {metric.lower()} trend over time")
                break

    if len(suggestions) < 3:
        if f"What is the total {primary.lower()}?" not in suggestions:
            suggestions.append(f"What is the total {primary.lower()}?")
        if categories:
            suggestions.append(f"Compare {primary.lower()} across {categories[0].lower()}s")
        if time_cols:
            suggestions.append(f"Show {primary.lower()} trend over {time_cols[0].lower()}")

    return list(dict.fromkeys(suggestions))[:5]


# ─────────────────────────────────────────────────────────────
# FEATURE 1 — ADVANCED DATA VISUALIZATION LAYER
# ─────────────────────────────────────────────────────────────

def render_visualization_layer(df: pd.DataFrame, kpis: dict):
    st.markdown('<div class="section-title">📊 Advanced Data Visualization</div>', unsafe_allow_html=True)

    numeric_cols     = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    time_cols        = [c for c in df.columns if any(k in c.lower() for k in ["year","date","month","time"])]

    if not numeric_cols:
        st.info("No numeric columns found for visualization.")
        return

    # ── Chart Recommendation Engine
    st.markdown("#### 🧠 Chart Recommendation Engine")
    rec_col = kpis.get("sales_col") or numeric_cols[0]

    rec_tabs = st.tabs(["📈 Trend", "📊 Distribution", "🗂️ Category Breakdown", "🔥 Correlation", "🌍 Geographic"])

    # TAB 1 – TREND
    with rec_tabs[0]:
        if time_cols:
            time_col = time_cols[0]
            try:
                temp = df.copy()
                temp[time_col] = pd.to_datetime(temp[time_col], errors="coerce")
                temp = temp.dropna(subset=[time_col])
                temp["_period"] = temp[time_col].dt.to_period("M").dt.to_timestamp()
                trend_df = temp.groupby("_period")[rec_col].sum().reset_index()
                trend_df.columns = [time_col, rec_col]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=trend_df[time_col], y=trend_df[rec_col],
                    mode="lines+markers",
                    line=dict(color=THEME["secondary"], width=2.5),
                    marker=dict(size=6, color=THEME["accent"]),
                    fill="tozeroy", fillcolor=f"rgba(168,85,247,0.12)",
                    name=rec_col
                ))
                # Rolling average overlay
                if len(trend_df) >= 3:
                    trend_df["_rolling"] = trend_df[rec_col].rolling(3, min_periods=1).mean()
                    fig.add_trace(go.Scatter(
                        x=trend_df[time_col], y=trend_df["_rolling"],
                        mode="lines", line=dict(color=THEME["warning"], width=1.5, dash="dot"),
                        name="3-period Moving Avg"
                    ))
                fig.update_layout(
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=THEME["text_main"]), legend=dict(bgcolor="rgba(0,0,0,0)"),
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#2d2d3a"),
                    margin=dict(l=0, r=0, t=30, b=0), height=340
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"💡 *AI Tip: The chart shows {rec_col} over time with a 3-period moving average to smooth short-term fluctuations.*")
            except Exception as e:
                st.warning(f"Trend chart skipped: {e}")
        else:
            st.info("No date/time column detected for trend analysis.")

    # TAB 2 – DISTRIBUTION
    with rec_tabs[1]:
        sel_col = st.selectbox("Select column for distribution:", numeric_cols, key="dist_col")
        fig = make_subplots(rows=1, cols=2, subplot_titles=["Histogram", "Box Plot"])
        fig.add_trace(go.Histogram(x=df[sel_col].dropna(), marker_color=THEME["secondary"], opacity=0.8, name="Histogram"), row=1, col=1)
        fig.add_trace(go.Box(y=df[sel_col].dropna(), marker_color=THEME["accent"], boxpoints="outliers", name="Distribution"), row=1, col=2)
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=THEME["text_main"]), showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0), height=340
        )
        st.plotly_chart(fig, use_container_width=True)
        # Outlier annotation
        q1, q3 = df[sel_col].quantile(0.25), df[sel_col].quantile(0.75)
        iqr = q3 - q1
        outliers = df[(df[sel_col] < q1 - 1.5*iqr) | (df[sel_col] > q3 + 1.5*iqr)]
        if len(outliers):
            st.markdown(f'<div style="color:{THEME["warning"]};font-size:0.85rem">⚠️ <b>{len(outliers)} outliers</b> detected in <b>{sel_col}</b> using IQR method.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="color:{THEME["success"]};font-size:0.85rem">✅ No outliers detected in <b>{sel_col}</b>.</div>', unsafe_allow_html=True)

    # TAB 3 – CATEGORY BREAKDOWN
    with rec_tabs[2]:
        if categorical_cols:
            cat_sel  = st.selectbox("Group by:", categorical_cols, key="cat_col")
            num_sel  = st.selectbox("Metric:", numeric_cols, key="cat_num")
            agg_mode = st.radio("Aggregation:", ["Sum", "Mean", "Count"], horizontal=True, key="agg_mode")
            agg_fn   = {"Sum": "sum", "Mean": "mean", "Count": "count"}[agg_mode]
            cat_df   = df.groupby(cat_sel)[num_sel].agg(agg_fn).reset_index().sort_values(num_sel, ascending=False)

            c1, c2 = st.columns(2)
            with c1:
                fig_bar = px.bar(cat_df, x=cat_sel, y=num_sel, text_auto=".2s",
                                 color=num_sel, color_continuous_scale="Purples",
                                 template="plotly_dark")
                fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                      coloraxis_showscale=False, margin=dict(l=0,r=0,t=20,b=0), height=300)
                st.plotly_chart(fig_bar, use_container_width=True)
            with c2:
                fig_pie = px.pie(cat_df, names=cat_sel, values=num_sel,
                                 hole=0.45, color_discrete_sequence=px.colors.sequential.Purples_r,
                                 template="plotly_dark")
                fig_pie.update_traces(textposition="inside", textinfo="percent+label")
                fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=20,b=0), height=300, showlegend=False)
                st.plotly_chart(fig_pie, use_container_width=True)

            # Top & Bottom performers
            top = cat_df.head(3)[cat_sel].tolist()
            bot = cat_df.tail(3)[cat_sel].tolist()
            st.markdown(f'<div style="font-size:0.85rem;color:{THEME["success"]}">🏆 Top performers: <b>{", ".join(map(str,top))}</b></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.85rem;color:{THEME["warning"]}">⚠️ Underperformers: <b>{", ".join(map(str,bot))}</b></div>', unsafe_allow_html=True)
        else:
            st.info("No categorical columns found for grouping.")

    # TAB 4 – CORRELATION HEATMAP
    with rec_tabs[3]:
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr()
            fig = go.Figure(go.Heatmap(
                z=corr.values, x=corr.columns, y=corr.columns,
                colorscale="Purp", text=corr.round(2).values.astype(str),
                texttemplate="%{text}", zmin=-1, zmax=1,
                colorbar=dict(title="Correlation")
            ))
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0,r=0,t=20,b=0), height=380
            )
            st.plotly_chart(fig, use_container_width=True)
            # AI tip
            corr_pairs = [(corr.columns[i], corr.columns[j], corr.iloc[i,j])
                          for i in range(len(corr)) for j in range(i+1, len(corr))]
            if corr_pairs:
                strongest = max(corr_pairs, key=lambda x: abs(x[2]))
                st.caption(f"💡 Strongest correlation: **{strongest[0]}** ↔ **{strongest[1]}** (r = {strongest[2]:.2f})")
        else:
            st.info("Need at least 2 numeric columns for correlation analysis.")

    # TAB 5 – GEOGRAPHIC
    with rec_tabs[4]:
        geo_cols = [c for c in df.columns if any(k in c.lower() for k in ["country","state","region","city","location","geo"])]
        if geo_cols and numeric_cols:
            geo_col = st.selectbox("Geographic column:", geo_cols, key="geo_col")
            geo_num = st.selectbox("Metric:", numeric_cols, key="geo_num")
            geo_df  = df.groupby(geo_col)[geo_num].sum().reset_index().sort_values(geo_num, ascending=True)
            fig = px.bar(geo_df, x=geo_num, y=geo_col, orientation="h",
                         color=geo_num, color_continuous_scale="Purples",
                         text_auto=".2s", template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               coloraxis_showscale=False, margin=dict(l=0,r=0,t=20,b=0),
                               height=max(300, len(geo_df) * 30))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No geographic column detected (Country / State / Region / City).")


# ─────────────────────────────────────────────────────────────
# FEATURE 2 — INTERACTIVE DASHBOARD BUILDER
# ─────────────────────────────────────────────────────────────

def render_dashboard_builder(df: pd.DataFrame):
    st.markdown('<div class="section-title">🛠️ Interactive Dashboard Builder</div>', unsafe_allow_html=True)

    numeric_cols     = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    time_cols        = [c for c in df.columns if any(k in c.lower() for k in ["year","date","month","time"])]
    all_cols         = df.columns.tolist()

    st.markdown("Build your own layout — choose widgets and arrange them below.")

    # ── Layout template
    col_tmpl, col_name, col_save = st.columns([2, 2, 1])
    with col_tmpl:
        template = st.selectbox(
            "Start from template:",
            ["Blank", "Sales Overview", "Operations Review", "Executive Summary"],
            key="db_template"
        )
    with col_name:
        layout_name = st.text_input("Save layout as:", value="My Dashboard", key="layout_name")
    with col_save:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save Layout"):
            st.session_state["dashboard_layouts"][layout_name] = {
                "template": template,
                "saved_at": datetime.now().strftime("%d %b %Y %H:%M"),
            }
            st.success(f"✅ Layout '{layout_name}' saved!")

    # Saved layouts
    if st.session_state["dashboard_layouts"]:
        st.markdown("**📁 Saved Layouts:**")
        for name, meta in st.session_state["dashboard_layouts"].items():
            st.markdown(f'<span style="color:{THEME["accent"]};font-size:0.85rem">📌 {name} — saved {meta["saved_at"]}</span>', unsafe_allow_html=True)

    st.divider()

    # ── Widget builder
    st.markdown("#### ➕ Add Widgets to Your Dashboard")
    num_widgets = st.slider("Number of widgets:", 1, 6, 3, key="num_widgets")
    widget_configs = []
    widget_cols_row = st.columns(min(num_widgets, 3))

    for i in range(num_widgets):
        with widget_cols_row[i % 3]:
            st.markdown(f'<div class="report-box">', unsafe_allow_html=True)
            chart_type = st.selectbox(
                f"Widget {i+1} type:",
                ["KPI Card", "Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot", "Data Table"],
                key=f"wtype_{i}"
            )
            col_choice = st.selectbox(f"Column:", all_cols, key=f"wcol_{i}")
            widget_configs.append({"type": chart_type, "col": col_choice})
            st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🖥️ Render My Dashboard", type="primary"):
        st.markdown("---")
        st.markdown("### 🖥️ Your Custom Dashboard")
        render_cols = st.columns(min(num_widgets, 3))
        for i, cfg in enumerate(widget_configs):
            with render_cols[i % 3]:
                _render_widget(df, cfg["type"], cfg["col"], i)


def _render_widget(df, chart_type, col, idx):
    try:
        if chart_type == "KPI Card":
            val = df[col].sum() if pd.api.types.is_numeric_dtype(df[col]) else df[col].nunique()
            label = "Sum" if pd.api.types.is_numeric_dtype(df[col]) else "Unique"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label} of {col}</div>
                <div class="kpi-value">{val:,.0f}</div>
            </div>""", unsafe_allow_html=True)

        elif chart_type == "Bar Chart" and pd.api.types.is_numeric_dtype(df[col]):
            cat_cols = df.select_dtypes("object").columns
            if len(cat_cols):
                gdf = df.groupby(cat_cols[0])[col].sum().reset_index()
                fig = px.bar(gdf, x=cat_cols[0], y=col, color_discrete_sequence=[THEME["secondary"]],
                             template="plotly_dark", height=260)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  margin=dict(l=0,r=0,t=20,b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.bar_chart(df[col])

        elif chart_type == "Line Chart" and pd.api.types.is_numeric_dtype(df[col]):
            fig = px.line(df.reset_index(), x="index", y=col,
                          color_discrete_sequence=[THEME["secondary"]], template="plotly_dark", height=260)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               margin=dict(l=0,r=0,t=20,b=0))
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Pie Chart":
            if not pd.api.types.is_numeric_dtype(df[col]):
                vc = df[col].value_counts().head(8).reset_index()
                vc.columns = [col, "count"]
                fig = px.pie(vc, names=col, values="count", hole=0.4,
                             color_discrete_sequence=px.colors.sequential.Purples_r
