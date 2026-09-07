"""
Visualization utilities for the Agentic Data Analyst.

Generates reusable charts for numerical and categorical data:
- Histogram
- Box plot
- Bar chart
- Line chart
- Scatter plot
- Correlation heatmap
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_OUTPUT_DIR = Path("backend") / "uploads" / "charts"


def _validate_dataframe(df: pd.DataFrame) -> None:
    """Validate the input DataFrame."""

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Cannot create visualizations from an empty DataFrame.")


def _prepare_output_dir(output_dir: str | Path | None) -> Path:
    """Create and return the chart output directory."""

    directory = (
        Path(output_dir)
        if output_dir is not None
        else DEFAULT_OUTPUT_DIR
    )

    directory.mkdir(parents=True, exist_ok=True)

    return directory


def _safe_filename(value: str) -> str:
    """Create a safe filename from a column name."""

    safe_name = "".join(
        character if character.isalnum() or character in "_-" else "_"
        for character in str(value)
    )

    return safe_name.strip("_") or "chart"


def _save_figure(
    figure: plt.Figure,
    output_dir: Path,
    filename: str,
) -> str:
    """Save a matplotlib figure and close it."""

    output_path = output_dir / filename

    figure.tight_layout()
    figure.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close(figure)

    return str(output_path)


def create_histogram(
    df: pd.DataFrame,
    column: str,
    output_dir: str | Path | None = None,
) -> str:
    """
    Create a histogram for a numerical column.

    Returns
    -------
    str
        Path to the generated chart.
    """

    _validate_dataframe(df)

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    if not pd.api.types.is_numeric_dtype(df[column]):
        raise ValueError(
            f"Column '{column}' must be numerical for a histogram."
        )

    data = df[column].dropna()

    if data.empty:
        raise ValueError(f"Column '{column}' contains no valid values.")

    output_path = _prepare_output_dir(output_dir)

    figure, axis = plt.subplots(figsize=(8, 5))

    axis.hist(data, bins=10)

    axis.set_title(f"Distribution of {column}")
    axis.set_xlabel(column)
    axis.set_ylabel("Frequency")

    filename = f"histogram_{_safe_filename(column)}.png"

    return _save_figure(
        figure,
        output_path,
        filename,
    )


def create_box_plot(
    df: pd.DataFrame,
    column: str,
    output_dir: str | Path | None = None,
) -> str:
    """Create a box plot for a numerical column."""

    _validate_dataframe(df)

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    if not pd.api.types.is_numeric_dtype(df[column]):
        raise ValueError(
            f"Column '{column}' must be numerical for a box plot."
        )

    data = df[column].dropna()

    if data.empty:
        raise ValueError(f"Column '{column}' contains no valid values.")

    output_path = _prepare_output_dir(output_dir)

    figure, axis = plt.subplots(figsize=(8, 5))

    axis.boxplot(data)

    axis.set_title(f"Box Plot of {column}")
    axis.set_ylabel(column)

    filename = f"boxplot_{_safe_filename(column)}.png"

    return _save_figure(
        figure,
        output_path,
        filename,
    )


def create_bar_chart(
    df: pd.DataFrame,
    column: str,
    output_dir: str | Path | None = None,
    top_n: int = 10,
) -> str:
    """
    Create a bar chart showing category frequencies.
    """

    _validate_dataframe(df)

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    if top_n <= 0:
        raise ValueError("top_n must be greater than zero.")

    data = df[column].dropna()

    if data.empty:
        raise ValueError(f"Column '{column}' contains no valid values.")

    frequencies = data.value_counts().head(top_n)

    output_path = _prepare_output_dir(output_dir)

    figure, axis = plt.subplots(figsize=(8, 5))

    frequencies.plot(
        kind="bar",
        ax=axis,
    )

    axis.set_title(f"Category Distribution of {column}")
    axis.set_xlabel(column)
    axis.set_ylabel("Count")

    axis.tick_params(axis="x", rotation=45)

    filename = f"bar_{_safe_filename(column)}.png"

    return _save_figure(
        figure,
        output_path,
        filename,
    )


def create_line_chart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    output_dir: str | Path | None = None,
) -> str:
    """
    Create a line chart using two columns.
    """

    _validate_dataframe(df)

    for column in [x_column, y_column]:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' does not exist.")

    data = df[[x_column, y_column]].dropna()

    if data.empty:
        raise ValueError("No valid data available for line chart.")

    data = data.sort_values(by=x_column)

    output_path = _prepare_output_dir(output_dir)

    figure, axis = plt.subplots(figsize=(8, 5))

    axis.plot(
        data[x_column],
        data[y_column],
        marker="o",
    )

    axis.set_title(f"{y_column} Trend by {x_column}")
    axis.set_xlabel(x_column)
    axis.set_ylabel(y_column)

    filename = (
        f"line_{_safe_filename(x_column)}_"
        f"{_safe_filename(y_column)}.png"
    )

    return _save_figure(
        figure,
        output_path,
        filename,
    )


def create_scatter_plot(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    output_dir: str | Path | None = None,
) -> str:
    """
    Create a scatter plot between two numerical columns.
    """

    _validate_dataframe(df)

    for column in [x_column, y_column]:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' does not exist.")

        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(
                f"Column '{column}' must be numerical "
                "for a scatter plot."
            )

    data = df[[x_column, y_column]].dropna()

    if data.empty:
        raise ValueError("No valid data available for scatter plot.")

    output_path = _prepare_output_dir(output_dir)

    figure, axis = plt.subplots(figsize=(8, 5))

    axis.scatter(
        data[x_column],
        data[y_column],
    )

    axis.set_title(f"{y_column} vs {x_column}")
    axis.set_xlabel(x_column)
    axis.set_ylabel(y_column)

    filename = (
        f"scatter_{_safe_filename(x_column)}_"
        f"{_safe_filename(y_column)}.png"
    )

    return _save_figure(
        figure,
        output_path,
        filename,
    )


def create_correlation_heatmap(
    df: pd.DataFrame,
    output_dir: str | Path | None = None,
) -> str:
    """
    Create a correlation heatmap for numerical columns.
    """

    _validate_dataframe(df)

    numeric_df = df.select_dtypes(include=np.number)

    if numeric_df.shape[1] < 2:
        raise ValueError(
            "At least two numerical columns are required "
            "for a correlation heatmap."
        )

    correlation_matrix = numeric_df.corr()

    output_path = _prepare_output_dir(output_dir)

    figure, axis = plt.subplots(figsize=(9, 7))

    image = axis.imshow(
        correlation_matrix,
        aspect="auto",
    )

    axis.set_xticks(range(len(correlation_matrix.columns)))
    axis.set_yticks(range(len(correlation_matrix.columns)))

    axis.set_xticklabels(
        correlation_matrix.columns,
        rotation=45,
        ha="right",
    )

    axis.set_yticklabels(
        correlation_matrix.columns,
    )

    # Display correlation values inside cells.
    for row in range(len(correlation_matrix)):
        for column in range(len(correlation_matrix)):
            value = correlation_matrix.iloc[row, column]

            if not pd.isna(value):
                axis.text(
                    column,
                    row,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                )

    figure.colorbar(image, ax=axis)

    axis.set_title("Correlation Heatmap")

    filename = "correlation_heatmap.png"

    return _save_figure(
        figure,
        output_path,
        filename,
    )


def generate_visualizations(
    df: pd.DataFrame,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """
    Automatically generate useful visualizations for a dataset.

    Rules:
    - Numerical columns → histogram + box plot
    - Categorical columns → bar chart
    - First two numerical columns → scatter plot
    - First numerical column pair → line chart
    - Two or more numerical columns → correlation heatmap
    """

    _validate_dataframe(df)

    output_path = _prepare_output_dir(output_dir)

    numerical_columns = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        exclude=np.number
    ).columns.tolist()

    charts: list[dict[str, Any]] = []

    # Numerical visualizations
    for column in numerical_columns:

        try:
            path = create_histogram(
                df,
                column,
                output_path,
            )

            charts.append(
                {
                    "type": "histogram",
                    "column": column,
                    "path": path,
                }
            )

        except (ValueError, TypeError):
            pass

        try:
            path = create_box_plot(
                df,
                column,
                output_path,
            )

            charts.append(
                {
                    "type": "box_plot",
                    "column": column,
                    "path": path,
                }
            )

        except (ValueError, TypeError):
            pass

    # Categorical visualizations
    for column in categorical_columns:

        try:
            path = create_bar_chart(
                df,
                column,
                output_path,
            )

            charts.append(
                {
                    "type": "bar_chart",
                    "column": column,
                    "path": path,
                }
            )

        except (ValueError, TypeError):
            pass

    # Scatter plot
    if len(numerical_columns) >= 2:

        try:
            x_column = numerical_columns[0]
            y_column = numerical_columns[1]

            path = create_scatter_plot(
                df,
                x_column,
                y_column,
                output_path,
            )

            charts.append(
                {
                    "type": "scatter_plot",
                    "x_column": x_column,
                    "y_column": y_column,
                    "path": path,
                }
            )

        except (ValueError, TypeError):
            pass

    # Line chart
    if len(numerical_columns) >= 2:

        try:
            x_column = numerical_columns[0]
            y_column = numerical_columns[1]

            path = create_line_chart(
                df,
                x_column,
                y_column,
                output_path,
            )

            charts.append(
                {
                    "type": "line_chart",
                    "x_column": x_column,
                    "y_column": y_column,
                    "path": path,
                }
            )

        except (ValueError, TypeError):
            pass

    # Correlation heatmap
    if len(numerical_columns) >= 2:

        try:
            path = create_correlation_heatmap(
                df,
                output_path,
            )

            charts.append(
                {
                    "type": "correlation_heatmap",
                    "path": path,
                }
            )

        except (ValueError, TypeError):
            pass

    return {
        "status": "success",
        "chart_count": len(charts),
        "charts": charts,
    }


if __name__ == "__main__":

    sample_data = {
        "Age": [22, 25, 28, 30, 35, 40],
        "Salary": [25000, 30000, 40000, 50000, 65000, 80000],
        "Experience": [1, 2, 4, 5, 8, 10],
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

    print("\n=== AUTOMATIC VISUALIZATION ===")

    result = generate_visualizations(sample_df)

    print(f"\nCharts generated: {result['chart_count']}")

    for chart in result["charts"]:
        print(
            f"{chart['type']} -> {chart['path']}"
        )