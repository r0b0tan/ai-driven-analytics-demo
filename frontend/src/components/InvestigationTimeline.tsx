import { Fragment, type ReactNode } from "react";
import type { PipelineStep } from "../types";

const STEP_ICONS: Record<string, ReactNode> = {
  "Detect anomalies": (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  ),
  "Segment analysis": (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
    </svg>
  ),
  "Contribution analysis": (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="18" y1="20" x2="18" y2="10" />
      <line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6" y1="20" x2="6" y2="14" />
    </svg>
  ),
  "Insight generation": (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5" />
      <path d="M9 18h6" />
      <path d="M10 22h4" />
    </svg>
  ),
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
