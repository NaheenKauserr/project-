import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def get_column_types(df):
    """
    Classifies DataFrame columns into types.
    Returns: dict with keys: 'numeric', 'categorical', 'datetime', 'boolean'
    """
    if df is None or df.empty:
        return {"numeric": [], "categorical": [], "datetime": [], "boolean": []}
        
    types = {
        "numeric": [],
        "categorical": [],
        "datetime": [],
        "boolean": []
    }
    
    for col in df.columns:
        if pd.api.types.is_bool_dtype(df[col]) or (df[col].nunique() == 2 and set(df[col].dropna().unique()) <= {0, 1}):
            types["boolean"].append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            # If a numeric column has very few unique values, maybe it is categorical?
            # We'll stick to strict types for ML logic consistency.
            if df[col].nunique() <= 10 and not pd.api.types.is_float_dtype(df[col]):
                # If int and very few unique values, consider it categorical for visualization
                types["categorical"].append(col)
            types["numeric"].append(col)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            types["datetime"].append(col)
        else:
            types["categorical"].append(col)
            
    # Remove duplicates from lists to be safe
    for k in types:
        types[k] = list(set(types[k]))

    return types

@st.cache_data
def compute_stats(df):
    """
    Computes statistical properties of the numeric columns.
    Returns DataFrame.
    """
    if df is None or df.empty:
        return pd.DataFrame()
        
    num_df = df.select_dtypes(include=[np.number])
    if num_df.empty:
        return pd.DataFrame()
        
    stats = num_df.describe().T
    return stats

@st.cache_data
def find_correlations(df):
    """
    Finds pearson correlations between numerical fields.
    Returns a list of tuples/dicts.
    """
    if df is None or df.empty:
        return []
        
    num_df = df.select_dtypes(include=[np.number])
    if num_df.shape[1] < 2:
        return []
        
    corr_matrix = num_df.corr().abs()
    
    # Get upper triangle
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    
    correlations = []
    for row in upper.index:
        for col in upper.columns:
            val = upper.loc[row, col]
            if not pd.isna(val) and val > 0.0:  # You can apply threshold here
                correlations.append({"col1": row, "col2": col, "score": float(val)})
                
    # Sort descending
    correlations.sort(key=lambda x: x["score"], reverse=True)
    return correlations

@st.cache_data
def detect_outliers(df):
    """Returns dict of column: number of outliers using IQR."""
    outliers = {}
    if df is None or df.empty:
        return outliers
        
    num_df = df.select_dtypes(include=[np.number])
    for col in num_df.columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        count = ((df[col] < lower) | (df[col] > upper)).sum()
        if count > 0:
            outliers[col] = int(count)
    return outliers

