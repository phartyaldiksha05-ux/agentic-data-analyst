# 🤖 Agentic Data Analyst

An autonomous AI-powered data analyst that profiles datasets, plans and runs statistical analysis, generates visualizations, and produces plain-language insights — all from a single CSV upload.

## 📌 Overview

Upload a CSV, and the system automatically:

```
📤 Upload CSV
⬇️
🔍 Understand & Profile Data
⬇️
🤖 AI Creates Analysis Plan
⬇️
🧹 Clean Data
⬇️
📊 Statistical Analysis
⬇️
📈 Automatic Visualizations
⬇️
💡 Generate Insights
⬇️
📋 Final Dashboard/Report
```

The goal is a fully working **MVP**: a clean, reliable end-to-end pipeline rather than a feature-heavy tool.

## ✨ Features

- **Dataset Profiling** — rows, columns, data types, missing values, duplicates, unique values, numerical/categorical split
- **AI Planner Agent** — an LLM decides which analyses are relevant for the uploaded dataset
- **Data Cleaning** — median/mode imputation, duplicate removal, basic type conversion
- **Statistical Analysis** — descriptive stats, distributions, outlier detection
- **Categorical Analysis** — frequency counts, most common category, percentage distribution
- **Correlation Analysis** — correlation matrix + heatmap, strong correlation detection
- **Automatic Visualizations** — histograms, box plots, bar charts, line charts, scatter plots, correlation heatmaps
- **AI-Generated Insights** — statistical results translated into plain-language takeaways
- **Dashboard/Report** — a final view combining profile, charts, and insights

## 🏗️ Tech Stack

| Layer            | Tech                          |
|-------------------|-------------------------------|
| Backend            | FastAPI, Pandas               |
| AI Agent / LLM     | LLM API integration           |
| Data Analysis      | Pandas, NumPy                 |
| Visualization      | Matplotlib / Plotly (charting layer) |
| Frontend           | Web UI (upload, dashboard, insights views) |

## 📁 Project Structure

agentic-data-analyst/
│
├── frontend/                # Upload page, dataset overview, plan display, charts dashboard, insights UI
│
├── backend/
│   ├── main.py               # FastAPI app entrypoint
│   │
│   ├── routes/
│   │   ├── upload.py          # File upload endpoint
│   │   └── analyze.py         # Analysis trigger endpoint
│   │
│   ├── services/
│   │   ├── profiler.py        # Dataset profiling logic
│   │   └── cleaning.py        # Data cleaning functions
│   │
│   ├── agent/
│   │   ├── planner.py         # AI Planner Agent — decides the analysis plan
│   │   └── insights.py        # Converts results into plain-language insights
│   │
│   ├── tools/
│   │   ├── statistics.py      # Descriptive statistics
│   │   ├── visualization.py   # Chart generation
│   │   ├── correlation.py     # Correlation matrix + heatmap
│   │   └── outliers.py        # Outlier detection
│   │
│   └── uploads/               # Uploaded dataset storage
│
├── requirements.txt
└── README.md

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js (if the frontend requires it)
- An LLM API key (for the AI Planner Agent / insights generation)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
# install dependencies and start the dev server as per the frontend framework used
```

### Environment Variables

Create a `.env` file in `backend/` with your LLM API credentials:

```
LLM_API_KEY=your_api_key_here
```

## 🔌 API Endpoints

| Method | Endpoint            | Description                          |
|--------|----------------------|---------------------------------------|
| POST   | `/upload`             | Upload a CSV (Excel support optional) |
| GET    | `/profile`             | Get dataset profile                   |
| POST   | `/clean`               | Run data cleaning                     |
| POST   | `/analyze`             | Run full analysis pipeline            |

## 👥 Team & Responsibilities

| Member         | Focus Area                                   |
|-----------------|-----------------------------------------------|
| **Diksha**       | AI Planner Agent, LLM integration, frontend, final integration |
| **Anjali**       | Backend setup, file upload, dataset profiling, data cleaning, APIs |
| **Siddharth**    | Statistical analysis, categorical/numerical analysis, correlation, visualizations |

THANKYOU!
