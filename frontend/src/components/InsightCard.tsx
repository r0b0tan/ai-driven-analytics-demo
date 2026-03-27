import { useState } from "react";
import { explainInsight } from "../api/client";
import type { Insight } from "../types";

const SEVERITY_COLORS: Record<string, string> = {
  high: "#ef4444",
  medium: "#f59e0b",
  low: "#10b981",
};

const TYPE_LABELS: Record<string, string> = {
  performance_drop: "Performance Drop",
  performance_spike: "Performance Spike",
  efficiency_gap: "Efficiency Gap",
  audience_shift: "Audience Shift",
};

interface Props {
  insight: Insight;
  onExplained?: (updated: Insight) => void;
}

export default function InsightCard({ insight, onExplained }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [localInsight, setLocalInsight] = useState(insight);

  const handleExplain = async () => {
    setLoading(true);
    setError(null);
    try {
      const updated = await explainInsight(localInsight.id);
      setLocalInsight(updated);
      onExplained?.(updated);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "LLM unavailable";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const pctChange = localInsight.data.deviation != null
    ? `${localInsight.data.deviation > 0 ? "+" : ""}${(localInsight.data.deviation * 100).toFixed(1)}%`
    : null;

  return (
    <div className={`insight-card insight-card--${localInsight.severity}`}>
      <div className="insight-card__header">
        <span
          className="insight-card__type-badge"
          style={{ backgroundColor: SEVERITY_COLORS[localInsight.severity] + "22",
                   color: SEVERITY_COLORS[localInsight.severity] }}
        >
          {TYPE_LABELS[localInsight.type] ?? localInsight.type}
        </span>
        <span className="insight-card__campaign">{localInsight.campaign}</span>
      </div>

      <h4 className="insight-card__title">{localInsight.title}</h4>
      <p className="insight-card__summary">{localInsight.summary}</p>

      <div className="insight-card__metrics">
        {pctChange && (
          <div className="insight-metric">
            <span className="insight-metric__label">Change</span>
            <span
              className="insight-metric__value"
              style={{ color: localInsight.data.deviation! < 0 ? "#ef4444" : "#10b981" }}
            >
              {pctChange}
            </span>
          </div>
        )}
        {localInsight.data.observed != null && (
          <div className="insight-metric">
            <span className="insight-metric__label">Observed</span>
            <span className="insight-metric__value">
              {Number(localInsight.data.observed).toLocaleString()}
            </span>
          </div>
        )}
        {localInsight.data.baseline != null && (
          <div className="insight-metric">
            <span className="insight-metric__label">Baseline</span>
            <span className="insight-metric__value">
              {Number(localInsight.data.baseline).toLocaleString()}
            </span>
          </div>
        )}
        <div className="insight-metric">
          <span className="insight-metric__label">Confidence</span>
          <span className="insight-metric__value">
            {(localInsight.confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {localInsight.top_contributor && (
        <div className="insight-card__contributor">
          <span className="insight-card__contributor-label">Primary driver</span>
          <span className="insight-card__contributor-value">
            {localInsight.top_contributor.segment}{" "}
            <span className="text-muted">({localInsight.top_contributor.dimension})</span>
          </span>
        </div>
      )}

      {localInsight.ai_explanation ? (
        <div className="insight-card__ai-explanation">
          <span className="ai-badge">AI Explanation</span>
          <p>{localInsight.ai_explanation}</p>
        </div>
      ) : (
        <button
          className="btn btn--ghost btn--sm"
          onClick={handleExplain}
          disabled={loading}
        >
          {loading ? "Asking AI…" : "Explain with AI"}
        </button>
      )}

      {error && <p className="error-text">{error}</p>}
    </div>
  );
}
