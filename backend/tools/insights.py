"""
Rule-Based Insights Engine
---------------------------
Generates automatic, human-readable insights from a pandas DataFrame.

This module is designed to be reusable by:
- FastAPI backend
- AI Agent
- Analysis pipeline
- Dashboard / report generation
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def _to_python_value(value: Any) -> Any:
    """Convert pandas/numpy values into JSON-friendly Python values."""
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass

    return value


def _validate_dataframe(df: pd.DataFrame) -> None:
    """Validate that the input is a non-empty DataFrame."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("DataFrame is empty.")


def generate_numerical_insights(df: pd.DataFrame) -> list[str]:
    """
    Generate insights for numerical columns.

    Includes:
    - highest/lowest values
    - average values
    - range information
    """
    numerical_df = df.select_dtypes(include="number")
    insights: list[str] = []

    for column in numerical_df.columns:
        series = numerical_df[column].dropna()

        if series.empty:
            continue

        mean_value = series.mean()
        min_value = series.min()
        max_value = series.max()

        insights.append(
            f"{column} has an average value of {mean_value:.2f}, "
            f"with a minimum of {min_value} and a maximum of {max_value}."
        )

        if mean_value != 0:
            if max_value > mean_value * 1.5:
                insights.append(
                    f"{column} has some relatively high values compared with "
                    f"its average."
                )

            if min_value < mean_value * 0.5:
                insights.append(
                    f"{column} has some relatively low values compared with "
                    f"its average."
                )

    return insights


def generate_categorical_insights(df: pd.DataFrame) -> list[str]:
    """
    Generate insights for categorical columns.

    Includes:
    - most common category
    - frequency
    - percentage distribution
    """
    categorical_df = df.select_dtypes(include=["object", "category", "bool"])
    insights: list[str] = []

    for column in categorical_df.columns:
        series = categorical_df[column].dropna()

        if series.empty:
            continue

        value_counts = series.value_counts()

        if value_counts.empty:
            continue

        most_common = value_counts.index[0]
        frequency = int(value_counts.iloc[0])
        percentage = (frequency / len(series)) * 100

        insights.append(
            f"{column}: '{most_common}' is the most common category, "
            f"appearing {frequency} times ({percentage:.2f}% of non-missing values)."
        )

    return insights


def generate_missing_value_insights(df: pd.DataFrame) -> list[str]:
    """Generate insights about missing values."""
    insights: list[str] = []

    missing_counts = df.isnull().sum()

    for column, count in missing_counts.items():
        count = int(count)

        if count > 0:
            percentage = (count / len(df)) * 100

            insights.append(
                f"{column} contains {count} missing value(s) "
                f"({percentage:.2f}% of the dataset)."
            )

    if missing_counts.sum() == 0:
        insights.append("No missing values were detected in the dataset.")

    return insights


def generate_distribution_insights(df: pd.DataFrame) -> list[str]:
    """
    Generate simple distribution-related insights.

    Uses mean and median to identify potential skewness.
    """
    numerical_df = df.select_dtypes(include="number")
    insights: list[str] = []

    for column in numerical_df.columns:
        series = numerical_df[column].dropna()

        if len(series) < 3:
            continue

        mean_value = series.mean()
        median_value = series.median()

        if median_value == 0:
            continue

        difference = abs(mean_value - median_value) / abs(median_value)

        if difference >= 0.20:
            if mean_value > median_value:
                insights.append(
                    f"{column} appears to be positively skewed because "
                    f"the mean is noticeably higher than the median."
                )
            else:
                insights.append(
                    f"{column} appears to be negatively skewed because "
                    f"the mean is noticeably lower than the median."
                )

    return insights


def generate_correlation_insights(
    df: pd.DataFrame,
    threshold: float = 0.6,
) -> list[str]:
    """
    Generate insights from strong correlations between numerical columns.
    """
    numerical_df = df.select_dtypes(include="number")

    if numerical_df.shape[1] < 2:
        return []

    correlation_matrix = numerical_df.corr()

    insights: list[str] = []
    columns = list(correlation_matrix.columns)

    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            col1 = columns[i]
            col2 = columns[j]

            correlation = correlation_matrix.loc[col1, col2]

            if pd.isna(correlation):
                continue

            if abs(correlation) >= threshold:
                strength = "strong"

                if abs(correlation) >= 0.8:
                    strength = "very strong"

                direction = (
                    "positive"
                    if correlation > 0
                    else "negative"
                )

                insights.append(
                    f"{col1} and {col2} have a {strength} {direction} "
                    f"correlation (r = {correlation:.2f})."
                )

    return insights


def generate_outlier_insights(df: pd.DataFrame) -> list[str]:
    """
    Generate simple outlier insights using the IQR method.
    """
    numerical_df = df.select_dtypes(include="number")
    insights: list[str] = []

    for column in numerical_df.columns:
        series = numerical_df[column].dropna()

        if len(series) < 4:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outliers = series[
            (series < lower_bound) | (series > upper_bound)
        ]

        outlier_count = len(outliers)

        if outlier_count > 0:
            percentage = (outlier_count / len(series)) * 100

            insights.append(
                f"{column} contains {outlier_count} potential outlier(s) "
                f"({percentage:.2f}% of non-missing values)."
            )

    if not insights:
        insights.append("No potential outliers were detected using the IQR method.")

    return insights


def generate_insights(df: pd.DataFrame) -> dict[str, Any]:
    """
    Generate a complete rule-based insight report.

    Returns a JSON-friendly dictionary that can directly
    be consumed by FastAPI or another backend service.
    """
    _validate_dataframe(df)

    numerical_columns = list(
        df.select_dtypes(include="number").columns
    )

    categorical_columns = list(
        df.select_dtypes(include=["object", "category", "bool"]).columns
    )

    numerical_insights = generate_numerical_insights(df)
    categorical_insights = generate_categorical_insights(df)
    missing_insights = generate_missing_value_insights(df)
    distribution_insights = generate_distribution_insights(df)
    correlation_insights = generate_correlation_insights(df)
    outlier_insights = generate_outlier_insights(df)

    all_insights = (
        numerical_insights
        + categorical_insights
        + missing_insights
        + distribution_insights
        + correlation_insights
        + outlier_insights
    )

    return {
        "dataset": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "numerical_columns": numerical_columns,
            "categorical_columns": categorical_columns,
        },
        "insights": all_insights,
        "categories": {
            "numerical": numerical_insights,
            "categorical": categorical_insights,
            "missing_values": missing_insights,
            "distribution": distribution_insights,
            "correlation": correlation_insights,
            "outliers": outlier_insights,
        },
        "total_insights": len(all_insights),
    }


if __name__ == "__main__":
    # ---------------------------------------------------------
    # Local test
    # ---------------------------------------------------------

    sample_data = {
        "Name": ["A", "B", "C", "D", "E"],
        "Department": [
            "IT",
            "IT",
            "HR",
            "IT",
            "Finance",
        ],
        "Age": [22, 25, 30, 35, 28],
        "Salary": [25000, 35000, 45000, 55000, 70000],
        "Experience": [1, 2, 4, 5, 8],
        "Performance": [60, 70, 80, 90, 95],
    }

    df = pd.DataFrame(sample_data)

    print("\n=== RULE-BASED INSIGHTS ===\n")

    result = generate_insights(df)

    print(f"Rows: {result['dataset']['rows']}")
    print(f"Columns: {result['dataset']['columns']}")
    print(f"Total Insights: {result['total_insights']}")

    print("\n--- Insights ---")

    for index, insight in enumerate(result["insights"], start=1):
        print(f"{index}. {insight}")