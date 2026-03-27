import { useState } from "react";

const PRESET_QUESTIONS = [
  "Why did campaign performance drop yesterday?",
  "Which audience segment performs best?",
  "Where should we shift budget for maximum efficiency?",
  "What is causing the CPA increase in Campaign A?",
  "Which campaigns show signs of creative fatigue?",
];

interface Props {
  onSubmit: (question: string) => void;
  loading: boolean;
}

export default function QuestionPanel({ onSubmit, loading }: Props) {
  const [question, setQuestion] = useState("");

  const handleSubmit = () => {
    const q = question.trim();
    if (!q) return;
    onSubmit(q);
  };

  const handlePreset = (q: string) => {
    setQuestion(q);
    onSubmit(q);
  };

  return (
    <div className="question-panel">
      <div className="question-panel__header">
        <span className="question-panel__icon">&#128269;</span>
        <h2>Ask the AI Analyst</h2>
      </div>

      <div className="question-panel__input-row">
        <input
          className="question-panel__input"
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. Why did Campaign A clicks drop?"
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          disabled={loading}
        />
        <button
          className="btn btn--primary"
          onClick={handleSubmit}
          disabled={loading || !question.trim()}
        >
          {loading ? "Investigating…" : "Investigate"}
        </button>
      </div>

      <div className="question-panel__presets">
        <span className="question-panel__presets-label">Quick scenarios:</span>
        {PRESET_QUESTIONS.map((q) => (
          <button
            key={q}
            className="btn btn--ghost btn--sm"
            onClick={() => handlePreset(q)}
            disabled={loading}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
