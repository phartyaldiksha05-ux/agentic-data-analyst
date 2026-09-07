from fastapi import APIRouter, HTTPException

from services.store import get_dataset, update_dataset
from services.profiler import profile_dataframe
from services.cleaning import clean_dataset

router = APIRouter()


@router.get("/profile/{dataset_id}")
def get_profile(dataset_id: str):
    df = get_dataset(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return {"dataset_id": dataset_id, "profile": profile_dataframe(df)}


@router.post("/clean/{dataset_id}")
def clean(dataset_id: str):
    df = get_dataset(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    cleaned_df, summary = clean_dataset(df)
    update_dataset(dataset_id, cleaned_df)

    return {
        "dataset_id": dataset_id,
        "cleaning_summary": summary,
        "profile_after_cleaning": profile_dataframe(cleaned_df),
    }


@router.post("/analyze/{dataset_id}")
def run_analysis(dataset_id: str):
    """
    Placeholder for Siddharth's statistics/visualization/correlation tools.
    Once his functions in tools/ are ready, import and call them here, e.g.:

        from tools.statistics import run_statistics
        from tools.correlation import run_correlation
        from tools.visualization import generate_charts

        results = {
            "statistics": run_statistics(df),
            "correlation": run_correlation(df),
            "charts": generate_charts(df),
        }
    """
    df = get_dataset(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    return {
        "dataset_id": dataset_id,
        "message": "Analysis endpoint is wired up. Waiting on tools/ from Siddharth.",
    }
