import pandas as pd
import streamlit as st
import plotly.graph_objects as go

try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False

@st.cache_data
def auto_forecast(df, column_types):
    """
    Forecasts a target variable using Prophet if a time column exists.
    Returns: dict {'figure': plotly_fig, 'forecast_df': pd.DataFrame} or None
    """
    if not HAS_PROPHET:
        # If prophet fails to import or isn't installed
        return None

    if df is None or df.empty:
        return None

    def apply_sneat_theme(fig_to_style):
        fig_to_style.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", color="#4b4b4b", size=12),
            title_font=dict(size=16, color="#4b4b4b", family="Inter"),
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis=dict(showgrid=False, zeroline=False, linecolor="#ebe9f1"),
            yaxis=dict(showgrid=True, gridcolor="#ebe9f1", zeroline=False, linecolor="rgba(0,0,0,0)"),
        )
        return fig_to_style


    date_cols = column_types.get("datetime", [])
    num_cols = column_types.get("numeric", [])

    if not date_cols or not num_cols:
        return None

    # Pick first date and first numeric
    date_col = date_cols[0]
    
    # Try to find a good numeric target by name, else first one
    target_col = num_cols[0]
    for col in num_cols:
        l_col = col.lower()
        if any(w in l_col for w in ['value', 'sales', 'price', 'amount', 'total']):
            target_col = col
            break

    # Prepare data for prophet
    pdf = df[[date_col, target_col]].dropna().copy()
    pdf = pdf.rename(columns={date_col: 'ds', target_col: 'y'})
    
    # Ensure datetime
    pdf['ds'] = pd.to_datetime(pdf['ds'], errors='coerce')
    pdf = pdf.dropna(subset=['ds'])
    
    # Needs at least 12 rows
    if len(pdf) < 12:
        return None

    # Group by date to remove duplicates/multiple entries per date
    pdf = pdf.groupby('ds')['y'].sum().reset_index()
    pdf = pdf.sort_values('ds')

    try:
        m = Prophet(daily_seasonality=False, yearly_seasonality=True)
        m.fit(pdf)

        # Decide periods: 30 or 20% of length
        periods = max(30, int(len(pdf) * 0.2))
        
        # Decide frequency based on data diff
        diffs = pdf['ds'].diff().dt.days.dropna()
        if len(diffs) > 0 and diffs.median() > 20:
            freq = 'M'
        else:
            freq = 'D'

        future = m.make_future_dataframe(periods=periods, freq=freq)
        forecast = m.predict(future)

        # Create Plotly figure
        fig = go.Figure()

        # Actual data
        fig.add_trace(go.Scatter(
            x=pdf['ds'], y=pdf['y'], mode='markers', name='Actual',
            marker=dict(color='#4b4b4b', size=4)
        ))

        # Prediction
        fig.add_trace(go.Scatter(
            x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast',
            line=dict(color='#7367f0')
        ))

        # Confidence intervals
        fig.add_trace(go.Scatter(
            x=list(forecast['ds']) + list(forecast['ds'])[::-1],
            y=list(forecast['yhat_upper']) + list(forecast['yhat_lower'])[::-1],
            fill='toself', fillcolor='rgba(115, 103, 240, 0.2)', line=dict(color='rgba(255,255,255,0)'),
            name='Confidence Interval', hoverinfo="skip"
        ))

        fig.update_layout(title=f"Forecast of {target_col}", xaxis_title="Date", yaxis_title=target_col)
        fig = apply_sneat_theme(fig)

        return {
            'figure': fig,
            'forecast_df': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
        }
        
    except Exception as e:
        print(f"Prophet forecasting failed: {e}")
        return None

