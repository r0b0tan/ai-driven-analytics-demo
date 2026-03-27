"""
Contribution analysis — determines which segment/dimension drove an anomaly.
All arithmetic is deterministic; LLM only narrates the results.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .metrics import percent_change


@dataclass
class Contributor:
    dimension: str
    segment: str
    baseline_value: float
    observed_value: float
    absolute_impact: float      # raw delta (observed - baseline)
    relative_impact: float      # fraction of total change this segment explains
    pct_change: float           # within-segment percent change
    confidence: float           # 0-1 based on data volume and signal strength

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "segment": self.segment,
            "baseline_value": self.baseline_value,
            "observed_value": self.observed_value,
            "absolute_impact": round(self.absolute_impact, 4),
            "relative_impact": round(self.relative_impact, 4),
            "pct_change": round(self.pct_change, 4),
            "confidence": round(self.confidence, 3),
        }


def compute_contributions(
    baseline_segments: dict[str, float],
    observed_segments: dict[str, float],
    dimension: str,
) -> list[Contributor]:
    """
    For each segment, compute how much of the total change it explains.

    baseline_segments / observed_segments:
        {segment_name: metric_value}
    """
    total_baseline = sum(baseline_segments.values())
    total_observed = sum(observed_segments.values())
    total_delta = total_observed - total_baseline

    contributors: list[Contributor] = []

    all_segments = set(baseline_segments) | set(observed_segments)
    for seg in all_segments:
        base = baseline_segments.get(seg, 0.0)
        obs = observed_segments.get(seg, 0.0)
        delta = obs - base

        relative = (delta / total_delta) if total_delta != 0 else 0.0
        pct = percent_change(base, obs)

        # Confidence is higher when segment has more baseline volume
        volume_share = base / total_baseline if total_baseline > 0 else 0
        confidence = min(0.99, 0.5 + volume_share * 0.5)

        contributors.append(
            Contributor(
                dimension=dimension,
                segment=seg,
                baseline_value=round(base, 4),
                observed_value=round(obs, 4),
                absolute_impact=round(delta, 4),
                relative_impact=round(relative, 4),
                pct_change=pct,
                confidence=round(confidence, 3),
            )
        )

    # Sort by absolute relative impact descending
    contributors.sort(key=lambda c: abs(c.relative_impact), reverse=True)
    return contributors


def top_contributor(contributors: list[Contributor]) -> Contributor | None:
    if not contributors:
        return None
    return contributors[0]


def build_contribution_summary(
    contributors: list[Contributor],
    metric: str,
    direction: str,
) -> dict[str, Any]:
    top = top_contributor(contributors)
    if top is None:
        return {}

    return {
        "metric": metric,
        "direction": direction,
        "primary_driver": top.to_dict(),
        "all_contributors": [c.to_dict() for c in contributors],
        "explanation_inputs": {
            "top_segment": top.segment,
            "top_dimension": top.dimension,
            "relative_impact_pct": round(abs(top.relative_impact) * 100, 1),
            "segment_pct_change": round(top.pct_change * 100, 1),
        },
    }
