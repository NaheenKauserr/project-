import pandas as pd
import numpy as np

_LAST_CLEANING_REPORT = {}

def clean_data(df):
    """
    Cleans DataFrame:
    - Removes duplicates
    - Fills numeric missing with median
    - Fills text missing with mode
    - Converts strings to dates if applicable
    - Converts convertible string columns to numeric
    Returns the cleaned dataframe.
    """
    import copy
    global _LAST_CLEANING_REPORT
    
    if df is None or df.empty:
        return df
        
    cleaned = df.copy()
    report = {
        "initial_rows": len(cleaned),
        "duplicates_removed": 0,
        "missing_filled": 0,
        "date_conversions": [],
        "numeric_conversions": []
    }
    
    # Remove duplicates
    dupes = cleaned.duplicated().sum()
    if dupes > 0:
        cleaned.drop_duplicates(inplace=True)
        report["duplicates_removed"] = int(dupes)
        
    # Track missing before fill
    missing_sum = cleaned.isnull().sum().sum()
    report["missing_filled"] = int(missing_sum)
    
    # Fill missing values dynamically
    for col in cleaned.columns:
        if cleaned[col].isnull().any():
            # If numeric, fill with median
            if pd.api.types.is_numeric_dtype(cleaned[col]):
                # if all are nan, fill with 0
                median_val = cleaned[col].median()
                if pd.isna(median_val):
                    median_val = 0
                cleaned[col] = cleaned[col].fillna(median_val)
            else:
                # categorical or string, fill with mode
                mode_vals = cleaned[col].mode()
                mode_val = mode_vals.iloc[0] if not mode_vals.empty else "Unknown"
                cleaned[col] = cleaned[col].fillna(mode_val)
                
    # Auto convert string to dates where reasonable
    for col in cleaned.select_dtypes(include=['object']):
        # Ignore columns that are clearly just text/categorical with low unique count
        if cleaned[col].nunique() > 1:
            try:
                # just check first non-null sample
                sample = cleaned[col].dropna().iloc[0]
                if isinstance(sample, str) and ANY_DATE_HINTS(col, sample):
                    cleaned[col] = pd.to_datetime(cleaned[col], errors='ignore')
                    if pd.api.types.is_datetime64_any_dtype(cleaned[col]):
                        report["date_conversions"].append(col)
            except Exception:
                pass

        # Try to convert string to numeric if possible
        try:
            temp = pd.to_numeric(cleaned[col], errors='coerce')
            # If more than 50% are valid numbers after cast, let's keep it
            if temp.notna().sum() / len(temp) > 0.5:
                # fill remaining NaNs with median
                median_val = temp.median()
                if pd.isna(median_val):
                    median_val = 0
                cleaned[col] = temp.fillna(median_val)
                report["numeric_conversions"].append(col)
        except Exception:
            pass

    _LAST_CLEANING_REPORT = report
    return cleaned

def ANY_DATE_HINTS(col_name, sample_val):
    c = col_name.lower()
    if any(k in c for k in ['date', 'time', 'year', 'month', 'day']):
        return True
    try:
        # Check simple date format parse
        pd.to_datetime([sample_val])
        return True
    except:
        return False

def get_cleaning_report():
    """Returns the dictionary generated during the last clean_data execution."""
    global _LAST_CLEANING_REPORT
    return _LAST_CLEANING_REPORT.copy()

