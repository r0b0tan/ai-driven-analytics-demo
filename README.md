# AI-Driven Analytics Demo

An AI-assisted marketing performance analytics system that investigates anomalies, generates explainable insights, and produces traceable recommendations.

**The LLM never calculates metrics.** All numbers come from the deterministic analytics pipeline. The LLM only narrates findings.

## Architecture

```
User Question
     │
     ▼
┌─────────────────────────────────────────────┐
│  FastAPI Backend                            │
│                                             │
│  Analytics Pipeline (deterministic)         │
│    Metric Calculation → Anomaly Detection   │
│    → Segment Analysis → Contribution        │
│                                             │
│  Insight Engine → Suggestion Engine         │
│       (structured)    (with decision trace) │
│                                             │
│  LLM Layer (Ollama / Groq)                 │
│    narrates findings only                   │
└─────────────────┬───────────────────────────┘
                  │
     ┌────────────▼────────────┐
     │  React + Vite + TS UI   │
     │  Recharts · Axios       │
     └─────────────────────────┘
```

## Key Features

- **4-step investigation pipeline** — anomaly detection → segment analysis → contribution analysis → insight generation
- **Explainable suggestions** — every recommendation includes a decision trace with the rule applied, exact values, and threshold used
- **Dual LLM modes** — switch between Ollama (local) and Groq (cloud) at runtime via the UI
- **90 days of synthetic data** with 5 injected anomaly events: creative fatigue, audience saturation, budget cuts, competitor bid spikes, seasonal boost
- **On-demand AI explanations** — click "Explain with AI" on any insight or suggestion to get a narrative interpretation
- **Natural-language investigation** — ask questions like *"Why did campaign performance drop?"* and get answers backed by pipeline evidence

## Quick Start

```bash
./start.sh
```

This creates the Python venv, installs all dependencies, and starts both backend (`:8000`) and frontend (`:5173`).

### Manual Setup

**Backend:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in GROQ_API_KEY if using Groq
uvicorn main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:5173         |
| Backend  | http://localhost:8000         |
| API Docs | http://localhost:8000/docs    |

## LLM Providers

| Provider | Type  | Setup |
|----------|-------|-------|
| Ollama   | Local | `ollama pull llama3.2` — select **Ollama (Local)** in the UI |
| Groq     | Cloud | Set `GROQ_API_KEY` in `backend/.env` — select **Groq (Cloud)** in the UI |

The provider can be switched at runtime through the sidebar model selector — no restart needed.

## Analytics Pipeline

The pipeline runs entirely deterministic code. No LLM is involved in any calculation.

| Step | Module | What it does |
|------|--------|-------------|
| 1 | `anomaly_detection.py` | Compares each day against a 7-day rolling average, flags deviations beyond z-score thresholds |
| 2 | `segment_analysis.py` | Breaks down performance by audience, device, creative, region; ranks segments |
| 3 | `contribution_analysis.py` | Attributes the anomaly to specific dimension segments |
| 4 | `insight_generator.py` | Produces typed `Insight` objects (drop / spike / efficiency gap) |
| 5 | `suggestion_generator.py` | Generates `Suggestion` objects with full decision traces |

### Suggestion Types

| Type | Rule | Example |
|------|------|---------|
| `budget_shift` | ROAS gap > 1.2× between campaigns | *Shift budget from Campaign C to Campaign B* |
| `creative_refresh` | Creative CTR > 15% below campaign average | *Refresh creative_v1 in Campaign A* |
| `audience_pause` | Audience CPA > 50% above campaign average | *Pause 55+ desktop in Campaign A* |

Each suggestion includes a `decision_trace` object with the exact rule, input values, and thresholds.

## Synthetic Data

90 days of campaign data (3 campaigns × 5 audiences × 3 devices × 3 creatives × 5 regions) with injected events:

| Event | Campaign | Days | Effect |
|-------|----------|------|--------|
| Creative fatigue | A | 55–67 | CTR −60% on creative_v1 |
| Audience saturation | A | 62–70 | Clicks −25%, conversions −30% for 18–24 mobile |
| Budget cut | C | 45–60 | Impressions −50%, spend −45% |
| Competitor bid spike | B | 70–77 | Spend +35%, conversions −20% |
| Seasonal boost | B | 30–40 | Clicks +30%, conversions +35%, revenue +40% |

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

frontend/src/
  api/                # Axios API client
  charts/             # Recharts visualisations (time series, segments, CPA)
  components/         # UI components (InsightCard, SuggestionCard, …)
  pages/              # Dashboard page
  types/              # TypeScript interfaces

docs/
  architecture.md     # System design details
  demo_story.md       # Walkthrough scenario
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 · FastAPI · Pydantic |
| Frontend | React 19 · Vite · TypeScript · Recharts |
| LLM | Ollama (local) · Groq (cloud) |
| Data | Deterministic synthetic generator with seeded RNG |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/data/campaigns` | List campaigns |
| `GET` | `/api/data/timeseries` | All daily time series |
| `GET` | `/api/data/timeseries/{campaign}` | Campaign time series |
| `GET` | `/api/analytics/anomalies` | Detected anomalies |
| `GET` | `/api/analytics/kpi` | KPI summary per campaign |
| `GET` | `/api/analytics/segments/{campaign}` | Segment breakdown |
| `GET` | `/api/insights` | Structured insights |
| `POST` | `/api/insights/explain` | AI explanation for an insight |
| `GET` | `/api/suggestions` | Actionable suggestions |
| `POST` | `/api/suggestions/explain` | AI explanation for a suggestion |
| `POST` | `/api/investigate` | Full AI investigation for a question |
| `GET/POST` | `/api/llm/provider` | Get/set LLM provider |
| `GET` | `/api/llm/models` | Available models |
| `GET` | `/api/llm/health` | LLM connectivity check |

## License

MIT
