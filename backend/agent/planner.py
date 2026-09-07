"""
Rule-based planner for the Agentic Data Analyst AI Agent.

Given a `DatasetProfile`, decides which analysis tools are relevant and
produces an ordered `AnalysisPlan`. This is a deterministic, rule-based
implementation so the MVP works end-to-end without any LLM API.

A future LLM-based planner can be implemented separately and swapped in
behind the same `generate_plan(profile) -> AnalysisPlan` interface — no
changes to `schemas.py` or to callers would be required.
"""

from __future__ import annotations

import logging
from typing import List, Tuple

from .schemas import AnalysisPlan, AnalysisStep, ColumnProfile, ColumnType, DatasetProfile

logger = logging.getLogger(__name__)


class AnalysisTool:
    """Canonical tool name constants, to avoid magic strings/typos elsewhere."""

    DATA_CLEANING = "data_cleaning"
    DESCRIPTIVE_STATISTICS = "descriptive_statistics"
    CATEGORICAL_ANALYSIS = "categorical_analysis"
    CORRELATION_ANALYSIS = "correlation_analysis"
    DISTRIBUTION_VISUALIZATION = "distribution_visualization"
    CATEGORICAL_VISUALIZATION = "categorical_visualization"
    OUTLIER_DETECTION = "outlier_detection"
    TIME_SERIES_ANALYSIS = "time_series_analysis"


class PlannerError(Exception):
    """Raised when the planner cannot produce a valid analysis plan."""


class RuleBasedPlanner:
    """
    Deterministic, rule-based analysis planner.

    Rules
    -----
    - missing values > 0            -> data_cleaning
    - duplicate rows > 0            -> data_cleaning (merged with the above)
    - >= 1 numeric column           -> descriptive_statistics
    - >= 1 categorical column       -> categorical_analysis
    - >= 2 numeric columns          -> correlation_analysis
    - numeric column(s) present     -> distribution_visualization
    - categorical column(s) present -> categorical_visualization
    - numeric column(s) present     -> outlier_detection
    - datetime column(s) present    -> time_series_analysis

    Usage
    -----
    >>> planner = RuleBasedPlanner()
    >>> plan = planner.generate_plan(profile)
    >>> plan.model_dump()  # JSON-serializable dict
    """

    def generate_plan(self, profile: DatasetProfile) -> AnalysisPlan:
        """
        Generate an ordered analysis plan for the given dataset profile.

        Args:
            profile: A validated `DatasetProfile` instance.

        Returns:
            An `AnalysisPlan` containing the ordered, reasoned list of steps.

        Raises:
            PlannerError: if `profile` is not a `DatasetProfile`, or has no
                columns to reason about.
        """
        self._validate_input(profile)

        logger.info(
            "Generating analysis plan for dataset '%s' (%d rows, %d columns, %d duplicate rows)",
            profile.dataset_name,
            profile.rows,
            len(profile.columns),
            profile.duplicate_rows,
        )

        numeric_cols = self._columns_of_type(profile.columns, ColumnType.NUMERIC)
        categorical_cols = self._columns_of_type(profile.columns, ColumnType.CATEGORICAL)
        datetime_cols = self._columns_of_type(profile.columns, ColumnType.DATETIME)
        total_missing = sum(column.missing_count for column in profile.columns)

        # Each entry is (tool_name, reason). Order here defines execution order.
        candidates: List[Tuple[str, str]] = []

        cleaning_reasons = []
        if total_missing > 0:
            cleaning_reasons.append(f"{total_missing} missing value(s) detected across columns")
        if profile.duplicate_rows > 0:
            cleaning_reasons.append(f"{profile.duplicate_rows} duplicate row(s) detected")
        if cleaning_reasons:
            candidates.append((AnalysisTool.DATA_CLEANING, "; ".join(cleaning_reasons)))

        if numeric_cols:
            candidates.append((
                AnalysisTool.DESCRIPTIVE_STATISTICS,
                f"{len(numeric_cols)} numeric column(s) detected: {self._names(numeric_cols)}",
            ))

        if categorical_cols:
            candidates.append((
                AnalysisTool.CATEGORICAL_ANALYSIS,
                f"{len(categorical_cols)} categorical column(s) detected: {self._names(categorical_cols)}",
            ))

        if len(numeric_cols) >= 2:
            candidates.append((
                AnalysisTool.CORRELATION_ANALYSIS,
                f"{len(numeric_cols)} numeric columns present, correlation analysis is applicable",
            ))

        if numeric_cols:
            candidates.append((
                AnalysisTool.DISTRIBUTION_VISUALIZATION,
                f"Numeric column(s) present, distributions can be visualized: {self._names(numeric_cols)}",
            ))

        if categorical_cols:
            candidates.append((
                AnalysisTool.CATEGORICAL_VISUALIZATION,
                "Categorical column(s) present, category frequencies can be visualized: "
                f"{self._names(categorical_cols)}",
            ))

        if numeric_cols:
            candidates.append((
                AnalysisTool.OUTLIER_DETECTION,
                f"Numeric column(s) present, outlier detection is applicable: {self._names(numeric_cols)}",
            ))

        if datetime_cols:
            candidates.append((
                AnalysisTool.TIME_SERIES_ANALYSIS,
                f"Date/datetime column(s) detected: {self._names(datetime_cols)}",
            ))

        if not candidates:
            logger.warning(
                "No applicable analysis steps found for dataset '%s' — profile may be empty of "
                "recognizable column types",
                profile.dataset_name,
            )

        steps = [
            AnalysisStep(step=index, tool=tool, reason=reason)
            for index, (tool, reason) in enumerate(candidates, start=1)
        ]

        logger.info("Generated %d step(s) for dataset '%s'", len(steps), profile.dataset_name)
        return AnalysisPlan(analysis_plan=steps)

    @staticmethod
    def _validate_input(profile: DatasetProfile) -> None:
        """Guard against invalid input before running any planning rules."""
        if not isinstance(profile, DatasetProfile):
            raise PlannerError(
                f"Expected a DatasetProfile instance, got {type(profile).__name__}"
            )
        if not profile.columns:
            # DatasetProfile's own validator should already prevent this,
            # but the planner stays defensive in case profile is constructed
            # via model_construct() or similar, bypassing validation.
            raise PlannerError("Cannot generate a plan for a dataset with no columns")

    @staticmethod
    def _columns_of_type(columns: List[ColumnProfile], col_type: ColumnType) -> List[ColumnProfile]:
        """Filter columns down to a specific `ColumnType`."""
        return [column for column in columns if column.type == col_type]

    @staticmethod
    def _names(columns: List[ColumnProfile]) -> str:
        """Comma-joined column names, used for readable `reason` strings."""
        return ", ".join(column.name for column in columns)
