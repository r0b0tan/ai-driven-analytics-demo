import { useState } from "react";
import { explainSuggestion } from "../api/client";
import type { Suggestion } from "../types";

const TYPE_ICONS: Record<string, string> = {
  budget_shift: "💸",
  creative_refresh: "🎨",
  audience_pause: "⏸",
  bid_adjustment: "📈",
};

const TYPE_LABELS: Record<string, string> = {
  budget_shift: "Budget Shift",
  creative_refresh: "Creative Refresh",
  audience_pause: "Audience Pause",
  bid_adjustment: "Bid Adjustment",
};

interface Props {
  suggestion: Suggestion;
}

export default function SuggestionCard({ suggestion }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [local, setLocal] = useState(suggestion);
  const [showTrace, setShowTrace] = useState(false);

  const handleExplain = async () => {
    setLoading(true);
    setError(null);
    try {
      const updated = await explainSuggestion(local.id);
      setLocal(updated);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "LLM unavailable";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="suggestion-card">
      <div className="suggestion-card__header">
        <span className="suggestion-card__icon">{TYPE_ICONS[local.type] ?? "→"}</span>
        <span className="suggestion-card__type">{TYPE_LABELS[local.type] ?? local.type}</span>
        <span className="suggestion-card__confidence">
          {(local.confidence * 100).toFixed(0)}% confidence
        </span>
      </div>

      <h4 className="suggestion-card__action">{local.action}</h4>
      <p className="suggestion-card__rationale">{local.rationale}</p>

      {local.expected_gain != null && (
        <div className="suggestion-card__gain">
          <span className="suggestion-card__gain-label">Expected efficiency gain</span>
          <span className="suggestion-card__gain-value">{local.expected_gain}×</span>
        </div>
      )}

      {local.ai_explanation && (
        <div className="suggestion-card__ai-explanation">
          <span className="ai-badge">AI Explanation</span>
          <p>{local.ai_explanation}</p>
        </div>
      )}

      <div className="suggestion-card__footer">
        <button
          className="btn btn--ghost btn--sm"
          onClick={() => setShowTrace(!showTrace)}
        >
          {showTrace ? "Hide" : "Explain"} decision
        </button>

        {!local.ai_explanation && (
          <button
            className="btn btn--ghost btn--sm"
            onClick={handleExplain}
            disabled={loading}
          >
            {loading ? "Asking AI…" : "Ask AI"}
          </button>
        )}
      </div>

      {showTrace && (
        <div className="suggestion-card__trace">
          <div className="trace-row">
            <span className="trace-label">Decision rule</span>
            <code className="trace-value">{local.decision_trace.rule}</code>
          </div>
          {Object.entries(local.decision_trace)
            .filter(([k]) => k !== "rule")
            .map(([k, v]) => (
              <div key={k} className="trace-row">
                <span className="trace-label">{k.replace(/_/g, " ")}</span>
                <span className="trace-value">{String(v)}</span>
              </div>
            ))}
        </div>
      )}

      {error && <p className="error-text">{error}</p>}
    </div>
  );
}
