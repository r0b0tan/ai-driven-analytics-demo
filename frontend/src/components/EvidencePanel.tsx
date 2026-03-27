import { useEffect, useState } from "react";
import { getAllTimeseries, getAnomalies, getKpiSummary, getSegments } from "../api/client";
import type { Anomaly, DailyRecord, KpiSummary, SegmentPerformance } from "../types";
import CpaChart from "../charts/CpaChart";
import SegmentChart from "../charts/SegmentChart";
import TimeSeriesChart from "../charts/TimeSeriesChart";

type Metric = "clicks" | "impressions" | "spend" | "conversions" | "revenue";

const METRICS: Metric[] = ["clicks", "impressions", "spend", "conversions", "revenue"];

export default function EvidencePanel() {
  const [timeseries, setTimeseries] = useState<Record<string, DailyRecord[]>>({});
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [kpi, setKpi] = useState<KpiSummary>({});
  const [segments, setSegments] = useState<SegmentPerformance[]>([]);
  const [selectedMetric, setSelectedMetric] = useState<Metric>("clicks");
  const [selectedCampaign, setSelectedCampaign] = useState("Campaign A");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getAllTimeseries(),
      getAnomalies(),
      getKpiSummary(),
    ]).then(([ts, an, kp]) => {
      setTimeseries(ts);
      setAnomalies(an);
      setKpi(kp);
      setLoading(false);
    }).catch(console.error);
  }, []);

  useEffect(() => {
    getSegments(selectedCampaign, "audience")
      .then(setSegments)
      .catch(console.error);
  }, [selectedCampaign]);

  if (loading) {
    return <div className="evidence-panel evidence-panel--loading">Loading evidence…</div>;
  }

  const campaigns = Object.keys(timeseries);

  return (
    <div className="evidence-panel">
      <h3 className="section-title">Evidence</h3>

      {/* Controls */}
      <div className="evidence-panel__controls">
        <div className="control-group">
          <label>Metric</label>
          <div className="btn-group">
            {METRICS.map((m) => (
              <button
                key={m}
                className={`btn btn--sm ${selectedMetric === m ? "btn--active" : "btn--ghost"}`}
                onClick={() => setSelectedMetric(m)}
              >
                {m}
              </button>
            ))}
          </div>
        </div>
        <div className="control-group">
          <label>Campaign (segments)</label>
          <select
            value={selectedCampaign}
            onChange={(e) => setSelectedCampaign(e.target.value)}
          >
            {campaigns.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Time series chart */}
      <div className="chart-card">
        <h4 className="chart-title">
          Campaign {selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1)} Over Time
          {anomalies.some((a) => a.metric === selectedMetric) && (
            <span className="chart-title__badge">anomalies marked</span>
          )}
        </h4>
        <TimeSeriesChart
          data={timeseries}
          metric={selectedMetric}
          anomalies={anomalies}
        />
      </div>

      <div className="evidence-panel__row">
        {/* Segment breakdown */}
        <div className="chart-card chart-card--half">
          <h4 className="chart-title">
            {selectedCampaign} — Audience Clicks
          </h4>
          {segments.length > 0 ? (
            <SegmentChart segments={segments} metric="clicks" />
          ) : (
            <p className="text-muted">No segment data</p>
          )}
        </div>

        {/* CPA comparison */}
        <div className="chart-card chart-card--half">
          <CpaChart kpi={kpi} />
        </div>
      </div>

      {/* Anomaly table */}
      {anomalies.length > 0 && (
        <div className="anomaly-table">
          <h4 className="chart-title">Detected Anomalies ({anomalies.length})</h4>
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Campaign</th>
                <th>Metric</th>
                <th>Change</th>
                <th>Z-score</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody>
              {anomalies.slice(0, 10).map((a, i) => (
                <tr key={i}>
                  <td>{a.date}</td>
                  <td>{a.campaign}</td>
                  <td>{a.metric}</td>
                  <td
                    style={{ color: a.deviation < 0 ? "#ef4444" : "#10b981" }}
                  >
                    {a.deviation > 0 ? "+" : ""}
                    {(a.deviation * 100).toFixed(1)}%
                  </td>
                  <td>{a.z_score != null ? a.z_score.toFixed(2) : "—"}</td>
                  <td>
                    <span className={`severity-badge severity-badge--${a.severity}`}>
                      {a.severity}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
