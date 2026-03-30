import axios from "axios";
import type {
  Anomaly,
  DailyRecord,
  Insight,
  InvestigationResult,
  KpiSummary,
  ModelOptions,
  ProviderInfo,
  SegmentPerformance,
  Suggestion,
} from "../types";

const api = axios.create({
  baseURL: "https://aidata.christophbauer.dev/api",
  timeout: 60_000,
});

// ── LLM Provider ──────────────────────────────────────────────────────────────

export async function getProvider(): Promise<ProviderInfo> {
  const res = await api.get<ProviderInfo>("/llm/provider");
  return res.data;
}

export async function setProvider(provider: string, model: string): Promise<ProviderInfo> {
  const res = await api.post<ProviderInfo>("/llm/provider", { provider, model });
  return res.data;
}

export async function getModels(): Promise<ModelOptions> {
  const res = await api.get<ModelOptions>("/llm/models");
  return res.data;
}

export async function getLlmHealth(): Promise<{ provider: string; healthy: boolean }> {
  const res = await api.get("/llm/health");
  return res.data;
}

// ── Data ──────────────────────────────────────────────────────────────────────

export async function getCampaigns(): Promise<string[]> {
  const res = await api.get<{ campaigns: string[] }>("/data/campaigns");
  return res.data.campaigns;
}

export async function getAllTimeseries(): Promise<Record<string, DailyRecord[]>> {
  const res = await api.get<{ data: Record<string, DailyRecord[]> }>("/data/timeseries");
  return res.data.data;
}

export async function getTimeseries(campaign: string): Promise<DailyRecord[]> {
  const res = await api.get<{ data: DailyRecord[] }>(`/data/timeseries/${encodeURIComponent(campaign)}`);
  return res.data.data;
}

// ── Analytics ─────────────────────────────────────────────────────────────────

export async function getAnomalies(): Promise<Anomaly[]> {
  const res = await api.get<{ anomalies: Anomaly[] }>("/analytics/anomalies");
  return res.data.anomalies;
}

export async function getKpiSummary(): Promise<KpiSummary> {
  const res = await api.get<{ kpi_summary: KpiSummary }>("/analytics/kpi");
  return res.data.kpi_summary;
}

export async function getSegments(
  campaign: string,
  dimension: string
): Promise<SegmentPerformance[]> {
  const res = await api.get<{ segments: SegmentPerformance[] }>(
    `/analytics/segments/${encodeURIComponent(campaign)}`,
    { params: { dimension } }
  );
  return res.data.segments;
}

// ── Insights ──────────────────────────────────────────────────────────────────

export async function getInsights(): Promise<Insight[]> {
  const res = await api.get<{ insights: Insight[] }>("/insights");
  return res.data.insights;
}

export async function explainInsight(insightId: string): Promise<Insight> {
  const res = await api.post<Insight>("/insights/explain", { insight_id: insightId });
  return res.data;
}

// ── Suggestions ───────────────────────────────────────────────────────────────

export async function getSuggestions(): Promise<Suggestion[]> {
  const res = await api.get<{ suggestions: Suggestion[] }>("/suggestions");
  return res.data.suggestions;
}

export async function explainSuggestion(suggestionId: string): Promise<Suggestion> {
  const res = await api.post<Suggestion>("/suggestions/explain", { suggestion_id: suggestionId });
  return res.data;
}

// ── Investigation ─────────────────────────────────────────────────────────────

export async function investigate(
  question: string,
  contextHint?: string
): Promise<InvestigationResult> {
  const res = await api.post<InvestigationResult>("/investigate", {
    question,
    context_hint: contextHint,
  });
  return res.data;
}
