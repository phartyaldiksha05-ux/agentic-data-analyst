"""
Correlation analysis utilities for the Agentic Data Analyst.

This module calculates Pearson correlation between numerical columns
and identifies strong positive and negative relationships.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _to_python_value(value: Any) -> Any:
    """Convert NumPy/Pandas values into JSON-serializable Python values."""

    if pd.isna(value):
        return None

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)

    return value


def _classify_correlation(value: float) -> str:
    """Classify correlation strength."""

    absolute_value = abs(value)

    if absolute_value >= 0.8:
        return "very strong"

    if absolute_value >= 0.6:
        return "strong"

    if absolute_value >= 0.4:
        return "moderate"

    if absolute_value >= 0.2:
        return "weak"

    return "very weak"


def calculate_correlation_matrix(
    df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Calculate Pearson correlation matrix for numerical columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.

    Returns
    -------
    dict
        JSON-serializable correlation matrix.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Cannot analyze an empty DataFrame.")

    numeric_df = df.select_dtypes(include=np.number)

    if numeric_df.shape[1] < 2:
        return {
            "status": "success",
            "message": "At least two numerical columns are required.",
            "columns": list(numeric_df.columns),
            "matrix": {},
        }

    correlation_matrix = numeric_df.corr(method="pearson")

    matrix = {}

    for column in correlation_matrix.columns:
        matrix[column] = {
            other_column: _to_python_value(
                correlation_matrix.loc[column, other_column]
            )
            for other_column in correlation_matrix.columns
        }

    return {
        "status": "success",
        "method": "pearson",
        "columns": list(numeric_df.columns),
        "matrix": matrix,
    }


def find_strong_correlations(
    df: pd.DataFrame,
    threshold: float = 0.6,
) -> dict[str, Any]:
    """
    Find strong positive and negative correlations.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.

    threshold : float, default=0.6
        Minimum absolute correlation value considered strong.

    Returns
    -------
    dict
        Strong correlation pairs.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Cannot analyze an empty DataFrame.")

    if not 0 < threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1.")

    numeric_df = df.select_dtypes(include=np.number)

    if numeric_df.shape[1] < 2:
        return {
            "status": "success",
            "message": "At least two numerical columns are required.",
            "strong_positive": [],
            "strong_negative": [],
        }

    correlation_matrix = numeric_df.corr(method="pearson")

    strong_positive = []
    strong_negative = []

    columns = correlation_matrix.columns

    # Only examine each pair once.
    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):

            column_a = columns[i]
            column_b = columns[j]

            correlation = correlation_matrix.loc[
                column_a, column_b
            ]

            if pd.isna(correlation):
                continue

            correlation = float(correlation)

            correlation_data = {
                "column_1": column_a,
                "column_2": column_b,
                "correlation": round(correlation, 4),
                "strength": _classify_correlation(correlation),
            }

            if correlation >= threshold:
                strong_positive.append(correlation_data)

            elif correlation <= -threshold:
                strong_negative.append(correlation_data)

    # Strongest relationships first.
    strong_positive.sort(
        key=lambda item: item["correlation"],
        reverse=True,
    )

    strong_negative.sort(
        key=lambda item: item["correlation"],
    )

    return {
        "status": "success",
        "threshold": threshold,
        "strong_positive": strong_positive,
        "strong_negative": strong_negative,
    }


def get_correlation_analysis(
    df: pd.DataFrame,
    threshold: float = 0.6,
) -> dict[str, Any]:
    """
    Generate complete correlation analysis.

    This function combines:
    - Correlation matrix
    - Strong positive correlations
    - Strong negative correlations
    """

    matrix_result = calculate_correlation_matrix(df)

    strong_result = find_strong_correlations(
        df,
        threshold=threshold,
    )

    return {
        "status": "success",
        "method": "pearson",
        "threshold": threshold,
        "matrix": matrix_result.get("matrix", {}),
        "strong_positive": strong_result.get(
            "strong_positive", []
        ),
        "strong_negative": strong_result.get(
            "strong_negative", []
        ),
    }


if __name__ == "__main__":
    # Local test dataset
    sample_data = {
        "Age": [22, 25, 28, 30, 35, 40],
        "Salary": [25000, 30000, 40000, 50000, 65000, 80000],
        "Experience": [1, 2, 4, 5, 8, 10],
        "Performance": [55, 60, 68, 75, 85, 92],
        "Department": [
            "IT",
            "IT",
            "HR",
            "IT",
            "Sales",
            "IT",
        ],
    }

    sample_df = pd.DataFrame(sample_data)

    print("\n=== CORRELATION MATRIX ===")

    matrix_result = calculate_correlation_matrix(sample_df)

    for column, correlations in matrix_result["matrix"].items():
        print(f"\n{column}:")
        for other_column, value in correlations.items():
            print(f"  {other_column}: {value}")

    print("\n=== STRONG CORRELATIONS ===")

    strong_result = find_strong_correlations(
        sample_df,
        threshold=0.6,
    )

    print("\nStrong Positive:")
    for item in strong_result["strong_positive"]:
        print(
            f"{item['column_1']} <-> {item['column_2']} : "
            f"{item['correlation']} "
            f"({item['strength']})"
        )

    print("\nStrong Negative:")
    for item in strong_result["strong_negative"]:
        print(
            f"{item['column_1']} <-> {item['column_2']} : "
            f"{item['correlation']} "
            f"({item['strength']})"
        )