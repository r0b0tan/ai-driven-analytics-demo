import { useCallback, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { getInsights, getSuggestions, investigate } from "../api/client";
import type { Insight, InvestigationResult, PipelineStep, Suggestion } from "../types";
import EvidencePanel from "../components/EvidencePanel";
import InsightCard from "../components/InsightCard";
import InvestigationTimeline from "../components/InvestigationTimeline";
import ModelSelector from "../components/ModelSelector";
import QuestionPanel from "../components/QuestionPanel";
import SuggestionCard from "../components/SuggestionCard";

const SECTIONS = ["investigation", "evidence", "insights", "suggestions"] as const;

export default function Dashboard() {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [result, setResult] = useState<InvestigationResult | null>(null);
  const [pipelineSteps, setPipelineSteps] = useState<PipelineStep[]>([]);
  const [loading, setLoading] = useState(false);
  const [dataLoading, setDataLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<typeof SECTIONS[number]>("investigation");
  const clickLockRef = useRef(false);

  // Click sets active immediately, pauses scroll detection briefly
  const handleNavClick = useCallback((id: typeof SECTIONS[number]) => {
    setActiveSection(id);
    clickLockRef.current = true;
    setTimeout(() => { clickLockRef.current = false; }, 800);
  }, []);

  // Track which section is visible on scroll (disabled briefly after click)
  useEffect(() => {
    const handleScroll = () => {
      if (clickLockRef.current) return;
      let current: typeof SECTIONS[number] = SECTIONS[0];
      for (const id of SECTIONS) {
        const el = document.getElementById(id);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.top <= 150) {
            current = id;
          }
        }
      }
      setActiveSection(current);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Load insights and suggestions on mount
  useEffect(() => {
    Promise.all([getInsights(), getSuggestions()])
      .then(([ins, sug]) => {
        setInsights(ins);
        setSuggestions(sug);
      })
      .catch(console.error)
      .finally(() => setDataLoading(false));
  }, []);

  const handleQuestion = async (question: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    // Show pending steps immediately
    setPipelineSteps([
      { step: 1, name: "Detect anomalies", status: "running" },
      { step: 2, name: "Segment analysis", status: "pending" },
      { step: 3, name: "Contribution analysis", status: "pending" },
      { step: 4, name: "Insight generation", status: "pending" },
    ]);

    try {
      const res = await investigate(question);
      setResult(res);
      setPipelineSteps(res.pipeline_steps);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Investigation failed";
      setError(msg);
      setPipelineSteps([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar__brand">
          <span className="sidebar__logo">&#9650;</span>
          <span className="sidebar__name">AI Analytics</span>
        </div>
        <nav className="sidebar__nav">
          {SECTIONS.map((id) => (
            <a
              key={id}
              href={`#${id}`}
              onClick={() => handleNavClick(id)}
              className={`sidebar__link${activeSection === id ? " sidebar__link--active" : ""}`}
            >
              {id.charAt(0).toUpperCase() + id.slice(1)}
            </a>
          ))}
        </nav>
        <div className="sidebar__section-title">LLM</div>
        <ModelSelector />
      </aside>

      {/* Main content */}
      <main className="main-content">
        <header className="page-header">
          <h1>Marketing Performance Investigation</h1>
          <p className="page-header__sub">
            AI-assisted analytics · Explainable decisions · Traceable reasoning
          </p>
        </header>

        {/* Question → Investigation → Evidence → Insights → Suggestions */}
        <section id="investigation" className="section">
          <QuestionPanel onSubmit={handleQuestion} loading={loading} />
        </section>

        {(loading || pipelineSteps.length > 0) && (
          <section className="section">
            <InvestigationTimeline steps={pipelineSteps} active={loading} />
          </section>
        )}

        {error && (
          <section className="section">
            <div className="error-banner">
              <strong>Error:</strong> {error}
            </div>
          </section>
        )}

        {result && (
          <section className="section">
            <div className="ai-answer">
              <div className="ai-answer__header">
                <span className="ai-badge">AI Analyst</span>
                <span className="ai-answer__question">{result.question}</span>
              </div>
              <div className="ai-answer__text"><ReactMarkdown>{result.answer}</ReactMarkdown></div>
            </div>
          </section>
        )}

        <section id="evidence" className="section">
          <EvidencePanel />
        </section>

        <section id="insights" className="section">
          <h3 className="section-title">
            Insights
            {dataLoading && <span className="text-muted"> loading…</span>}
          </h3>
          {insights.length === 0 && !dataLoading && (
            <p className="text-muted">No insights generated.</p>
          )}
          <div className="card-grid">
            {insights.slice(0, 6).map((insight) => (
              <InsightCard
                key={insight.id}
                insight={insight}
                onExplained={(updated) =>
                  setInsights((prev) =>
                    prev.map((i) => (i.id === updated.id ? updated : i))
                  )
                }
              />
            ))}
          </div>
        </section>

        <section id="suggestions" className="section">
          <h3 className="section-title">
            Recommendations
            {dataLoading && <span className="text-muted"> loading…</span>}
          </h3>
          {suggestions.length === 0 && !dataLoading && (
            <p className="text-muted">No suggestions generated.</p>
          )}
          <div className="card-grid">
            {suggestions.slice(0, 4).map((suggestion) => (
              <SuggestionCard key={suggestion.id} suggestion={suggestion} />
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
