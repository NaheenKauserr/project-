import os
import google.generativeai as genai
import streamlit as st

def generate_rule_based_insights(df, stats, correlations):
    """Fallback generator for insights if API is unavailable."""
    insights_list = ["**Automated Local Analysis (API Unavailable/Quota Full):**"]
    
    # Volume insight
    insights_list.append(f"- **Data Architecture**: The dataset contains **{len(df):,}** distinct records spread across **{len(df.columns)}** metric profiles, establishing a solid foundation for robust machine learning models.")
    
    # Correlation insight
    if correlations:
        top_corr = correlations[0]
        insights_list.append(f"- **Key Driver Identified**: A significant correlation (Score: **{top_corr['score']:.2f}**) exists between `{top_corr['col1']}` and `{top_corr['col2']}`. This strong proportional relationship suggests that fluctuations in one metric reliably predict shifts in the other.")
        
    # Categorical dominant entity insight
    cat_cols = list(df.select_dtypes(['object', 'category']).columns)
    if cat_cols:
        primary_cat = cat_cols[0]
        try:
            top_val = df[primary_cat].mode().iloc[0]
            insights_list.append(f"- **Dominant Segment**: Within the `{primary_cat}` categorical division, the value **'{top_val}'** is the most frequently occurring baseline, representing the primary driving segment of your underlying operations.")
        except Exception:
            pass

    # Numeric insight
    num_cols = list(df.select_dtypes('number').columns)
    if num_cols:
        target_num = num_cols[0]
        try:
            mean_val = df[target_num].mean()
            insights_list.append(f"- **Central Tendency Focus**: The average moving baseline for `{target_num}` normalizes around **{mean_val:,.2f}**. Sharp deviations from this center point in future data payloads should trigger automatic review workflows.")
        except Exception:
            pass
            
    return "\n".join(insights_list)

@st.cache_data
def generate_insights(df, stats, correlations):
    """
    Generates AI-powered insights from data summary.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if df is None or df.empty:
        return "No data available to analyze."
        
    if not api_key or api_key == "your_key_here":
        return generate_rule_based_insights(df, stats, correlations)

    try:
        genai.configure(api_key=api_key)
        # Using the specified Gemini model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Prepare context data
        rows = len(df)
        cols = len(df.columns)
        numeric_cols = list(df.select_dtypes('number').columns)
        cat_cols = list(df.select_dtypes(['object', 'category']).columns)
        
        # Format stats specifically to avoid sending overly huge string
        stats_str = stats.to_csv() if not stats.empty else "None"
        import json
        corr_str = json.dumps(correlations) if correlations else "None"
        
        prompt = (
            f"Analyze this dataset summary: {rows} rows, {cols} columns, "
            f"numeric: {numeric_cols}, categorical: {cat_cols}, "
            f"key stats (describe): {stats_str}, correlations: {corr_str}. "
            "Give 3-5 bullet point insights highlighting interesting patterns or anomalies. Do not just restate the numbers, infer potential business or real-world meanings."
        )
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"API Failed: {e}")
        return generate_rule_based_insights(df, stats, correlations)

