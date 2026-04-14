import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_file(uploaded_file):
    """
    Loads a file (CSV or Excel) uploaded via Streamlit into a DataFrame.
    Returns None with an error message on failure.
    """
    if uploaded_file is None:
        return None
        
    try:
        filename, file_extension = os.path.splitext(uploaded_file.name)
        file_extension = file_extension.lower()
        
        if file_extension in ['.csv']:
            # Try multiple encodings just in case
            try:
                df = pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                try:
                    df = pd.read_csv(uploaded_file, encoding='latin1')
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='cp1252')
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(uploaded_file)
        else:
            st.error(f"Unsupported file format: {file_extension}. Please upload a CSV or Excel file.")
            return None
            
        return df

    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def get_file_info(df):
    """Returns basic shape and size info of the dataframe."""
    if df is None:
        return {}
    
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "size_kb": df.memory_usage(deep=True).sum() / 1024,
        "missing_cells": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum())
    }

