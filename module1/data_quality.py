import streamlit as st

def data_quality_section(df):
    st.title("🔍 Data Quality Report")
    st.write("Missing values:", df.isnull().sum())
