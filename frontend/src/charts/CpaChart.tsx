import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { KpiSummary } from "../types";

interface Props {
  kpi: KpiSummary;
  height?: number;
}

export default function CpaChart({ kpi, height = 200 }: Props) {
  const data = Object.entries(kpi)
    .filter(([, m]) => m.cpa != null)
    .map(([campaign, m]) => ({
      campaign,
      cpa: m.cpa ?? 0,
      roas: m.roas ?? 0,
    }))
    .sort((a, b) => a.cpa - b.cpa);

  const minCpa = data[0]?.cpa ?? 0;

  return (
    <div className="cpa-chart">
      <h4 className="chart-title">CPA by Campaign</h4>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="campaign" tick={{ fill: "#94a3b8", fontSize: 11 }} />
          <YAxis
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            tickFormatter={(v: number) => `$${v.toFixed(0)}`}
          />
          <Tooltip
            contentStyle={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: 6 }}
            formatter={(v: unknown) => [`$${(v as number).toFixed(2)}`, "CPA"]}
          />
          <Bar dataKey="cpa" radius={[3, 3, 0, 0]}>
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.cpa === minCpa ? "#10b981" : entry.cpa > minCpa * 1.5 ? "#ef4444" : "#6366f1"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
