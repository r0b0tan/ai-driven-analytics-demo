import { useState, type ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import { explainSuggestion } from "../api/client";
import type { Suggestion } from "../types";

const TYPE_ICONS: Record<string, ReactNode> = {
  budget_shift: (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="12" y1="1" x2="12" y2="23" />
      <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
    </svg>
  ),
  creative_refresh: (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="m9.06 11.9 8.07-8.06a2.85 2.85 0 1 1 4.03 4.03l-8.06 8.08" />
      <path d="M7.07 14.94c-1.66 0-3 1.35-3 3.02 0 1.33-2.5 1.52-2 2.02 1.08 1.1 2.49 2.02 4 2.02 2.2 0 4-1.8 4-4.04a3.01 3.01 0 0 0-3-3.02z" />
    </svg>
  ),
  audience_pause: (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="6" y="4" width="4" height="16" />
      <rect x="14" y="4" width="4" height="16" />
    </svg>
  ),
  bid_adjustment: (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
      <polyline points="17 6 23 6 23 12" />
    </svg>
  ),
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
        <span className="suggestion-card__icon">
          {TYPE_ICONS[local.type] ?? (
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          )}
        </span>
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
          <div className="ai-explanation__meta">
            <span className="ai-explanation__rule">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ display: "inline", verticalAlign: "middle", marginRight: "4px" }}>
                <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              Decision triggered by rule: <code>{local.decision_trace.rule}</code>
            </span>
            <span className="ai-explanation__conf">Confidence: {(local.confidence * 100).toFixed(0)}%</span>
          </div>
          <span className="ai-badge">AI Explanation</span>
          <ReactMarkdown>{local.ai_explanation}</ReactMarkdown>
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
