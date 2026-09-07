"""
Statistical analysis utilities for the Agentic Data Analyst.

This module provides reusable functions for:
- Descriptive statistics
- Numerical column analysis
- Dataset-level statistical summaries

All functions accept a Pandas DataFrame and return
JSON-serializable Python dictionaries so they can be
used easily by FastAPI and the AI analysis agent.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _to_python_value(value: Any) -> Any:
    """
    Convert NumPy/Pandas values into JSON-serializable Python values.

    Parameters
    ----------
    value:
        Any Pandas/NumPy/Python value.

    Returns
    -------
    Any
        JSON-compatible Python value.
    """
    if pd.isna(value):
        return None

    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating,)):
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)

    if isinstance(value, (np.bool_,)):
        return bool(value)

    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()

    return value


def get_descriptive_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """
    Calculate descriptive statistics for all numerical columns.

    Statistics returned for each numerical column:
    - count
    - mean
    - median
    - minimum
    - maximum
    - standard deviation
    - 25th percentile
    - 50th percentile
    - 75th percentile

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.

    Returns
    -------
    dict
        Dictionary containing descriptive statistics.

    Raises
    ------
    TypeError
        If df is not a Pandas DataFrame.
    ValueError
        If the DataFrame is empty.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Cannot analyze an empty DataFrame.")

    numeric_df = df.select_dtypes(include=np.number)

    if numeric_df.empty:
        return {
            "status": "success",
            "message": "No numerical columns found.",
            "columns": {},
        }

    results: dict[str, Any] = {}

    for column in numeric_df.columns:
        series = numeric_df[column].dropna()

        if series.empty:
            results[column] = {
                "count": 0,
                "mean": None,
                "median": None,
                "min": None,
                "max": None,
                "std": None,
                "q1": None,
                "q2": None,
                "q3": None,
            }
            continue

        results[column] = {
            "count": int(series.count()),
            "mean": _to_python_value(series.mean()),
            "median": _to_python_value(series.median()),
            "min": _to_python_value(series.min()),
            "max": _to_python_value(series.max()),
            "std": _to_python_value(series.std()),
            "q1": _to_python_value(series.quantile(0.25)),
            "q2": _to_python_value(series.quantile(0.50)),
            "q3": _to_python_value(series.quantile(0.75)),
        }

    return {
        "status": "success",
        "columns": results,
    }


def analyze_numerical_columns(df: pd.DataFrame) -> dict[str, Any]:
    """
    Analyze all numerical columns in a dataset.

    Provides:
    - Data type
    - Total values
    - Non-null values
    - Missing values
    - Unique values
    - Mean
    - Median
    - Minimum
    - Maximum
    - Standard deviation
    - Range

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.

    Returns
    -------
    dict
        Structured numerical analysis results.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Cannot analyze an empty DataFrame.")

    numeric_df = df.select_dtypes(include=np.number)

    results: dict[str, Any] = {}

    for column in numeric_df.columns:
        series = numeric_df[column]

        non_null = series.dropna()

        if non_null.empty:
            results[column] = {
                "dtype": str(series.dtype),
                "total_values": int(len(series)),
                "non_null_values": 0,
                "missing_values": int(series.isna().sum()),
                "unique_values": 0,
                "mean": None,
                "median": None,
                "min": None,
                "max": None,
                "std": None,
                "range": None,
            }
            continue

        minimum = non_null.min()
        maximum = non_null.max()

        results[column] = {
            "dtype": str(series.dtype),
            "total_values": int(len(series)),
            "non_null_values": int(series.notna().sum()),
            "missing_values": int(series.isna().sum()),
            "unique_values": int(series.nunique()),
            "mean": _to_python_value(non_null.mean()),
            "median": _to_python_value(non_null.median()),
            "min": _to_python_value(minimum),
            "max": _to_python_value(maximum),
            "std": _to_python_value(non_null.std()),
            "range": _to_python_value(maximum - minimum),
        }

    return {
        "status": "success",
        "numerical_columns": list(numeric_df.columns),
        "column_count": len(numeric_df.columns),
        "analysis": results,
    }


def get_dataset_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """
    Generate a high-level statistical summary of the dataset.

    This function combines useful dataset-level information with
    numerical descriptive statistics.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.

    Returns
    -------
    dict
        Complete statistical summary.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Cannot analyze an empty DataFrame.")

    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()

    return {
        "status": "success",
        "dataset": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "numerical_columns": numeric_columns,
            "numerical_column_count": len(numeric_columns),
        },
        "descriptive_statistics": get_descriptive_statistics(df),
        "numerical_analysis": analyze_numerical_columns(df),
    }


if __name__ == "__main__":
    # Simple local test
    sample_data = {
        "Age": [22, 25, 28, 30, 35],
        "Salary": [25000, 35000, 45000, 55000, 70000],
        "Experience": [1, 2, 4, 5, 8],
        "Department": ["IT", "IT", "HR", "IT", "Sales"],
    }

    sample_df = pd.DataFrame(sample_data)

    print("\n=== DESCRIPTIVE STATISTICS ===")
    print(get_descriptive_statistics(sample_df))

    print("\n=== NUMERICAL ANALYSIS ===")
    print(analyze_numerical_columns(sample_df))

    print("\n=== COMPLETE DATASET STATISTICS ===")
    print(get_dataset_statistics(sample_df))