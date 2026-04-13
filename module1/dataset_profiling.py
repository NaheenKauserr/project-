import streamlit as st
import pandas as pd

def dataset_profiling_section(df):
    st.title("📊 Dataset Profiling")
    st.dataframe(df.describe())
