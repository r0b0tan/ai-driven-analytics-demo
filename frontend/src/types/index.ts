// ── LLM Provider ─────────────────────────────────────────────────────────────

export interface ProviderInfo {
  provider: "ollama" | "groq";
  model: string;
}

export interface ModelOptions {
  models: Record<string, string[]>;
  current: ProviderInfo;
}

// ── Analytics ─────────────────────────────────────────────────────────────────

export interface DailyRecord {
  date: string;
  impressions: number;
  clicks: number;
  spend: number;
  conversions: number;
  revenue: number;
}

export interface Anomaly {
  campaign: string;
  metric: string;
  date: string;
  observed: number;
  baseline: number;
  deviation: number;
  z_score: number | null;
  severity: "low" | "medium" | "high";
  direction: "drop" | "spike";
  evidence: Record<string, unknown>;
}

export interface SegmentPerformance {
  dimension: string;
  segment: string;
  metrics: Record<string, number>;
  vs_average: Record<string, number>;
  rank: number;
  label: "best" | "worst" | "average" | "";
}

// ── Insights ──────────────────────────────────────────────────────────────────

export interface Insight {
  id: string;
  type: "performance_drop" | "performance_spike" | "efficiency_gap" | "audience_shift";
  campaign: string;
  metric: string;
  title: string;
  summary: string;
  data: {
    observed?: number;
    baseline?: number;
    deviation?: number;
    z_score?: number | null;
    date?: string;
    evidence?: Record<string, unknown>;
    efficiency_gap?: number;
    best_segment?: string;
    worst_segment?: string;
    [key: string]: unknown;
  };
  confidence: number;
  severity: "low" | "medium" | "high";
  top_contributor: {
    dimension: string;
    segment: string;
    relative_impact: number;
    pct_change: number;
    confidence: number;
  } | null;
  ai_explanation: string | null;
}

// ── Suggestions ───────────────────────────────────────────────────────────────

export interface DecisionTrace {
  rule: string;
  [key: string]: unknown;
}

export interface Suggestion {
  id: string;
  type: "budget_shift" | "creative_refresh" | "audience_pause" | "bid_adjustment";
  campaign_from: string;
  campaign_to: string | null;
  action: string;
  rationale: string;
  expected_gain: number | null;
  confidence: number;
  decision_trace: DecisionTrace;
  ai_explanation: string | null;
}

// ── Investigation ─────────────────────────────────────────────────────────────

export interface PipelineStep {
  step: number;
  name: string;
  status: "running" | "complete" | "pending";
  found?: number;
}

export interface InvestigationResult {
  question: string;
  answer: string;
  evidence: {
    anomalies: Anomaly[];
    insights: Insight[];
    suggestions: Suggestion[];
  };
  pipeline_steps: PipelineStep[];
}

export interface KpiSummary {
  [campaign: string]: {
    clicks: number;
    impressions: number;
    spend: number;
    conversions: number;
    revenue: number;
    ctr: number | null;
    cpa: number | null;
    cvr: number | null;
    roas: number | null;
    record_count: number;
  };
}

// ── UI State ─────────────────────────────────────────────────────────────────

export type InvestigationPhase =
  | "idle"
  | "anomaly_detection"
  | "segment_analysis"
  | "contribution_analysis"
  | "insight_generation"
  | "complete";
