"""
FastAPI route definitions.
"""
from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from analytics.pipeline import run_pipeline
from config.llm_config import PROVIDER_MODELS
from data.synthetic_generator import (
    aggregate_daily,
    generate_campaign_data,
    get_events_metadata,
)
from insight_engine.insight_generator import generate_insights
from llm_layer.factory import get_llm, get_provider_info, set_provider
from llm_layer.ollama_provider import OllamaProvider
from suggestion_engine.suggestion_generator import generate_suggestions

router = APIRouter()

# ── Cached dataset (generated once on first request) ─────────────────────────
_dataset: dict[str, list[dict[str, Any]]] | None = None
_pipeline_cache: dict[str, Any] | None = None


def _get_dataset() -> dict[str, list[dict[str, Any]]]:
    global _dataset
    if _dataset is None:
        _dataset = generate_campaign_data(seed=42, days=90)
    return _dataset


def _get_pipeline(metric: str = "clicks") -> dict[str, Any]:
    global _pipeline_cache
    if _pipeline_cache is None:
        data = _get_dataset()
        # Aggregate to daily totals per campaign for anomaly detection
        daily_data = {c: aggregate_daily(recs) for c, recs in data.items()}
        _pipeline_cache = run_pipeline(daily_data, focus_metric=metric, raw_data=data)
        _pipeline_cache["_raw"] = data  # Keep raw for segment queries
    return _pipeline_cache


# ── Request / Response models ─────────────────────────────────────────────────

class ProviderRequest(BaseModel):
    provider: str
    model: str


class QuestionRequest(BaseModel):
    question: str
    context_hint: str | None = None


class ExplainInsightRequest(BaseModel):
    insight_id: str


class ExplainSuggestionRequest(BaseModel):
    suggestion_id: str


# ── LLM Provider routes ───────────────────────────────────────────────────────

@router.get("/llm/provider")
def get_current_provider():
    return get_provider_info()


@router.post("/llm/provider")
def update_provider(req: ProviderRequest):
    if req.provider not in ("ollama", "groq"):
        raise HTTPException(400, f"Unknown provider: {req.provider!r}")
    set_provider(req.provider, req.model)
    return {"status": "ok", **get_provider_info()}


@router.get("/llm/models")
def list_models():
    info = get_provider_info()
    models = PROVIDER_MODELS.copy()

    # If Ollama is active, try to fetch live model list
    if info["provider"] == "ollama":
        try:
            provider = get_llm()
            if isinstance(provider, OllamaProvider):
                live = provider.list_models()
                if live:
                    models["ollama"] = live
        except Exception:
            pass

    return {"models": models, "current": info}


@router.get("/llm/health")
def llm_health():
    info = get_provider_info()
    if info["provider"] == "ollama":
        try:
            provider = get_llm()
            if isinstance(provider, OllamaProvider):
                ok = provider.health_check()
                return {"provider": "ollama", "healthy": ok}
        except Exception:
            return {"provider": "ollama", "healthy": False}
    return {"provider": info["provider"], "healthy": True}


# ── Data / Analytics routes ───────────────────────────────────────────────────

@router.get("/data/campaigns")
def get_campaigns():
    dataset = _get_dataset()
    return {"campaigns": list(dataset.keys())}


@router.get("/data/timeseries/{campaign}")
def get_timeseries(campaign: str):
    dataset = _get_dataset()
    if campaign not in dataset:
        raise HTTPException(404, f"Campaign {campaign!r} not found")
    daily = aggregate_daily(dataset[campaign])
    return {"campaign": campaign, "data": daily}


@router.get("/data/timeseries")
def get_all_timeseries():
    dataset = _get_dataset()
    result = {}
    for campaign, records in dataset.items():
        result[campaign] = aggregate_daily(records)
    return {"data": result}


@router.get("/data/events")
def get_injected_events():
    return {"events": get_events_metadata()}


@router.get("/analytics/pipeline")
def get_pipeline_result(metric: str = "clicks"):
    result = _get_pipeline(metric)
    # Exclude raw data from response
    clean = {k: v for k, v in result.items() if k != "_raw"}
    return clean


@router.get("/analytics/anomalies")
def get_anomalies():
    result = _get_pipeline()
    return {"anomalies": result["anomalies"]}


@router.get("/analytics/segments/{campaign}")
def get_segments(campaign: str, dimension: str = "audience"):
    result = _get_pipeline()
    segments = result.get("segments", {}).get(campaign, {})
    if dimension not in segments:
        raise HTTPException(404, f"No segment data for {campaign!r} / {dimension!r}")
    return {"campaign": campaign, "dimension": dimension, "segments": segments[dimension]}


@router.get("/analytics/kpi")
def get_kpi_summary():
    result = _get_pipeline()
    return {"kpi_summary": result["kpi_summary"]}


# ── Insight routes ────────────────────────────────────────────────────────────

@router.get("/insights")
def get_insights():
    pipeline = _get_pipeline()
    insights = generate_insights(pipeline)
    return {"insights": [i.to_dict() for i in insights]}


@router.post("/insights/explain")
def explain_insight(req: ExplainInsightRequest):
    pipeline = _get_pipeline()
    insights = generate_insights(pipeline)
    insight = next((i for i in insights if i.id == req.insight_id), None)
    if insight is None:
        raise HTTPException(404, f"Insight {req.insight_id!r} not found")

    try:
        llm = get_llm()
        explanation = llm.explain_insight(json.dumps(insight.to_dict(), indent=2))
        insight.ai_explanation = explanation
    except Exception as exc:
        raise HTTPException(503, f"LLM unavailable: {exc}") from exc

    return insight.to_dict()


# ── Suggestion routes ─────────────────────────────────────────────────────────

@router.get("/suggestions")
def get_suggestions():
    pipeline = _get_pipeline()
    insights = generate_insights(pipeline)
    suggestions = generate_suggestions(insights, pipeline)
    return {"suggestions": [s.to_dict() for s in suggestions]}


@router.post("/suggestions/explain")
def explain_suggestion(req: ExplainSuggestionRequest):
    pipeline = _get_pipeline()
    insights = generate_insights(pipeline)
    suggestions = generate_suggestions(insights, pipeline)
    suggestion = next((s for s in suggestions if s.id == req.suggestion_id), None)
    if suggestion is None:
        raise HTTPException(404, f"Suggestion {req.suggestion_id!r} not found")

    try:
        llm = get_llm()
        explanation = llm.explain_suggestion(
            json.dumps(suggestion.to_dict(), indent=2),
            json.dumps({"kpi_summary": pipeline.get("kpi_summary", {})}, indent=2),
        )
        suggestion.ai_explanation = explanation
    except Exception as exc:
        raise HTTPException(503, f"LLM unavailable: {exc}") from exc

    return suggestion.to_dict()


# ── Question / Investigation routes ──────────────────────────────────────────

@router.post("/investigate")
def investigate(req: QuestionRequest):
    pipeline = _get_pipeline()
    insights = generate_insights(pipeline)
    suggestions = generate_suggestions(insights, pipeline)

    # Find all anomalies relevant to the question (matching campaign names)
    question_lower = req.question.lower()
    all_anomalies = pipeline["anomalies"]
    relevant_anomalies = [
        a for a in all_anomalies
        if a.get("campaign", "").lower() in question_lower
    ]
    # Fall back to top anomalies if none match
    if not relevant_anomalies:
        relevant_anomalies = all_anomalies[:5]
    else:
        relevant_anomalies = relevant_anomalies[:10]

    # Build per-campaign daily timeseries for campaigns mentioned in the question
    dataset = _get_dataset()
    timeseries_context: dict[str, list[dict[str, Any]]] = {}
    for campaign_name, records in dataset.items():
        if campaign_name.lower() in question_lower:
            daily = aggregate_daily(records)
            timeseries_context[campaign_name] = daily

    context = {
        "question": req.question,
        "relevant_anomalies": relevant_anomalies[:10],
        "all_anomaly_count": len(all_anomalies),
        "kpi_summary": pipeline["kpi_summary"],
        "top_insights": [i.to_dict() for i in insights[:5]],
        "top_suggestions": [s.to_dict() for s in suggestions[:3]],
        "timeseries": timeseries_context,
        "pipeline_steps": pipeline["pipeline_steps"],
    }

    try:
        llm = get_llm()
        answer = llm.answer_question(req.question, json.dumps(context, indent=2))
    except Exception as exc:
        raise HTTPException(503, f"LLM unavailable: {exc}") from exc

    return {
        "question": req.question,
        "answer": answer,
        "evidence": {
            "anomalies": relevant_anomalies[:5],
            "insights": [i.to_dict() for i in insights[:5]],
            "suggestions": [s.to_dict() for s in suggestions[:3]],
        },
        "pipeline_steps": pipeline["pipeline_steps"],
    }
