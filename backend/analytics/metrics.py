"""
Deterministic metric calculations.
All numbers come from here — the LLM never computes these.
"""
from __future__ import annotations

import math
from typing import Any


def compute_ctr(clicks: float, impressions: float) -> float | None:
    if impressions == 0:
        return None
    return round(clicks / impressions, 4)


def compute_cpa(spend: float, conversions: float) -> float | None:
    if conversions == 0:
        return None
    return round(spend / conversions, 2)


def compute_roas(revenue: float, spend: float) -> float | None:
    if spend == 0:
        return None
    return round(revenue / spend, 2)


def compute_cvr(conversions: float, clicks: float) -> float | None:
    if clicks == 0:
        return None
    return round(conversions / clicks, 4)


def moving_average(values: list[float], window: int = 7) -> list[float | None]:
    result: list[float | None] = []
    for i, _ in enumerate(values):
        if i < window - 1:
            result.append(None)
        else:
            window_vals = values[i - window + 1 : i + 1]
            result.append(round(sum(window_vals) / window, 4))
    return result


def percent_change(baseline: float, observed: float) -> float:
    if baseline == 0:
        return 0.0
    return round((observed - baseline) / baseline, 4)


def z_score(value: float, mean: float, std: float) -> float | None:
    if std == 0:
        return None
    return round((value - mean) / std, 3)


def rolling_stats(
    values: list[float], window: int = 7
) -> list[dict[str, float | None]]:
    stats = []
    for i, v in enumerate(values):
        if i < window:
            stats.append({"mean": None, "std": None, "z_score": None})
            continue
        window_vals = values[i - window : i]
        mean = sum(window_vals) / window
        variance = sum((x - mean) ** 2 for x in window_vals) / window
        std = math.sqrt(variance)
        zs = z_score(v, mean, std)
        stats.append({"mean": round(mean, 4), "std": round(std, 4), "z_score": zs})
    return stats


def aggregate_by_dimension(
    records: list[dict[str, Any]], group_key: str, metrics: list[str]
) -> dict[str, dict[str, float]]:
    groups: dict[str, dict[str, list[float]]] = {}
    for rec in records:
        key = str(rec.get(group_key, "unknown"))
        if key not in groups:
            groups[key] = {m: [] for m in metrics}
        for m in metrics:
            val = rec.get(m)
            if val is not None:
                groups[key][m].append(float(val))

    result: dict[str, dict[str, float]] = {}
    for key, vals in groups.items():
        result[key] = {}
        for m in metrics:
            if vals[m]:
                result[key][m] = round(sum(vals[m]) / len(vals[m]), 4)
            else:
                result[key][m] = 0.0
    return result


def efficiency_ratio(metric_a: float, metric_b: float) -> float | None:
    """Returns metric_a / metric_b — used for comparing CPA across segments."""
    if metric_b == 0:
        return None
    return round(metric_a / metric_b, 3)
