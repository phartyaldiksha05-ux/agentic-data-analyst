"""
Outlier detection utilities for the Agentic Data Analyst.

This module uses the IQR (Interquartile Range) method to detect
potential outliers in numerical columns.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _to_python_value(value: Any) -> Any:
    """Convert NumPy/Pandas values to JSON-serializable Python values."""

    if pd.isna(value):
        return None

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)

    return value


def detect_outliers(df: pd.DataFrame) -> dict[str, Any]:
    """
    Detect potential outliers in all numerical columns using IQR.

    IQR = Q3 - Q1

    Lower Bound = Q1 - 1.5 * IQR
    Upper Bound = Q3 + 1.5 * IQR

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.

    Returns
    -------
    dict
        JSON-serializable outlier analysis results.
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
                "outlier_count": 0,
                "outlier_percentage": 0.0,
                "q1": None,
                "q3": None,
                "iqr": None,
                "lower_bound": None,
                "upper_bound": None,
                "outlier_values": [],
            }
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outlier_mask = (series < lower_bound) | (series > upper_bound)
        outliers = series[outlier_mask]

        outlier_count = int(outliers.count())
        total_values = int(series.count())

        outlier_percentage = (
            (outlier_count / total_values) * 100
            if total_values > 0
            else 0.0
        )

        results[column] = {
            "outlier_count": outlier_count,
            "outlier_percentage": round(outlier_percentage, 2),
            "q1": _to_python_value(q1),
            "q3": _to_python_value(q3),
            "iqr": _to_python_value(iqr),
            "lower_bound": _to_python_value(lower_bound),
            "upper_bound": _to_python_value(upper_bound),
            "outlier_values": [
                _to_python_value(value)
                for value in outliers.tolist()
            ],
        }

    return {
        "status": "success",
        "columns": results,
    }


def get_outlier_summary(df: pd.DataFrame) -> dict[str, Any]:
    """
    Generate a high-level summary of outliers in the dataset.

    Returns the total number of columns containing outliers and
    the total number of detected outlier values.
    """

    analysis = detect_outliers(df)

    if not analysis["columns"]:
        return {
            "status": "success",
            "columns_with_outliers": 0,
            "total_outliers": 0,
        }

    columns_with_outliers = 0
    total_outliers = 0

    for result in analysis["columns"].values():
        count = result["outlier_count"]

        if count > 0:
            columns_with_outliers += 1
            total_outliers += count

    return {
        "status": "success",
        "columns_with_outliers": columns_with_outliers,
        "total_outliers": total_outliers,
        "details": analysis["columns"],
    }


if __name__ == "__main__":
    # Local test dataset
    sample_data = {
        "Age": [22, 25, 28, 30, 35, 100],
        "Salary": [25000, 35000, 45000, 55000, 70000, 250000],
        "Experience": [1, 2, 4, 5, 8, 30],
        "Department": ["IT", "IT", "HR", "IT", "Sales", "IT"],
    }

    sample_df = pd.DataFrame(sample_data)

    print("\n=== OUTLIER DETECTION ===")

    result = detect_outliers(sample_df)

    for column, data in result["columns"].items():
        print(f"\n{column}")
        print(f"Q1: {data['q1']}")
        print(f"Q3: {data['q3']}")
        print(f"IQR: {data['iqr']}")
        print(f"Lower Bound: {data['lower_bound']}")
        print(f"Upper Bound: {data['upper_bound']}")
        print(f"Outlier Count: {data['outlier_count']}")
        print(f"Outlier Percentage: {data['outlier_percentage']}%")
        print(f"Outlier Values: {data['outlier_values']}")

    print("\n=== OUTLIER SUMMARY ===")
    print(get_outlier_summary(sample_df))