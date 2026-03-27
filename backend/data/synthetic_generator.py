"""
Synthetic marketing data generator.
Produces 90 days of campaign data with injected anomaly events.
"""
from __future__ import annotations

import math
import random
from datetime import date, timedelta
from typing import Any


# ── Campaign definitions ──────────────────────────────────────────────────────

CAMPAIGNS = {
    "Campaign A": {
        "base_impressions": 50_000,
        "base_clicks": 1_200,
        "base_spend": 800,
        "base_conversions": 48,
        "base_revenue": 2_400,
        "cpm_noise": 0.08,
    },
    "Campaign B": {
        "base_impressions": 35_000,
        "base_clicks": 900,
        "base_spend": 600,
        "base_conversions": 54,
        "base_revenue": 3_240,
        "cpm_noise": 0.06,
    },
    "Campaign C": {
        "base_impressions": 20_000,
        "base_clicks": 400,
        "base_spend": 300,
        "base_conversions": 18,
        "base_revenue": 720,
        "cpm_noise": 0.12,
    },
}

AUDIENCES = ["18-24 mobile", "25-34 desktop", "35-44 mobile", "45-54 desktop", "55+ desktop"]
DEVICES = ["mobile", "desktop", "tablet"]
CREATIVES = ["creative_v1", "creative_v2", "creative_v3"]
REGIONS = ["northeast", "southeast", "midwest", "west", "southwest"]

# Audience performance multipliers (relative to campaign base)
AUDIENCE_MULTIPLIERS = {
    "18-24 mobile":   {"clicks": 1.15, "conversions": 0.80, "spend": 0.95},
    "25-34 desktop":  {"clicks": 1.05, "conversions": 1.10, "spend": 1.00},
    "35-44 mobile":   {"clicks": 0.90, "conversions": 1.20, "spend": 1.05},
    "45-54 desktop":  {"clicks": 0.80, "conversions": 0.95, "spend": 0.90},
    "55+ desktop":    {"clicks": 0.60, "conversions": 0.70, "spend": 0.80},
}


# ── Injected anomaly events ───────────────────────────────────────────────────

EVENTS = [
    {
        "name": "creative_fatigue",
        "campaign": "Campaign A",
        "start_day": 55,
        "duration": 12,
        "effect": {"ctr": -0.60},
        "primary_dimension": "creative",
        "primary_segment": "creative_v1",
    },
    {
        "name": "audience_saturation",
        "campaign": "Campaign A",
        "start_day": 62,
        "duration": 8,
        "effect": {"clicks": -0.25, "conversions": -0.30},
        "primary_dimension": "audience",
        "primary_segment": "18-24 mobile",
    },
    {
        "name": "budget_cut",
        "campaign": "Campaign C",
        "start_day": 45,
        "duration": 15,
        "effect": {"impressions": -0.50, "spend": -0.45},
        "primary_dimension": "region",
        "primary_segment": "northeast",
    },
    {
        "name": "competitor_bid_spike",
        "campaign": "Campaign B",
        "start_day": 70,
        "duration": 7,
        "effect": {"spend": 0.35, "cpa": 0.40, "conversions": -0.20},
        "primary_dimension": "device",
        "primary_segment": "mobile",
    },
    {
        "name": "seasonal_boost",
        "campaign": "Campaign B",
        "start_day": 30,
        "duration": 10,
        "effect": {"clicks": 0.30, "conversions": 0.35, "revenue": 0.40},
        "primary_dimension": "audience",
        "primary_segment": "25-34 desktop",
    },
]


def _noise(scale: float = 0.08) -> float:
    return 1.0 + random.gauss(0, scale)


def _event_multiplier(
    day_index: int, campaign: str, metric: str
) -> float:
    multiplier = 1.0
    for event in EVENTS:
        if event["campaign"] != campaign:
            continue
        if event["start_day"] <= day_index < event["start_day"] + event["duration"]:
            effect = event["effect"].get(metric, 0)
            multiplier *= 1.0 + effect
    return multiplier


def generate_campaign_data(
    seed: int = 42, days: int = 90
) -> dict[str, list[dict[str, Any]]]:
    random.seed(seed)
    start_date = date(2024, 10, 1)
    all_data: dict[str, list[dict[str, Any]]] = {}

    for campaign, cfg in CAMPAIGNS.items():
        records: list[dict[str, Any]] = []

        for day_idx in range(days):
            current_date = start_date + timedelta(days=day_idx)
            day_of_week = current_date.weekday()
            # Weekday multiplier (lower on weekends for B2B-ish campaigns)
            day_mult = 0.75 if day_of_week >= 5 else 1.0

            # Slight downward trend over time to simulate ad fatigue
            trend = 1.0 - (day_idx / days) * 0.08

            for audience in AUDIENCES:
                aud_mult = AUDIENCE_MULTIPLIERS[audience]

                for device in DEVICES:
                    dev_mult = {"mobile": 1.1, "desktop": 0.95, "tablet": 0.65}[device]

                    for creative in CREATIVES:
                        creative_mult = {"creative_v1": 1.0, "creative_v2": 1.15, "creative_v3": 1.25}[creative]

                        for region in REGIONS:
                            region_mult = {
                                "northeast": 1.0,
                                "southeast": 0.92,
                                "midwest": 0.88,
                                "west": 1.05,
                                "southwest": 0.82,
                            }[region]

                            # Compute segment share of daily budget
                            segment_share = (1 / (len(AUDIENCES) * len(DEVICES) * len(CREATIVES) * len(REGIONS)))

                            impr = (
                                cfg["base_impressions"]
                                * segment_share
                                * day_mult
                                * trend
                                * dev_mult
                                * region_mult
                                * _event_multiplier(day_idx, campaign, "impressions")
                                * _noise(cfg["cpm_noise"])
                            )

                            # CTR affected by creative fatigue event for creative_v1
                            ctr_event_mult = 1.0
                            if creative == "creative_v1":
                                ctr_event_mult = _event_multiplier(day_idx, campaign, "ctr")

                            clicks = (
                                impr
                                * (cfg["base_clicks"] / cfg["base_impressions"])
                                * aud_mult["clicks"]
                                * creative_mult
                                * ctr_event_mult
                                * _event_multiplier(day_idx, campaign, "clicks")
                                * _noise(0.10)
                            )

                            spend = (
                                cfg["base_spend"]
                                * segment_share
                                * day_mult
                                * trend
                                * aud_mult["spend"]
                                * _event_multiplier(day_idx, campaign, "spend")
                                * _noise(0.07)
                            )

                            conversions = (
                                clicks
                                * (cfg["base_conversions"] / cfg["base_clicks"])
                                * aud_mult["conversions"]
                                * _event_multiplier(day_idx, campaign, "conversions")
                                * _noise(0.15)
                            )

                            revenue = conversions * (cfg["base_revenue"] / cfg["base_conversions"]) * _noise(0.06)

                            records.append({
                                "date": current_date.isoformat(),
                                "campaign": campaign,
                                "audience": audience,
                                "device": device,
                                "creative": creative,
                                "region": region,
                                "impressions": max(0, round(impr)),
                                "clicks": max(0, round(clicks)),
                                "spend": max(0.0, round(spend, 2)),
                                "conversions": max(0.0, round(conversions, 4)),
                                "revenue": max(0.0, round(revenue, 2)),
                            })

        all_data[campaign] = records

    return all_data


def aggregate_daily(
    records: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Aggregate granular segment records into daily campaign totals."""
    daily: dict[str, dict[str, Any]] = {}
    for r in records:
        d = r["date"]
        if d not in daily:
            daily[d] = {
                "date": d,
                "impressions": 0,
                "clicks": 0,
                "spend": 0.0,
                "conversions": 0.0,
                "revenue": 0.0,
            }
        daily[d]["impressions"] += r["impressions"]
        daily[d]["clicks"] += r["clicks"]
        daily[d]["spend"] = round(daily[d]["spend"] + r["spend"], 2)
        daily[d]["conversions"] += r["conversions"]
        daily[d]["revenue"] = round(daily[d]["revenue"] + r["revenue"], 2)

    for rec in daily.values():
        rec["conversions"] = int(round(rec["conversions"]))

    return sorted(daily.values(), key=lambda x: x["date"])


def get_events_metadata() -> list[dict[str, Any]]:
    return [
        {
            "name": e["name"],
            "campaign": e["campaign"],
            "start_day": e["start_day"],
            "duration": e["duration"],
            "primary_dimension": e["primary_dimension"],
            "primary_segment": e["primary_segment"],
        }
        for e in EVENTS
    ]
