"""
Deterministic segment analysis.
Breaks down campaign performance by audience, device, creative, region, etc.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .metrics import (
    aggregate_by_dimension,
    compute_cpa,
    compute_ctr,
    compute_cvr,
    compute_roas,
    percent_change,
)


@dataclass
class SegmentPerformance:
    dimension: str
    segment: str
    metrics: dict[str, float]
    vs_average: dict[str, float]        # fractional deviation from campaign average
    rank: int = 0
    label: str = ""                     # "best" | "worst" | "average"

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "segment": self.segment,
            "metrics": self.metrics,
            "vs_average": self.vs_average,
            "rank": self.rank,
            "label": self.label,
        }


def analyze_segments(
    records: list[dict[str, Any]],
    dimension: str,
    primary_metric: str = "clicks",
) -> list[SegmentPerformance]:
    """
    Aggregate all records by `dimension` and rank segments by `primary_metric`.
    """
    raw_metrics = ["clicks", "impressions", "spend", "conversions", "revenue"]
    aggregated = aggregate_by_dimension(records, dimension, raw_metrics)

    # Compute derived metrics per segment
    enriched: dict[str, dict[str, float]] = {}
    for seg, agg in aggregated.items():
        m = dict(agg)
        m["ctr"] = compute_ctr(m.get("clicks", 0), m.get("impressions", 0)) or 0.0
        m["cpa"] = compute_cpa(m.get("spend", 0), m.get("conversions", 0)) or 0.0
        m["cvr"] = compute_cvr(m.get("conversions", 0), m.get("clicks", 0)) or 0.0
        m["roas"] = compute_roas(m.get("revenue", 0), m.get("spend", 0)) or 0.0
        enriched[seg] = m

    # Campaign-level averages for comparison
    all_vals: dict[str, list[float]] = {}
    for m_dict in enriched.values():
        for k, v in m_dict.items():
            all_vals.setdefault(k, []).append(v)
    averages = {k: sum(vs) / len(vs) for k, vs in all_vals.items() if vs}

    # Build SegmentPerformance objects
    performances: list[SegmentPerformance] = []
    for seg, m in enriched.items():
        vs_avg = {
            k: round(percent_change(averages.get(k, 0), v), 4)
            for k, v in m.items()
            if averages.get(k, 0) != 0
        }
        performances.append(
            SegmentPerformance(
                dimension=dimension,
                segment=seg,
                metrics={k: round(v, 4) for k, v in m.items()},
                vs_average=vs_avg,
            )
        )

    # Rank by primary metric descending
    performances.sort(
        key=lambda p: p.metrics.get(primary_metric, 0), reverse=True
    )
    for i, p in enumerate(performances):
        p.rank = i + 1

    if performances:
        performances[0].label = "best"
        performances[-1].label = "worst"
        for p in performances[1:-1]:
            p.label = "average"

    return performances


def find_worst_performers(
    segments: list[SegmentPerformance],
    metric: str = "cpa",
    top_n: int = 3,
) -> list[SegmentPerformance]:
    """Return segments with highest CPA (worst efficiency)."""
    return sorted(segments, key=lambda s: s.metrics.get(metric, 0), reverse=True)[:top_n]


def find_best_performers(
    segments: list[SegmentPerformance],
    metric: str = "roas",
    top_n: int = 3,
) -> list[SegmentPerformance]:
    return sorted(segments, key=lambda s: s.metrics.get(metric, 0), reverse=True)[:top_n]
