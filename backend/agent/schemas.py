"""
Pydantic schemas for the Agentic Data Analyst — AI Agent module.

Defines the structured input (dataset profile, produced by the profiling
module owned by another team member) and structured output (analysis plan)
contracts used by the planner. Keeping these in one place means any future
planner implementation (rule-based, LLM-based, hybrid) can share the exact
same input/output contract.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class ColumnType(str, Enum):
    """Supported column data types, as reported by the profiling module."""

    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    TEXT = "text"
    OTHER = "other"


class ColumnProfile(BaseModel):
    """Profile information for a single dataset column."""

    name: str = Field(..., description="Column name")
    type: ColumnType = Field(..., description="Detected column data type")
    missing_count: int = Field(0, ge=0, description="Number of missing/null values")
    unique_count: int = Field(0, ge=0, description="Number of unique values")

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        """Ensure column names are non-empty and free of surrounding whitespace issues."""
        if not value or not value.strip():
            raise ValueError("Column name must not be empty or blank")
        return value


class DatasetProfile(BaseModel):
    """
    Overall dataset profile.

    This is the AI Agent's INPUT contract. It is expected to be produced by
    the profiling module (owned by another team member) and handed to the
    planner as-is.
    """

    dataset_name: str = Field(..., description="Name of the uploaded dataset file")
    rows: int = Field(..., ge=0, description="Total number of rows in the dataset")
    columns: List[ColumnProfile] = Field(
        default_factory=list, description="Per-column profile information"
    )
    duplicate_rows: int = Field(0, ge=0, description="Number of duplicate rows detected")

    @field_validator("dataset_name")
    @classmethod
    def dataset_name_must_not_be_blank(cls, value: str) -> str:
        """Ensure the dataset name is present."""
        if not value or not value.strip():
            raise ValueError("dataset_name must not be empty or blank")
        return value

    @field_validator("columns")
    @classmethod
    def must_have_columns(cls, value: List[ColumnProfile]) -> List[ColumnProfile]:
        """A dataset profile with zero columns can't be planned against."""
        if not value:
            raise ValueError("DatasetProfile must contain at least one column")
        return value


class AnalysisStep(BaseModel):
    """A single recommended analysis step within the plan."""

    step: int = Field(..., ge=1, description="Sequential order of the step (1-indexed)")
    tool: str = Field(..., description="Name of the analysis tool/module to invoke")
    reason: str = Field(..., description="Human-readable explanation for why this step was chosen")


class AnalysisPlan(BaseModel):
    """
    Full analysis plan.

    This is the AI Agent's OUTPUT contract, and is JSON-serializable via
    `AnalysisPlan(...).model_dump()` / `.model_dump_json()`.
    """

    analysis_plan: List[AnalysisStep] = Field(
        default_factory=list, description="Ordered list of recommended analysis steps"
    )
