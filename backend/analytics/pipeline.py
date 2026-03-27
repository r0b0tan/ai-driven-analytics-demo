"""
Orchestrates the full analytics pipeline:
  data → metrics → anomaly detection → segment analysis → contribution analysis

Returns structured results ready for insight_engine and suggestion_engine.
"""
from __future__ import annotations

from typing import Any

from .anomaly_detection import detect_anomalies, rank_anomalies
from .contribution_analysis import build_contribution_summary, compute_contributions
from .metrics import compute_cpa, compute_ctr, compute_cvr, compute_roas
from .segment_analysis import analyze_segments


TRACKED_METRICS = ["clicks", "impressions", "conversions", "spend", "revenue"]
DIMENSIONS = ["audience", "device", "creative", "region"]


def run_pipeline(
    campaign_data: dict[str, list[dict[str, Any]]],
    focus_metric: str = "clicks",
    raw_data: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """
    Full pipeline execution.

    Parameters
    ----------
    campaign_data : {campaign_name: [daily_records]}
    focus_metric  : the primary metric to investigate

    Returns structured pipeline result consumed by insight/suggestion engines.
    """
    step_log: list[dict[str, Any]] = []

    # ── Step 1: Detect anomalies ──────────────────────────────────────────────
    step_log.append({"step": 1, "name": "Detect anomalies", "status": "running"})
    all_anomalies = []
    for campaign, records in campaign_data.items():
        # Sort ascending
        sorted_records = sorted(records, key=lambda r: r["date"])
        for metric in TRACKED_METRICS:
            anomalies = detect_anomalies(
                sorted_records, campaign, metric, window=7
            )
            all_anomalies.extend(anomalies)

    ranked = rank_anomalies(all_anomalies)
    step_log[-1]["status"] = "complete"
    step_log[-1]["found"] = len(ranked)

    # ── Step 2: Segment analysis ──────────────────────────────────────────────
    step_log.append({"step": 2, "name": "Segment analysis", "status": "running"})
    segment_results: dict[str, dict[str, Any]] = {}
    segment_source = raw_data if raw_data is not None else campaign_data
    for campaign, records in segment_source.items():
        segment_results[campaign] = {}
        for dim in DIMENSIONS:
            if any(dim in r for r in records):
                segs = analyze_segments(records, dimension=dim, primary_metric=focus_metric)
                segment_results[campaign][dim] = [s.to_dict() for s in segs]

    step_log[-1]["status"] = "complete"

    # ── Step 3: Contribution analysis for top anomaly ─────────────────────────
    step_log.append({"step": 3, "name": "Contribution analysis", "status": "running"})
    contribution_results: dict[str, Any] = {}

    if ranked:
        top_anomaly = ranked[0]
        campaign_records = sorted(
            campaign_data.get(top_anomaly.campaign, []),
            key=lambda r: r["date"],
        )

        if len(campaign_records) >= 8:
            # Baseline: 7-day window before the anomaly
            try:
                anomaly_idx = next(
                    i for i, r in enumerate(campaign_records)
                    if r["date"] == top_anomaly.date
                )
                baseline_window = campaign_records[max(0, anomaly_idx - 7) : anomaly_idx]
                observed_record = campaign_records[anomaly_idx]

                for dim in DIMENSIONS:
                    if any(dim in r for r in baseline_window):
                        baseline_seg = _group_by(baseline_window, dim, top_anomaly.metric)
                        observed_seg = _group_by([observed_record], dim, top_anomaly.metric)

                        if baseline_seg and observed_seg:
                            contribs = compute_contributions(baseline_seg, observed_seg, dim)
                            contribution_results[dim] = build_contribution_summary(
                                contribs, top_anomaly.metric, top_anomaly.direction
                            )
            except (StopIteration, IndexError):
                pass

    step_log[-1]["status"] = "complete"

    # ── Step 4: Campaign-level KPI summary ────────────────────────────────────
    step_log.append({"step": 4, "name": "Insight generation", "status": "running"})
    kpi_summary = _build_kpi_summary(campaign_data)
    step_log[-1]["status"] = "complete"

    return {
        "anomalies": [a.to_dict() for a in ranked],
        "segments": segment_results,
        "contributions": contribution_results,
        "kpi_summary": kpi_summary,
        "pipeline_steps": step_log,
        "focus_metric": focus_metric,
    }


def _group_by(
    records: list[dict[str, Any]], dimension: str, metric: str
) -> dict[str, float]:
    groups: dict[str, list[float]] = {}
    for r in records:
        key = str(r.get(dimension, "unknown"))
        val = r.get(metric)
        if val is not None:
            groups.setdefault(key, []).append(float(val))
    return {k: sum(vs) / len(vs) for k, vs in groups.items()}


def _build_kpi_summary(
    campaign_data: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for campaign, records in campaign_data.items():
        totals: dict[str, float] = {m: 0.0 for m in TRACKED_METRICS}
        for r in records:
            for m in TRACKED_METRICS:
                totals[m] += float(r.get(m, 0))

        summary[campaign] = {
            **totals,
            "ctr": compute_ctr(totals["clicks"], totals["impressions"]),
            "cpa": compute_cpa(totals["spend"], totals["conversions"]),
            "cvr": compute_cvr(totals["conversions"], totals["clicks"]),
            "roas": compute_roas(totals["revenue"], totals["spend"]),
            "record_count": len(records),
        }
    return summary
