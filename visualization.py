import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np

@st.cache_data
def auto_charts(df, column_types):
    """
    Generates intelligent Plotly charts based on column types available.
    Returns: list of (title, plotly_figure)
    Maximum 10 charts.
    """
    charts = []
    
    if df is None or df.empty:
        return charts
        
    raw_num = column_types.get("numeric", [])
    num_cols = [c for c in raw_num if 'id' not in c.lower() and 'index' not in c.lower() and 'code' not in c.lower()]
    cat_cols = column_types.get("categorical", [])
    date_cols = column_types.get("datetime", [])
    
    # Optional sampling if data is huge
    plot_df = df.sample(n=1000) if len(df) > 1000 else df.copy()

    def apply_sneat_theme(fig_to_style):
        fig_to_style.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter", color="#2c2c2c", size=14),
            title_font=dict(size=18, color="#2c2c2c", family="Inter", weight="bold" if hasattr(go.layout.title.Font, 'weight') else None),
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis=dict(showgrid=False, zeroline=False, linecolor="#ebe9f1"),
            yaxis=dict(showgrid=True, gridcolor="#ebe9f1", zeroline=False, linecolor="rgba(0,0,0,0)"),
        )
        # Apply primary purple color to typical traces, rounded corners to bars
        fig_to_style.update_traces(
            selector=dict(type="bar"), 
            marker_color="#7367f0",
            marker_line_width=0,
            marker_cornerradius=6 # Only works in new plotly, ignored otherwise
        )
        fig_to_style.update_traces(
            selector=dict(type="scatter", mode="markers"),
            marker=dict(color="#7367f0", size=8, opacity=0.8)
        )
        fig_to_style.update_traces(
            selector=dict(type="scatter", mode="lines"),
            line_color="#7367f0"
        )
        fig_to_style.update_traces(
            selector=dict(type="pie"),
            hole=0.65,
            marker=dict(line=dict(color="white", width=2))
        )
        return fig_to_style

    # 1. Line Graph (datetime + numeric - Mean trend)
    if len(date_cols) > 0 and len(num_cols) > 0:
        try:
            date_col = date_cols[0]
            val_col = num_cols[0]
            agg_df = plot_df.dropna(subset=[date_col, val_col]).groupby(date_col)[val_col].mean().reset_index().sort_values(by=date_col)
            if not agg_df.empty:
                fig = px.line(agg_df, x=date_col, y=val_col, title=f"Trend over {date_col}")
                # Subtle gradient via fill='tozeroy' and marker updates
                fig.update_traces(fill='tozeroy', fillcolor='rgba(115, 103, 240, 0.2)')
                charts.append(("Line Graph", apply_sneat_theme(fig)))
        except Exception:
            pass

    # 2. Area Chart (datetime + numeric - Volume/Sum accumulation)
    if len(date_cols) > 0 and len(num_cols) > 0:
        try:
            date_col = date_cols[0]
            val_col = num_cols[0]
            agg_df = plot_df.dropna(subset=[date_col, val_col]).groupby(date_col)[val_col].sum().reset_index().sort_values(by=date_col)
            if not agg_df.empty:
                fig_area = px.area(agg_df, x=date_col, y=val_col, title=f"Total Volume over {date_col}")
                fig_area.update_traces(fillcolor='rgba(40, 199, 111, 0.6)', line_color='#28c76f')
                charts.append(("Area Chart", apply_sneat_theme(fig_area)))
        except Exception:
            pass

    # 3. Heat Map (Heat Chart) (2+ numeric)
    if len(num_cols) >= 2:
        try:
            corr_matrix = plot_df[num_cols].corr()
            if not corr_matrix.isna().all().all():
                fig = px.imshow(corr_matrix.fillna(0), text_auto=True, aspect="auto", 
                                title="Correlation Heatmap", color_continuous_scale=[[0, '#f8f7fa'], [1, '#7367f0']])
                charts.append(("Heat Chart", apply_sneat_theme(fig)))
        except Exception:
            pass

    # 4. Scatter Plot (2+ numeric)
    if len(num_cols) >= 2:
        try:
            num1, num2 = num_cols[0], num_cols[1]
            if not plot_df[[num1, num2]].dropna().empty:
                fig_scatter = px.scatter(plot_df, x=num1, y=num2, title=f"{num1} vs {num2}", opacity=0.7)
                charts.append(("Scatter Plot", apply_sneat_theme(fig_scatter)))
        except Exception:
            pass

    # 5. Histogram (1+ numeric)
    if len(num_cols) > 0:
        try:
            target_num = num_cols[0]
            if not plot_df[target_num].dropna().empty:
                fig_hist = px.histogram(plot_df.dropna(subset=[target_num]), x=target_num, title=f"Distribution of {target_num}")
                charts.append(("Histogram", apply_sneat_theme(fig_hist)))
        except Exception:
            pass

    # 6. Box Plot (categorical + numeric)
    if len(cat_cols) > 0 and len(num_cols) > 0:
        try:
            cat_col = cat_cols[0]
            val_col = num_cols[0]
            if plot_df[cat_col].nunique() <= 12 and not plot_df[val_col].dropna().empty:
                fig_box = px.box(plot_df, x=cat_col, y=val_col, title=f"Spread of {val_col} by {cat_col}")
                fig_box.update_traces(marker_color="#28c76f" if val_col else "#7367f0")
                charts.append(("Box Plot", apply_sneat_theme(fig_box)))
        except Exception:
            pass

    # 7. Violin Plot (categorical + numeric)
    if len(cat_cols) > 0 and len(num_cols) > 0:
        try:
            cat_col = cat_cols[0]
            val_col = num_cols[0]
            if plot_df[cat_col].nunique() <= 12 and not plot_df[val_col].dropna().empty:
                fig_violin = px.violin(plot_df, x=cat_col, y=val_col, title=f"Density of {val_col} by {cat_col}")
                fig_violin.update_traces(marker_color="#ea5455")
                charts.append(("Violin Plot", apply_sneat_theme(fig_violin)))
        except Exception:
            pass

    # 8. Bar Graph (categorical + numeric)
    if len(cat_cols) > 0 and len(num_cols) > 0:
        try:
            cat_col = cat_cols[0]
            val_col = num_cols[0]
            if plot_df[cat_col].nunique() <= 20:
                bar_df = plot_df.groupby(cat_col)[val_col].mean().reset_index().sort_values(by=val_col, ascending=False).head(15).dropna()
                if not bar_df.empty:
                    # Remove color=cat_col so they inherit single primary color
                    fig_bar = px.bar(bar_df, x=cat_col, y=val_col, title=f"Average {val_col} by {cat_col}")
                    charts.append(("Bar Graph", apply_sneat_theme(fig_bar)))
        except Exception:
            pass

    # 9. Pie Chart (categorical only, <=10 unique)
    if len(cat_cols) > 0:
        try:
            pie_col = next((col for col in cat_cols if 1 < plot_df[col].nunique() <= 10), None)
            if pie_col:
                pie_df = plot_df[pie_col].value_counts().reset_index()
                pie_df.columns = [pie_col, 'count']
                if not pie_df.empty:
                    # Using custom Sneat palette
                    fig_pie = px.pie(pie_df, names=pie_col, values='count', title=f"Proportion by {pie_col}",
                                     color_discrete_sequence=['#7367f0', '#28c76f', '#00cfe8', '#ea5455', '#ff9f43', '#a8aaae'])
                    charts.append(("Pie Chart", apply_sneat_theme(fig_pie)))
        except Exception:
            pass

    # 10. Treemap (categorical hierarchy)
    if len(cat_cols) > 0:
        try:
            tree_col = next((col for col in cat_cols if 1 < plot_df[col].nunique() <= 25), None)
            if tree_col:
                tree_df = plot_df[tree_col].value_counts().reset_index()
                tree_df.columns = [tree_col, 'count']
                if not tree_df.empty:
                    fig_tree = px.treemap(tree_df, path=[tree_col], values='count', title=f"Hierarchy of {tree_col}",
                                          color='count', color_continuous_scale=[[0, '#f8f7fa'], [1, '#7367f0']])
                    charts.append(("Treemap", apply_sneat_theme(fig_tree)))
        except Exception:
            pass

    return charts[:10]

