"""
Structured insight generation from pipeline results.
Produces typed insight objects — no LLM involvement at this stage.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Insight:
    id: str
    type: str           # performance_drop | performance_spike | audience_shift | efficiency_gap
    campaign: str
    metric: str
    title: str
    summary: str        # template-rendered, deterministic
    data: dict[str, Any]
    confidence: float
    severity: str
    top_contributor: dict[str, Any] | None = None
    ai_explanation: str | None = None  # filled later by LLM layer

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "campaign": self.campaign,
            "metric": self.metric,
            "title": self.title,
            "summary": self.summary,
            "data": self.data,
            "confidence": self.confidence,
            "severity": self.severity,
            "top_contributor": self.top_contributor,
            "ai_explanation": self.ai_explanation,
        }


def generate_insights(pipeline_result: dict[str, Any]) -> list[Insight]:
    insights: list[Insight] = []
    anomalies = pipeline_result.get("anomalies", [])
    contributions = pipeline_result.get("contributions", {})

    severity_key = {"high": 0, "medium": 1, "low": 2}
    # Take top 2 drops per campaign so each campaign gets representation
    seen_drop_campaigns: dict[str, int] = {}
    drops = []
    for a in sorted(
        [a for a in anomalies if a["direction"] == "drop"],
        key=lambda a: (severity_key[a["severity"]], -abs(a["deviation"]))
    ):
        count = seen_drop_campaigns.get(a["campaign"], 0)
        if count < 2:
            drops.append(a)
            seen_drop_campaigns[a["campaign"]] = count + 1
        if len(drops) >= 6:
            break
    spikes = sorted(
        [a for a in anomalies if a["direction"] == "spike"],
        key=lambda a: (severity_key[a["severity"]], -abs(a["deviation"]))
    )[:4]
    selected = sorted(
        drops + spikes,
        key=lambda a: (severity_key[a["severity"]], -abs(a["deviation"]))
    )
    for i, anomaly in enumerate(selected):
        insight_type = (
            "performance_drop" if anomaly["direction"] == "drop" else "performance_spike"
        )

        # Find primary contributor if available
        top_contrib = None
        for dim, contrib_data in contributions.items():
            if contrib_data.get("primary_driver"):
                top_contrib = {
                    "dimension": dim,
                    **contrib_data["primary_driver"],
                }
                break

        # Deterministic title and summary — no LLM
        direction_word = "dropped" if anomaly["direction"] == "drop" else "spiked"
        pct_display = abs(round(anomaly["deviation"] * 100, 1))
        title = (
            f"{anomaly['campaign']} {anomaly['metric']} {direction_word} "
            f"{pct_display}% on {anomaly['date']}"
        )

        if top_contrib:
            summary = (
                f"{anomaly['metric'].title()} {direction_word} {pct_display}% vs 7-day baseline. "
                f"Primary driver: {top_contrib['segment']} ({top_contrib['dimension']}) "
                f"accounts for {abs(round(top_contrib.get('relative_impact', 0) * 100, 1))}% of change."
            )
        else:
            summary = (
                f"{anomaly['metric'].title()} {direction_word} {pct_display}% vs 7-day baseline "
                f"(observed: {anomaly['observed']}, baseline: {anomaly['baseline']})."
            )

        insights.append(
            Insight(
                id=f"insight_{i:03d}",
                type=insight_type,
                campaign=anomaly["campaign"],
                metric=anomaly["metric"],
                title=title,
                summary=summary,
                data={
                    "observed": anomaly["observed"],
                    "baseline": anomaly["baseline"],
                    "deviation": anomaly["deviation"],
                    "z_score": anomaly.get("z_score"),
                    "date": anomaly["date"],
                    "evidence": anomaly.get("evidence", {}),
                },
                confidence=_compute_confidence(anomaly),
                severity=anomaly["severity"],
                top_contributor=top_contrib,
            )
        )

    # Add audience/efficiency insights from segment data
    segments = pipeline_result.get("segments", {})
    for campaign, dims in segments.items():
        for dim, segs in dims.items():
            if not segs:
                continue
            best = next((s for s in segs if s["label"] == "best"), None)
            worst = next((s for s in segs if s["label"] == "worst"), None)

            if best and worst:
                best_roas = best["metrics"].get("roas", 0)
                worst_roas = worst["metrics"].get("roas", 0)
                if worst_roas > 0 and best_roas / worst_roas > 1.5:
                    gap = round(best_roas / worst_roas, 2)
                    insights.append(
                        Insight(
                            id=f"insight_seg_{campaign}_{dim}",
                            type="efficiency_gap",
                            campaign=campaign,
                            metric="roas",
                            title=f"Efficiency gap detected in {campaign} — {dim}",
                            summary=(
                                f"{best['segment']} outperforms {worst['segment']} "
                                f"by {gap}× on ROAS ({dim} dimension)."
                            ),
                            data={
                                "dimension": dim,
                                "best_segment": best["segment"],
                                "worst_segment": worst["segment"],
                                "best_roas": best_roas,
                                "worst_roas": worst_roas,
                                "efficiency_gap": gap,
                            },
                            confidence=0.75,
                            severity="medium" if gap > 2.0 else "low",
                        )
                    )

    return insights


def _compute_confidence(anomaly: dict[str, Any]) -> float:
    base = 0.5
    z = anomaly.get("z_score")
    if z is not None:
        base += min(0.4, abs(z) * 0.1)
    pct = abs(anomaly.get("deviation", 0))
    base += min(0.1, pct * 0.2)
    return round(min(0.99, base), 3)
