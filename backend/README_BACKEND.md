# Backend — Agentic Data Analyst (Anjali's module)

## Run it

```bash
pip install -r requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

Server will be live at `http://127.0.0.1:8000`. Interactive docs at `http://127.0.0.1:8000/docs`.

## Endpoints

| Method | Endpoint                | Description                                      |
|--------|--------------------------|--------------------------------------------------|
| POST   | `/upload`                | Upload a CSV. Returns `dataset_id` + profile.     |
| GET    | `/profile/{dataset_id}`  | Get the current profile of a dataset.             |
| POST   | `/clean/{dataset_id}`    | Clean the dataset (median/mode fill, dedupe).     |
| POST   | `/analyze/{dataset_id}`  | Placeholder — plug in Siddharth's tools here.     |

## Flow

1. Frontend uploads a CSV to `/upload` → gets back `dataset_id` + profile.
2. Frontend/AI agent can call `/profile/{id}` any time to re-check the dataset.
3. Frontend calls `/clean/{id}` → dataset is cleaned in place, returns before/after summary.
4. Frontend calls `/analyze/{id}` → currently a stub. Once `tools/statistics.py`,
   `tools/correlation.py`, `tools/visualization.py` (Siddharth's files) exist,
   import them in `routes/analyze.py` and call them there — that's the only file
   that needs to change.

## Notes for integration

- Dataset storage is in-memory (`services/store.py`) — fine for MVP/demo, resets on server restart.
- All responses are JSON, so Diksha's AI agent and frontend can consume them directly.
- CORS is wide open (`allow_origins=["*"]`) so the frontend can call this from any port during dev.
- Only `.csv` is supported right now; add `.xlsx` support in `routes/upload.py` if time allows
  (just add pandas' `read_excel` as a branch based on file extension).
