"""
Deterministic suggestion engine.
Produces actionable recommendations from insight + segment data.
Every suggestion includes full decision trace for explainability.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from analytics.metrics import efficiency_ratio


@dataclass
class Suggestion:
    id: str
    type: str           # budget_shift | creative_refresh | audience_pause | bid_adjustment
    campaign_from: str
    campaign_to: str | None
    action: str         # short imperative sentence
    rationale: str      # deterministic explanation
    expected_gain: float | None    # efficiency multiplier
    confidence: float
    decision_trace: dict[str, Any] = field(default_factory=dict)
    ai_explanation: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "campaign_from": self.campaign_from,
            "campaign_to": self.campaign_to,
            "action": self.action,
            "rationale": self.rationale,
            "expected_gain": self.expected_gain,
            "confidence": self.confidence,
            "decision_trace": self.decision_trace,
            "ai_explanation": self.ai_explanation,
        }


def generate_suggestions(
    insights: list[Any],
    pipeline_result: dict[str, Any],
) -> list[Suggestion]:
    suggestions: list[Suggestion] = []
    kpi = pipeline_result.get("kpi_summary", {})
    segments = pipeline_result.get("segments", {})

    suggestions.extend(_budget_shift_suggestions(insights, kpi))
    suggestions.extend(_creative_refresh_suggestions(insights, segments))
    suggestions.extend(_audience_suggestions(insights, segments))

    # Deduplicate by (type, campaign_from)
    seen = set()
    unique: list[Suggestion] = []
    for s in suggestions:
        key = (s.type, s.campaign_from)
        if key not in seen:
            seen.add(key)
            unique.append(s)

    # Sort by confidence desc
    unique.sort(key=lambda s: s.confidence, reverse=True)
    return unique


def _budget_shift_suggestions(
    insights: list[Any],
    kpi: dict[str, Any],
) -> list[Suggestion]:
    suggestions: list[Suggestion] = []

    # Find campaigns with performance drops and alternatives with better ROAS
    drop_campaigns = [
        i for i in insights
        if i.type == "performance_drop" and i.metric in ("clicks", "conversions")
    ]
    if not drop_campaigns or len(kpi) < 2:
        return suggestions

    # Rank all campaigns by ROAS
    ranked_by_roas = sorted(
        [(c, m.get("roas") or 0) for c, m in kpi.items()],
        key=lambda x: x[1],
        reverse=True,
    )
    if len(ranked_by_roas) < 2:
        return suggestions

    best_campaign, best_roas = ranked_by_roas[0]

    for insight in drop_campaigns[:3]:
        if insight.campaign == best_campaign:
            continue
        from_roas = kpi.get(insight.campaign, {}).get("roas") or 0
        if best_roas == 0 or from_roas == 0:
            continue

        gap = efficiency_ratio(best_roas, from_roas)
        if gap is None or gap < 1.2:
            continue

        confidence = min(0.95, 0.5 + abs(insight.data.get("deviation", 0)) * 0.5)

        suggestions.append(
            Suggestion(
                id=f"sug_budget_{insight.campaign}",
                type="budget_shift",
                campaign_from=insight.campaign,
                campaign_to=best_campaign,
                action=f"Shift budget from {insight.campaign} to {best_campaign}",
                rationale=(
                    f"{insight.campaign} ROAS is {round(from_roas, 2)}× vs "
                    f"{best_campaign} at {round(best_roas, 2)}×. "
                    f"Reallocation offers {round(gap, 2)}× efficiency improvement."
                ),
                expected_gain=round(gap, 2),
                confidence=round(confidence, 3),
                decision_trace={
                    "rule": "budget_shift_when_roas_gap_gt_1.2",
                    "from_roas": round(from_roas, 2),
                    "to_roas": round(best_roas, 2),
                    "efficiency_ratio": round(gap, 2),
                    "trigger": f"{insight.metric} drop of {round(abs(insight.data.get('deviation', 0)) * 100, 1)}%",
                    "baseline_comparison": "7-day rolling average",
                },
            )
        )

    return suggestions


def _creative_refresh_suggestions(
    insights: list[Any],
    segments: dict[str, Any],
) -> list[Suggestion]:
    suggestions: list[Suggestion] = []

    for insight in insights:
        if insight.type not in ("performance_drop", "efficiency_gap"):
            continue

        campaign_segs = segments.get(insight.campaign, {})
        creative_segs = campaign_segs.get("creative", [])
        if not creative_segs:
            continue

        worst = next((s for s in reversed(creative_segs) if s.get("label") == "worst"), None)
        if not worst:
            continue

        ctr_drop = worst.get("vs_average", {}).get("ctr", 0)
        if ctr_drop > -0.15:  # Only suggest refresh if CTR is >15% below average
            continue

        confidence = min(0.9, 0.6 + abs(ctr_drop) * 0.5)

        suggestions.append(
            Suggestion(
                id=f"sug_creative_{insight.campaign}",
                type="creative_refresh",
                campaign_from=insight.campaign,
                campaign_to=None,
                action=f"Refresh creative '{worst['segment']}' in {insight.campaign}",
                rationale=(
                    f"Creative '{worst['segment']}' CTR is "
                    f"{round(abs(ctr_drop) * 100, 1)}% below campaign average — "
                    "indicating creative fatigue."
                ),
                expected_gain=None,
                confidence=round(confidence, 3),
                decision_trace={
                    "rule": "creative_refresh_when_ctr_15pct_below_avg",
                    "segment": worst["segment"],
                    "ctr": worst["metrics"].get("ctr"),
                    "ctr_vs_average": round(ctr_drop * 100, 1),
                    "threshold": -15.0,
                },
            )
        )

    return suggestions


def _audience_suggestions(
    insights: list[Any],
    segments: dict[str, Any],
) -> list[Suggestion]:
    suggestions: list[Suggestion] = []

    for insight in insights:
        campaign_segs = segments.get(insight.campaign, {})
        audience_segs = campaign_segs.get("audience", [])
        if not audience_segs:
            continue

        worst_audience = next(
            (s for s in reversed(audience_segs) if s.get("label") == "worst"), None
        )
        if not worst_audience:
            continue

        cpa = worst_audience["metrics"].get("cpa", 0)
        avg_cpa = sum(
            s["metrics"].get("cpa", 0) for s in audience_segs
        ) / len(audience_segs) if audience_segs else 0

        if avg_cpa == 0 or cpa / avg_cpa < 1.5:
            continue

        confidence = min(0.88, 0.55 + (cpa / avg_cpa - 1) * 0.1)

        suggestions.append(
            Suggestion(
                id=f"sug_audience_{insight.campaign}_{worst_audience['segment']}",
                type="audience_pause",
                campaign_from=insight.campaign,
                campaign_to=None,
                action=f"Pause or reduce bids for '{worst_audience['segment']}' in {insight.campaign}",
                rationale=(
                    f"Audience '{worst_audience['segment']}' CPA is {round(cpa, 2)} "
                    f"vs campaign average of {round(avg_cpa, 2)} "
                    f"({round((cpa/avg_cpa - 1)*100, 1)}% above average)."
                ),
                expected_gain=None,
                confidence=round(confidence, 3),
                decision_trace={
                    "rule": "pause_audience_when_cpa_50pct_above_avg",
                    "segment": worst_audience["segment"],
                    "segment_cpa": round(cpa, 2),
                    "campaign_avg_cpa": round(avg_cpa, 2),
                    "cpa_ratio": round(cpa / avg_cpa, 2),
                    "threshold": 1.5,
                },
            )
        )

    return suggestions
