import { Fragment } from "react";
import type { PipelineStep } from "../types";

const STEP_ICONS: Record<string, string> = {
  "Detect anomalies": "⚡",
  "Segment analysis": "🔬",
  "Contribution analysis": "📊",
  "Insight generation": "💡",
};

const DEFAULT_STEPS: PipelineStep[] = [
  { step: 1, name: "Detect anomalies", status: "pending" },
  { step: 2, name: "Segment analysis", status: "pending" },
  { step: 3, name: "Contribution analysis", status: "pending" },
  { step: 4, name: "Insight generation", status: "pending" },
];

interface Props {
  steps?: PipelineStep[];
  active: boolean;
}

export default function InvestigationTimeline({ steps, active }: Props) {
  const displaySteps = steps?.length ? steps : DEFAULT_STEPS;

  return (
    <div className="investigation-timeline">
      <h3 className="investigation-timeline__title">Investigation</h3>
      <div className="investigation-timeline__steps">
        {displaySteps.map((step, idx) => (
          <Fragment key={step.step}>
            <div
              className={`timeline-step timeline-step--${
                active && step.status === "running"
                  ? "running"
                  : step.status === "complete"
                  ? "complete"
                  : "pending"
              }`}
            >
              <div className="timeline-step__icon">
                {step.status === "complete"
                  ? "✓"
                  : step.status === "running"
                  ? <span className="spinner" />
                  : step.step}
              </div>
              <div className="timeline-step__body">
                <div className="timeline-step__name">
                  {STEP_ICONS[step.name] ?? ""} {step.name}
                </div>
                {step.found !== undefined && (
                  <div className="timeline-step__meta">
                    {step.found} anomaly{step.found !== 1 ? "ies" : ""} detected
                  </div>
                )}
              </div>
            </div>
            {idx < displaySteps.length - 1 && (
              <div className="timeline-connector" />
            )}
          </Fragment>
        ))}
      </div>
    </div>
  );
}
