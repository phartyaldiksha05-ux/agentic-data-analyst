"""
Data cleaning functions for the Agentic Data Analyst MVP.
"""

import pandas as pd
import numpy as np


def fill_missing_numerical(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing numeric values with the column median."""
    df = df.copy()
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    for col in numerical_cols:
        if df[col].isnull().any():
            median_value = df[col].median()
            df[col] = df[col].fillna(median_value)
    return df


def fill_missing_categorical(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing categorical values with the column mode (most frequent value)."""
    df = df.copy()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns
    for col in categorical_cols:
        if df[col].isnull().any():
            mode_series = df[col].mode(dropna=True)
            if not mode_series.empty:
                df[col] = df[col].fillna(mode_series[0])
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop exact duplicate rows."""
    return df.drop_duplicates().reset_index(drop=True)


def convert_basic_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Try to convert object columns that are actually numeric or dates
    into proper types. Safe no-op if conversion fails.
    """
    df = df.copy()
    for col in df.select_dtypes(include="object").columns:
        # Try numeric conversion first
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() >= 0.9 * df[col].notna().sum() and df[col].notna().sum() > 0:
            df[col] = converted
            continue

        # Try datetime conversion
        try:
            converted_dates = pd.to_datetime(df[col], errors="coerce")
            if converted_dates.notna().sum() >= 0.9 * df[col].notna().sum() and df[col].notna().sum() > 0:
                df[col] = converted_dates
        except (ValueError, TypeError):
            pass
    return df


def clean_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Run the full cleaning pipeline and return the cleaned dataframe
    plus a summary of what was changed (useful for the AI insights step).
    """
    original_rows = df.shape[0]
    original_missing = int(df.isnull().sum().sum())

    df = convert_basic_types(df)
    df = fill_missing_numerical(df)
    df = fill_missing_categorical(df)
    df = remove_duplicates(df)

    summary = {
        "rows_before": original_rows,
        "rows_after": int(df.shape[0]),
        "duplicates_removed": original_rows - int(df.shape[0]),
        "missing_values_before": original_missing,
        "missing_values_after": int(df.isnull().sum().sum()),
    }

    return df, summary
