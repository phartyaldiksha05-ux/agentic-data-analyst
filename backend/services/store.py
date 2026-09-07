"""
Very simple in-memory store for uploaded datasets.
Good enough for an MVP / demo. Not for production (data is lost on restart).
"""

import uuid
import pandas as pd

# dataset_id -> pandas DataFrame
_datasets: dict[str, pd.DataFrame] = {}


def save_dataset(df: pd.DataFrame) -> str:
    """Store a dataframe and return a new dataset_id."""
    dataset_id = str(uuid.uuid4())
    _datasets[dataset_id] = df
    return dataset_id


def get_dataset(dataset_id: str) -> pd.DataFrame | None:
    """Retrieve a dataframe by id, or None if it doesn't exist."""
    return _datasets.get(dataset_id)


def update_dataset(dataset_id: str, df: pd.DataFrame) -> None:
    """Overwrite an existing dataset (e.g. after cleaning)."""
    _datasets[dataset_id] = df


def dataset_exists(dataset_id: str) -> bool:
    return dataset_id in _datasets
