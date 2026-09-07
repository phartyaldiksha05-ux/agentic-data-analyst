"""
Dataset profiling: inspect a DataFrame and summarize its shape and quality.
This output is what gets handed to the AI Planner Agent (Diksha's module).
"""

import pandas as pd
import numpy as np


def profile_dataframe(df: pd.DataFrame) -> dict:
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    missing_values = df.isnull().sum()
    missing_values_dict = {
        col: int(count) for col, count in missing_values.items() if count > 0
    }

    unique_values = {col: int(df[col].nunique()) for col in df.columns}

    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}

    profile = {
        "num_rows": int(df.shape[0]),
        "num_columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "dtypes": dtypes,
        "missing_values": missing_values_dict,
        "total_missing_values": int(missing_values.sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "unique_values": unique_values,
        "numerical_columns": numerical_cols,
        "categorical_columns": categorical_cols,
    }

    return profile
