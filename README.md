# AI-Driven Analytics Demo

An AI-assisted marketing performance analytics system that investigates anomalies, generates explainable insights, and produces traceable recommendations.

**The LLM never calculates metrics.** All numbers come from the deterministic analytics pipeline. The LLM only narrates findings.

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in GROQ_API_KEY if using Groq
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: http://localhost:5173

---

## LLM Providers

### Ollama (local, default)

```bash
# Install Ollama and pull a model
ollama pull llama3
```

In the UI, select **Ollama (Local)** → `llama3`.

### Groq (cloud)

Set `GROQ_API_KEY` in `backend/.env`. In the UI, select **Groq (Cloud)**.

---

## Project Structure

```
backend/
  analytics/          # Deterministic metric calculations & pipeline
  insight_engine/     # Structured insight generation
  suggestion_engine/  # Actionable recommendation engine
  llm_layer/          # Provider abstraction (Groq + Ollama)
  api/                # FastAPI routes
  config/             # LLM configuration
  data/               # Synthetic data generator

frontend/
  src/
    api/              # Axios API client
    charts/           # Recharts components
    components/       # UI components
    pages/            # Dashboard page
    types/            # TypeScript interfaces

docs/
  architecture.md     # System design
  demo_story.md       # Walkthrough scenario
```

## Key Features

- **4-step investigation pipeline**: anomaly detection → segment analysis → contribution analysis → insight generation
- **Explainable suggestions**: every recommendation includes a decision trace with the rule applied, exact values, and threshold used
- **Dual LLM modes**: switch between Ollama (local) and Groq (cloud) at runtime via the UI
- **90 days of synthetic data** with 5 injected anomaly events: creative fatigue, audience saturation, budget cuts, competitor bid spikes, seasonal boost
- **On-demand AI explanations**: click "Explain with AI" on any insight or suggestion to get narrative interpretation
