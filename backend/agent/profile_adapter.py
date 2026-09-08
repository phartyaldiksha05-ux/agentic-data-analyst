"""
Profile Adapter
---------------
Converts the output of `services.profiler.profile_dataframe(df)` (a plain
dict, owned by another team member) into the AI Agent's `DatasetProfile`
Pydantic schema, without modifying `services/profiler.py` at all.

Why this file exists
---------------------
`profile_dataframe()` returns `numerical_columns` / `categorical_columns`
lists that are split purely on `df.select_dtypes(include/exclude=np.number)`.
That means a real datetime64 column (e.g. after `services/cleaning.py`'s
`convert_basic_types` upgrades it) still lands in `categorical_columns`,
because "not numeric" and "categorical" are being treated as the same thing
upstream. If we adapted the profile using those two lists directly, the
Agent's `time_series_analysis` rule could never fire.

Instead, this adapter classifies each column from its raw dtype string
(`profile["dtypes"]`), which is dtype-accurate and doesn't require touching
the profiler.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from .schemas import ColumnProfile, ColumnType, DatasetProfile

logger = logging.getLogger(__name__)


class ProfileAdapterError(Exception):
    """Raised when a profiler dict cannot be converted into a DatasetProfile."""


def _classify_column_type(dtype_str: str) -> ColumnType:
    """
    Map a pandas dtype string to the Agent's `ColumnType` enum.

    Args:
        dtype_str: e.g. "int64", "float64", "object", "datetime64[ns]", "bool".

    Returns:
        The best-matching `ColumnType`. Falls back to `ColumnType.OTHER` for
        anything unrecognized, rather than raising, so a single odd column
        doesn't break profiling for the whole dataset.
    """
    normalized = dtype_str.lower()

    if normalized.startswith("datetime"):
        return ColumnType.DATETIME

    if normalized == "bool":
        return ColumnType.BOOLEAN

    if normalized.startswith(("int", "float", "uint")):
        return ColumnType.NUMERIC

    if normalized in ("object", "category", "string", "str"):
        # "object" is classic pandas (<2.x); "string"/"str" cover the
        # nullable StringDtype used by pandas 2.x's opt-in and pandas 3.x's
        # default string backend. Covering all three keeps this adapter
        # correct regardless of which pandas version/config the deployed
        # environment ends up using.
        return ColumnType.CATEGORICAL

    logger.warning("Unrecognized dtype '%s' — classifying column as OTHER", dtype_str)
    return ColumnType.OTHER


def adapt_profile(profile: Dict[str, Any], dataset_name: str) -> DatasetProfile:
    """
    Convert a `profile_dataframe()` dict into a validated `DatasetProfile`.

    Args:
        profile: The dict returned by `services.profiler.profile_dataframe`.
        dataset_name: Identifier for the dataset. `store.py` does not persist
            the original filename, so callers (the orchestrator) pass the
            `dataset_id` here instead.

    Returns:
        A validated `DatasetProfile` ready for `RuleBasedPlanner.generate_plan`.

    Raises:
        ProfileAdapterError: if the profile dict is missing expected keys, or
            the resulting data fails `DatasetProfile`'s own validation.
    """
    try:
        column_names = profile["column_names"]
        dtypes = profile["dtypes"]
        num_rows = profile["num_rows"]
    except KeyError as exc:
        raise ProfileAdapterError(f"Profile dict is missing expected key: {exc}") from exc

    missing_values = profile.get("missing_values", {})
    unique_values = profile.get("unique_values", {})
    duplicate_rows = profile.get("duplicate_rows", 0)

    columns = []
    for name in column_names:
        dtype_str = dtypes.get(name, "object")
        columns.append(
            ColumnProfile(
                name=name,
                type=_classify_column_type(dtype_str),
                missing_count=int(missing_values.get(name, 0)),
                unique_count=int(unique_values.get(name, 0)),
            )
        )

    try:
        return DatasetProfile(
            dataset_name=dataset_name,
            rows=int(num_rows),
            columns=columns,
            duplicate_rows=int(duplicate_rows),
        )
    except Exception as exc:  # pydantic.ValidationError, primarily
        raise ProfileAdapterError(f"Could not build DatasetProfile: {exc}") from exc
