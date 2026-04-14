import streamlit as st
import time
from fpdf import FPDF
import markdown

def format_number(num):
    """Format large numbers to a readable string (e.g. 1M, 5K)."""
    try:
        num = float(num)
        if abs(num) >= 1_000_000_000:
            return f"{num / 1_000_000_000:.2f}B"
        elif abs(num) >= 1_000_000:
            return f"{num / 1_000_000:.2f}M"
        elif abs(num) >= 1_000:
            return f"{num / 1_000:.2f}K"
        elif num.is_integer():
            return str(int(num))
        else:
            return f"{num:.2f}"
    except (ValueError, TypeError):
        return str(num)

def safe_divide(a, b):
    """Safely divide two variables, returning 0 if b is 0."""
    try:
        return a / b if b != 0 else 0
    except (TypeError, ValueError):
        return 0

def get_memory_usage(df):
    """Return human readable memory usage of a dataframe."""
    mem = df.memory_usage(deep=True).sum()
    for unit in ['B', 'KB', 'MB', 'GB']:
        if mem < 1024.0:
            return f"{mem:.2f} {unit}"
        mem /= 1024.0
    return f"{mem:.2f} TB"

def timer_decorator(func):
    """Decorator that prints the execution time of a function."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f}s")
        return result
    return wrapper

def cache_decorator(func):
    """Applies Streamlit cache data decorator if applicable."""
    return st.cache_data(func)

def markdown_to_pdf_bytes(md_text):
    """Converts markdown text to a PDF bytearray for downloading."""
    # Strip non latin-1 characters (like emojis) which fpdf's default fonts do not support
    clean_text = md_text.encode('latin-1', 'ignore').decode('latin-1')
    
    html = markdown.markdown(clean_text)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    
    # fpdf2 write_html supports basic html tags mapped from markdown
    pdf.write_html(html)
    
    outbytes = pdf.output()
    return bytes(outbytes)
