"""
Deterministic anomaly detection.
Compares recent values against rolling baselines — no LLM involvement.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from .metrics import rolling_stats, percent_change


ANOMALY_Z_THRESHOLD = 2.0       # |z| > 2 triggers an anomaly
ANOMALY_PCT_THRESHOLD = 0.15    # |% change| > 15% triggers an anomaly


@dataclass
class Anomaly:
    campaign: str
    metric: str
    date: str
    observed: float
    baseline: float
    deviation: float        # fractional: -0.37 means -37%
    z_score: float | None
    severity: str           # "low" | "medium" | "high"
    direction: str          # "drop" | "spike"
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "campaign": self.campaign,
            "metric": self.metric,
            "date": self.date,
            "observed": self.observed,
            "baseline": self.baseline,
            "deviation": self.deviation,
            "z_score": self.z_score,
            "severity": self.severity,
            "direction": self.direction,
            "evidence": self.evidence,
        }


def _severity(z: float | None, pct: float) -> str:
    abs_pct = abs(pct)
    abs_z = abs(z) if z is not None else 0
    if abs_pct > 0.35 or abs_z > 3.0:
        return "high"
    if abs_pct > 0.20 or abs_z > 2.5:
        return "medium"
    return "low"


def detect_anomalies(
    time_series: list[dict[str, Any]],
    campaign: str,
    metric: str,
    date_key: str = "date",
    value_key: str | None = None,
    window: int = 7,
) -> list[Anomaly]:
    """
    Scan a time series and return all anomalous points.

    Parameters
    ----------
    time_series : list of dicts sorted ascending by date
    campaign    : campaign name for labelling
    metric      : metric name for labelling
    date_key    : key in each record for the date string
    value_key   : key for the metric value; defaults to `metric`
    window      : rolling baseline window
    """
    if value_key is None:
        value_key = metric

    values = [float(r[value_key]) for r in time_series if r.get(value_key) is not None]
    dates = [r[date_key] for r in time_series if r.get(value_key) is not None]

    if len(values) < window + 1:
        return []

    stats = rolling_stats(values, window)
    anomalies: list[Anomaly] = []

    for i in range(window, len(values)):
        stat = stats[i]
        if stat["mean"] is None:
            continue

        pct = percent_change(stat["mean"], values[i])
        zs = stat["z_score"]

        is_anomaly = abs(pct) > ANOMALY_PCT_THRESHOLD or (
            zs is not None and abs(zs) > ANOMALY_Z_THRESHOLD
        )

        if is_anomaly:
            anomalies.append(
                Anomaly(
                    campaign=campaign,
                    metric=metric,
                    date=dates[i],
                    observed=round(values[i], 4),
                    baseline=round(stat["mean"], 4),
                    deviation=pct,
                    z_score=zs,
                    severity=_severity(zs, pct),
                    direction="drop" if pct < 0 else "spike",
                    evidence={
                        "rolling_mean": stat["mean"],
                        "rolling_std": stat["std"],
                        "window_days": window,
                        "pct_threshold": ANOMALY_PCT_THRESHOLD,
                        "z_threshold": ANOMALY_Z_THRESHOLD,
                    },
                )
            )

    return anomalies


def find_most_recent_anomaly(
    anomalies: list[Anomaly],
) -> Anomaly | None:
    if not anomalies:
        return None
    return max(anomalies, key=lambda a: (a.date, abs(a.deviation)))


def rank_anomalies(anomalies: list[Anomaly]) -> list[Anomaly]:
    severity_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(
        anomalies,
        key=lambda a: (severity_order[a.severity], -abs(a.deviation)),
    )
