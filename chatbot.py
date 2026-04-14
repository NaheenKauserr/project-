import os
import google.generativeai as genai
import streamlit as st
import json

def chat_response(query, df, column_types):
    """
    Handles the chatbot responses and visualization generation.
    Returns: dict {"text": string, "code": string/None}
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_key_here":
        return {"text": "⚠️ Add GEMINI_API_KEY to .env to enable the chatbot.", "code": None}
        
    if df is None or df.empty:
        return {"text": "No dataset is currently loaded.", "code": None}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Prepare Data Context
        col_names = list(df.columns)
        row_cnt = len(df)
        
        # Only take a tiny sample
        sample_df = df.head(5)
        sample_csv = sample_df.to_csv(index=False)
        
        system_instructions = (
            "You are an expert Data Analyst AI for a premium dashboard. "
            "You are provided with a dataset context. The user will ask questions.\n"
            "If the question just needs a text answer, provide it clearly.\n"
            "If the question requires a visual chart (plot, graph, etc), you MUST generate valid python code using 'plotly.express as px' to create a figure named `fig`. "
            "The dataframe is available as `df`.\n"
            "IMPORTANT PLOTLY STYLING:\n"
            "- Use plot_bgcolor='white', paper_bgcolor='white'.\n"
            "- Use main color `#7367f0` for bars/lines.\n"
            "- Use font Inter.\n"
            "Wrap ONLY your code tightly in a ```python block."
        )
        
        context = (
            f"Dataset context:\n"
            f"- Columns: {col_names}\n"
            f"- Shape: {row_cnt} rows\n"
            f"- Sample data:\n{sample_csv}\n\n"
        )
        
        prompt = system_instructions + "\n\n" + context + f"User Question: {query}"
        
        chat = model.start_chat()
        response = chat.send_message(prompt)
        text_resp = response.text
        
        # Parse for code
        import re
        code_match = re.search(r'```python(.*?)```', text_resp, re.DOTALL)
        code = None
        if code_match:
            code = code_match.group(1).strip()
            # Remove the code block from the text response
            text_resp = text_resp.replace(code_match.group(0), "").strip()
            if not text_resp:
                text_resp = "Here is the visualization you requested:"
                
        return {"text": text_resp, "code": code}
        
    except Exception as e:
        return {"text": f"⚠️ Chat error: {str(e)}", "code": None}


