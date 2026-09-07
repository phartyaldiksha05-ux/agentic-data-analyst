import io
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException

from services.store import save_dataset
from services.profiler import profile_dataframe

router = APIRouter()

ALLOWED_EXTENSIONS = (".csv",)  # add ".xlsx" later if time allows


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    filename = file.filename or ""
    if not filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Only CSV files are supported right now.")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read CSV file: {e}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded CSV is empty.")

    dataset_id = save_dataset(df)
    profile = profile_dataframe(df)

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "profile": profile,
    }
