"""
Agent Orchestrator
------------------
The integration layer that turns a `dataset_id` into a full analysis run:

    fetch dataset -> profile it -> adapt profile -> plan -> execute plan -> aggregate

It calls existing team modules directly (`services.*`, `tools.*`) and does
not modify any of them. Its only job is coordination:

- Build the Agent's `DatasetProfile` from the existing profiler's output
  (via `profile_adapter`).
- Ask the existing `RuleBasedPlanner` what to do.
- Dispatch each planned step to the matching existing tool function, via a
  small tool registry (`TOOL_REGISTRY`).
- Never let one failing/missing tool take down the whole analysis — every
  step is executed independently and reports its own status.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from services.store import get_dataset, update_dataset
from services.profiler import profile_dataframe
from services.cleaning import clean_dataset
from tools.statistics import get_dataset_statistics
from tools.correlation import get_correlation_analysis
from tools.outliers import get_outlier_summary
from tools.visualization import generate_visualizations
from tools.insights import generate_categorical_insights

from .planner import AnalysisTool, PlannerError, RuleBasedPlanner
from .profile_adapter import ProfileAdapterError, adapt_profile

logger = logging.getLogger(__name__)


class OrchestratorError(Exception):
    """Base class for orchestrator-level failures (stop the whole run)."""


class DatasetNotFoundError(OrchestratorError):
    """Raised when the given dataset_id does not exist in the store."""


class StepStatus:
    """Status constants for individual step results."""

    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Tool handlers
#
# Each handler has the signature (df, context) -> dict, where `context` is a
# mutable dict shared across all steps in a single run. It's used for two
# things:
#   - `context["working_df"]`: the dataframe subsequent steps should use
#     (updated in place by data_cleaning, since cleaning should affect every
#     step that runs after it).
#   - caching the (expensive) visualization output so that
#     distribution_visualization and categorical_visualization — which both
#     map onto the same underlying `generate_visualizations()` call — only
#     run matplotlib once per analysis run.
# ---------------------------------------------------------------------------


def _run_data_cleaning(df: pd.DataFrame, context: dict) -> dict:
    """Run the existing cleaning pipeline and update the working dataframe."""
    cleaned_df, summary = clean_dataset(df)
    context["working_df"] = cleaned_df
    context["dataset_was_cleaned"] = True
    return {"cleaning_summary": summary}


def _run_descriptive_statistics(df: pd.DataFrame, context: dict) -> dict:
    """Run the existing full statistics tool."""
    return get_dataset_statistics(df)


def _run_categorical_analysis(df: pd.DataFrame, context: dict) -> dict:
    """
    No dedicated categorical-statistics tool exists yet. The closest existing
    functionality is `tools.insights.generate_categorical_insights`, which
    reports the most common category per column, so we reuse that here
    rather than duplicating category-frequency logic.
    """
    insights = generate_categorical_insights(df)
    return {
        "categorical_insights": insights,
        "note": (
            "No dedicated categorical_analysis tool exists yet; reused "
            "tools.insights.generate_categorical_insights as the closest "
            "available functionality."
        ),
    }


def _run_correlation_analysis(df: pd.DataFrame, context: dict) -> dict:
    """Run the existing correlation tool with its default threshold."""
    return get_correlation_analysis(df, threshold=0.6)


def _get_or_generate_visualizations(df: pd.DataFrame, context: dict) -> dict:
    """
    `tools.visualization.generate_visualizations` produces every chart type
    (numeric + categorical + scatter/line/heatmap) in one pass. Both
    visualization steps below need it, so it's cached in `context` and only
    actually executed once per analysis run.
    """
    if "visualizations" not in context:
        context["visualizations"] = generate_visualizations(df)
    return context["visualizations"]


_NUMERIC_CHART_TYPES = {
    "histogram",
    "box_plot",
    "scatter_plot",
    "line_chart",
    "correlation_heatmap",
}


def _run_distribution_visualization(df: pd.DataFrame, context: dict) -> dict:
    """Return the subset of generated charts that cover numeric distributions."""
    all_charts = _get_or_generate_visualizations(df, context)
    charts = [c for c in all_charts.get("charts", []) if c.get("type") in _NUMERIC_CHART_TYPES]
    return {"status": "success", "chart_count": len(charts), "charts": charts}


def _run_categorical_visualization(df: pd.DataFrame, context: dict) -> dict:
    """Return the subset of generated charts that cover categorical frequencies."""
    all_charts = _get_or_generate_visualizations(df, context)
    charts = [c for c in all_charts.get("charts", []) if c.get("type") == "bar_chart"]
    return {"status": "success", "chart_count": len(charts), "charts": charts}


def _run_outlier_detection(df: pd.DataFrame, context: dict) -> dict:
    """Run the existing outlier summary tool."""
    return get_outlier_summary(df)


# Tool registry: maps a planner-produced tool name to its handler.
# `AnalysisTool.TIME_SERIES_ANALYSIS` is intentionally absent — no
# implementation exists yet, so it will be reported as "skipped" rather
# than crashing the run. Adding time-series support later is just adding
# one more entry here.
TOOL_REGISTRY: Dict[str, Callable[[pd.DataFrame, dict], dict]] = {
    AnalysisTool.DATA_CLEANING: _run_data_cleaning,
    AnalysisTool.DESCRIPTIVE_STATISTICS: _run_descriptive_statistics,
    AnalysisTool.CATEGORICAL_ANALYSIS: _run_categorical_analysis,
    AnalysisTool.CORRELATION_ANALYSIS: _run_correlation_analysis,
    AnalysisTool.DISTRIBUTION_VISUALIZATION: _run_distribution_visualization,
    AnalysisTool.CATEGORICAL_VISUALIZATION: _run_categorical_visualization,
    AnalysisTool.OUTLIER_DETECTION: _run_outlier_detection,
}


class AgentOrchestrator:
    """
    Coordinates a full agentic analysis run for a single dataset.

    Usage:
        orchestrator = AgentOrchestrator()
        result = orchestrator.run_analysis(dataset_id)
    """

    def __init__(self, planner: Optional[RuleBasedPlanner] = None):
        self.planner = planner or RuleBasedPlanner()

    def run_analysis(self, dataset_id: str) -> Dict[str, Any]:
        """
        Run the full pipeline: fetch -> profile -> adapt -> plan -> execute.

        Args:
            dataset_id: The id returned by `/upload`.

        Returns:
            A JSON-serializable dict with the profile, the plan, and the
            per-step execution results, in the same order the plan defined.

        Raises:
            DatasetNotFoundError: if `dataset_id` doesn't exist in the store.
            OrchestratorError: if profiling/adapting/planning fails outright
                (this is distinct from a single tool failing, which is
                captured per-step instead and does not raise).
        """
        df = get_dataset(dataset_id)
        if df is None:
            raise DatasetNotFoundError(f"Dataset '{dataset_id}' not found.")

        raw_profile = profile_dataframe(df)

        try:
            dataset_profile = adapt_profile(raw_profile, dataset_name=dataset_id)
        except ProfileAdapterError as exc:
            raise OrchestratorError(f"Failed to adapt dataset profile: {exc}") from exc

        try:
            plan = self.planner.generate_plan(dataset_profile)
        except PlannerError as exc:
            raise OrchestratorError(f"Planner failed to generate a plan: {exc}") from exc

        context: Dict[str, Any] = {"working_df": df}
        step_results: List[Dict[str, Any]] = []

        logger.info(
            "Executing %d planned step(s) for dataset '%s'",
            len(plan.analysis_plan),
            dataset_id,
        )

        for step in plan.analysis_plan:
            handler = TOOL_REGISTRY.get(step.tool)
            working_df = context["working_df"]

            if handler is None:
                logger.info(
                    "Step %d ('%s') skipped: no tool implementation available yet",
                    step.step,
                    step.tool,
                )
                step_results.append({
                    "step": step.step,
                    "tool": step.tool,
                    "reason": step.reason,
                    "status": StepStatus.SKIPPED,
                    "detail": "No tool implementation available for this step yet.",
                })
                continue

            try:
                logger.info("Step %d: running '%s'", step.step, step.tool)
                result = handler(working_df, context)
                step_results.append({
                    "step": step.step,
                    "tool": step.tool,
                    "reason": step.reason,
                    "status": StepStatus.SUCCESS,
                    "result": result,
                })
            except Exception as exc:  # noqa: BLE001 - isolate tool failures deliberately
                logger.exception("Step %d ('%s') failed", step.step, step.tool)
                step_results.append({
                    "step": step.step,
                    "tool": step.tool,
                    "reason": step.reason,
                    "status": StepStatus.FAILED,
                    "error": str(exc),
                })

        # Persist the cleaned dataframe if data_cleaning ran, so later
        # standalone calls (e.g. GET /profile/{id}) see the cleaned data too.
        if context.get("dataset_was_cleaned"):
            update_dataset(dataset_id, context["working_df"])

        return {
            "dataset_id": dataset_id,
            "profile": raw_profile,
            "analysis_plan": [s.model_dump() for s in plan.analysis_plan],
            "results": step_results,
        }
