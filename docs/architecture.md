# Architecture

## Overview

AI-Driven Analytics Demo is a marketing performance analytics system that uses a deterministic analytics pipeline paired with an LLM interpretation layer. The LLM never calculates metrics — it only narrates findings produced by deterministic code.

```
User Question
     │
     ▼
FastAPI Backend
     │
     ├── Analytics Pipeline (deterministic)
     │     ├── Metric Calculation       metrics.py
     │     ├── Anomaly Detection        anomaly_detection.py
     │     ├── Segment Analysis         segment_analysis.py
     │     └── Contribution Analysis    contribution_analysis.py
     │
     ├── Insight Engine                 insight_generator.py
     │     └── Structured insights from pipeline results
     │
     ├── Suggestion Engine              suggestion_generator.py
     │     └── Actionable recommendations with decision traces
     │
     └── LLM Layer                      llm_layer/
           ├── BaseLLMProvider          base_provider.py
           ├── GroqProvider             groq_provider.py
           ├── OllamaProvider           ollama_provider.py
           └── Factory                  factory.py
```

## Key Principles

### 1. LLM Never Computes Metrics

All calculations happen in `analytics/`. The LLM receives only structured JSON with pre-computed values. Prompts explicitly instruct the model to never invent numbers.

### 2. Traceable Decision Logic

Every suggestion carries a `decision_trace` with:
- The decision rule applied (e.g., `budget_shift_when_roas_gap_gt_1.2`)
- The exact values compared
- The threshold that triggered the recommendation

### 3. Structured Insight Generation

Insights are generated deterministically from pipeline output. AI explanations are added on demand via the "Explain with AI" button — they are optional overlays, not the source of truth.

### 4. Provider Abstraction

`BaseLLMProvider` defines the interface. `GroqProvider` and `OllamaProvider` implement it. The factory pattern allows runtime switching without restart.

## Data Flow

```
synthetic_generator.py
        │
        │ 90 days × 3 campaigns × 5 audiences × 3 devices × 3 creatives × 5 regions
        │
        ▼
aggregate_daily()   ← collapses to daily campaign totals for anomaly detection
        │
        ▼
run_pipeline()
  ├── detect_anomalies()    7-day rolling z-score + % threshold
  ├── analyze_segments()    per-dimension aggregation and ranking
  ├── compute_contributions() which segment drove the anomaly
  └── build_kpi_summary()   campaign-level derived metrics
        │
        ▼
generate_insights()   typed Insight objects
generate_suggestions() typed Suggestion objects with decision traces
        │
        ▼
FastAPI routes → React UI
```

## Anomaly Detection

An anomaly is triggered when:
- `|% change vs 7-day rolling mean| > 15%`, OR
- `|z-score| > 2.0`

Severity:
- High: `|%| > 35%` or `|z| > 3.0`
- Medium: `|%| > 20%` or `|z| > 2.5`
- Low: below medium thresholds

## Suggestion Rules

| Suggestion Type | Rule |
|---|---|
| Budget shift | ROAS gap between campaigns > 1.2× AND a performance drop anomaly exists |
| Creative refresh | Segment CTR > 15% below campaign average |
| Audience pause | Segment CPA > 50% above campaign average |

## LLM Provider Configuration

Runtime switching via `POST /api/llm/provider`:

```json
{ "provider": "ollama", "model": "llama3" }
{ "provider": "groq", "model": "llama3-70b-8192" }
```

The factory resets the singleton instance on each provider change.
