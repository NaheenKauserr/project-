# module1/file_upload.py
import streamlit as st
import pandas as pd

def file_upload_section():
    st.title("📁 Data Upload")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx', 'xls']
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.session_state["uploaded_df"] = df
            st.session_state["file_name"] = uploaded_file.name
            
            st.success(f"✅ Successfully loaded {uploaded_file.name}")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error loading file: {e}")
