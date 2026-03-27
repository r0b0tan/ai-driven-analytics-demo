# Demo Story

## Scenario: "Why did Campaign A performance drop last week?"

This walkthrough demonstrates the full AI-assisted investigation flow.

---

### Act 1 — The Question

The user clicks the preset: **"Why did campaign performance drop yesterday?"**

The system immediately begins the 4-step investigation pipeline.

---

### Act 2 — Anomaly Detection

The pipeline scans 90 days of data across 3 campaigns.

It detects:

- **Campaign A clicks dropped 38%** on day 62 vs 7-day baseline
  - z-score: -2.8 (high severity)
  - Baseline: ~1,200 clicks/day → Observed: ~756 clicks/day

This is the injected `creative_fatigue` + `audience_saturation` event.

---

### Act 3 — Segment Analysis

The pipeline breaks down Campaign A by audience, device, creative, and region.

Audience analysis reveals:
- `18-24 mobile` — clicks are 38% below average (worst performer)
- `25-34 desktop` — near average
- `35-44 mobile` — slightly above average

Creative analysis reveals:
- `creative_v1` — CTR is 35% below average (creative fatigue signal)
- `creative_v2` and `creative_v3` are unaffected

---

### Act 4 — Contribution Analysis

The contribution engine attributes the total click drop by audience segment:

- `18-24 mobile` accounts for 62% of the total change
- High confidence (0.81) based on volume share

This is surfaced as the `top_contributor` on the insight card.

---

### Act 5 — Insights Generated

The system produces two structured insights:

1. **Campaign A clicks dropped 38% on 2024-11-22**
   - Type: `performance_drop`
   - Severity: high
   - Primary driver: `18-24 mobile` (audience)

2. **Efficiency gap in Campaign A — creative**
   - Type: `efficiency_gap`
   - `creative_v1` ROAS is 2.4× below `creative_v3`

---

### Act 6 — Suggestions

The suggestion engine produces:

1. **Shift budget from Campaign A to Campaign B**
   - Rule: `budget_shift_when_roas_gap_gt_1.2`
   - Campaign B ROAS: 5.40× vs Campaign A: 3.00×
   - Efficiency gain: 1.80×
   - Confidence: 0.82

2. **Refresh creative_v1 in Campaign A**
   - Rule: `creative_refresh_when_ctr_15pct_below_avg`
   - CTR is 35% below campaign average
   - Confidence: 0.78

3. **Pause 18-24 mobile in Campaign A**
   - Rule: `pause_audience_when_cpa_50pct_above_avg`
   - CPA 68% above campaign average
   - Confidence: 0.72

---

### Act 7 — AI Explanation

The user clicks **"Explain with AI"** on the budget shift suggestion.

The LLM receives the structured suggestion + KPI evidence and generates:

> "Campaign B is currently delivering a 5.40× ROAS compared to Campaign A's 3.00×,
> representing an 80% efficiency gap. Given that Campaign A is experiencing a
> significant click drop driven by audience saturation in the 18-24 mobile segment,
> reallocating budget toward Campaign B is expected to recover conversion volume
> at a substantially lower cost per acquisition."

The LLM did not produce any of the numbers — it only narrated them.

---

### What This Demonstrates

| Capability | How it shows |
|---|---|
| Explainable analytics | Decision traces on every suggestion |
| Deterministic pipelines | All metrics from `analytics/` — LLM never computes |
| Structured insight generation | Typed insight objects with severity, confidence, contributor |
| AI-assisted interpretation | On-demand narrative from pre-computed evidence |
| Traceable decision logic | `rule` field + full evidence on every suggestion |
