import streamlit as st
import numpy as np
import pandas as pd
import data_analysis
import utils

def generate_kpis(df, column_types):
    """
    Generates up to 12 dynamic, highly insightful KPIs based on actual data structure,
    including correlation relationships, aggregations, and variances.
    Returns: list of tuples (name, value, delta_or_caption)
    """
    kpis = []
    
    if df is None or df.empty:
        return kpis
        
    import data_cleaning
    report = data_cleaning.get_cleaning_report()
    
    # Group 1: Dataset Health & Base Stats
    kpis.append(("Total Records", f"{len(df):,}", "Rows analyzed"))
    
    if report.get("missing_filled", 0) > 0:
        kpis.append(("Missing Data Fixed", f"{report['missing_filled']:,}", "Imputed to preserve data"))
    else:
        kpis.append(("Data Quality", "100% Clean", "No missing values originally"))

    raw_numeric_cols = column_types.get("numeric", [])
    # Exclude IDs from aggregate math
    numeric_cols = [c for c in raw_numeric_cols if 'id' not in c.lower() and 'index' not in c.lower() and 'code' not in c.lower()]
    cat_cols = column_types.get("categorical", [])
    date_cols = column_types.get("datetime", [])
    
    # Track which numeric columns we use so we don't repeat the same metric
    used_num_cols = set()

    # Group 2: Relationship Finding
    correlations = data_analysis.find_correlations(df)
    if correlations:
        top_corr = correlations[0]
        kpis.append(("Strongest Relation", f"{top_corr['col1']} ~ {top_corr['col2']}", f"Score: {top_corr['score']:.2f}"))
        used_num_cols.update([top_corr['col1'], top_corr['col2']])
    else:
        kpis.append(("Strongest Relation", "None Found", "Insufficient data variation"))

    # Group 3: Financials / Volumes (Sums of key metrics)
    # Target columns that sound like amounts or totals
    sum_candidates = [c for c in numeric_cols if any(word in c.lower() for word in ['sales', 'revenue', 'profit', 'amount', 'total', 'price', 'cost', 'qty', 'quantity'])]
    if not sum_candidates:
        sum_candidates = [c for c in numeric_cols if c not in used_num_cols]
        
    for col in sum_candidates[:2]:
        total_sum = df[col].sum()
        avg_val = df[col].mean()
        # Treat as positive trend just for visual if sum > 0
        kpis.append((f"Total {col}", utils.format_number(total_sum), f"Avg: {utils.format_number(avg_val)}"))
        used_num_cols.add(col)
        
    # Group 4: High Variance / Volatility
    remaining_nums = [c for c in numeric_cols if c not in used_num_cols]
    if remaining_nums:
        # Calculate Coefficient of Variation (std / mean)
        cvs = []
        for col in remaining_nums:
            mean_val = df[col].mean()
            if mean_val != 0:
                cv = df[col].std() / mean_val
                cvs.append((col, cv))
        if cvs:
            cvs.sort(key=lambda x: abs(x[1]), reverse=True)
            most_volatile = cvs[0][0]
            kpis.append((f"High Volatility", f"{most_volatile}", f"CV: {abs(cvs[0][1]):.2f}"))
            used_num_cols.add(most_volatile)

    # Group 5: Peak Values (Max)
    remaining_nums = [c for c in numeric_cols if c not in used_num_cols]
    if remaining_nums:
        max_col = remaining_nums[0]
        max_val = df[max_col].max()
        kpis.append((f"Peak {max_col}", utils.format_number(max_val), "Highest recorded"))

    # Group 6: Categorical Insights (Top Entities)
    for col in cat_cols:
        if df[col].nunique() > 1:
            top_val = df[col].mode().iloc[0]
            top_count = (df[col] == top_val).sum()
            kpis.append((f"Top {col}", f"{str(top_val)}", f"{top_count} occurrences"))
            break # Just one categorical highlight

    # Group 7: Timeline
    if date_cols:
        d_col = date_cols[0]
        min_d, max_d = df[d_col].min(), df[d_col].max()
        if pd.notna(min_d) and pd.notna(max_d):
            days = (max_d - min_d).days
            kpis.append(("Time Span", f"{days} Days", f"{min_d.strftime('%Y-%m-%d')} to {max_d.strftime('%Y-%m-%d')}"))
            
    # Group 8: Outliers Presence
    outliers = data_analysis.detect_outliers(df)
    if outliers:
        # Find column with most outliers
        top_outlier_col = max(outliers, key=outliers.get)
        kpis.append((f"Total Outliers", f"{sum(outliers.values()):,}", f"Mostly in {top_outlier_col}"))

    # Pad to ensure a decent looking grid if we randomly got 3 or 7, but dashboard wraps correctly now.
    return kpis[:12]

