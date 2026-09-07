from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import upload, analyze

app = FastAPI(title="Agentic Data Analyst API")

# Allow the frontend (running on a different port) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["Upload"])
app.include_router(analyze.router, tags=["Analyze"])


@app.get("/")
def root():
    return {"status": "ok", "message": "Agentic Data Analyst API is running"}
