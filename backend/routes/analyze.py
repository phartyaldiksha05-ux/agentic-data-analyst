from fastapi import APIRouter, HTTPException

from services.store import get_dataset, update_dataset
from services.profiler import profile_dataframe
from services.cleaning import clean_dataset
from agent.orchestrator import AgentOrchestrator, DatasetNotFoundError, OrchestratorError

router = APIRouter()
orchestrator = AgentOrchestrator()


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
    Run the full agentic analysis pipeline for a dataset:
    profile -> AI agent plan -> execute relevant tools -> aggregated results.

    All coordination logic lives in agent/orchestrator.py — this route just
    calls it and translates orchestrator-level failures into HTTP errors.
    Individual tool failures within the plan do not raise here; they are
    reported per-step in the response body instead.
    """
    try:
        return orchestrator.run_analysis(dataset_id)
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except OrchestratorError as exc:
        raise HTTPException(status_code=500, detail=str(exc))