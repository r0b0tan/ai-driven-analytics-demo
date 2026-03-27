import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { DailyRecord, Anomaly } from "../types";

const CAMPAIGN_COLORS: Record<string, string> = {
  "Campaign A": "#6366f1",
  "Campaign B": "#10b981",
  "Campaign C": "#f59e0b",
};

interface Props {
  data: Record<string, DailyRecord[]>;
  metric: keyof Pick<DailyRecord, "clicks" | "impressions" | "spend" | "conversions" | "revenue">;
  anomalies?: Anomaly[];
  height?: number;
}

function mergeByDate(
  data: Record<string, DailyRecord[]>,
  metric: string
): Record<string, unknown>[] {
  const byDate: Record<string, Record<string, unknown>> = {};
  for (const [campaign, records] of Object.entries(data)) {
    for (const r of records) {
      if (!byDate[r.date]) byDate[r.date] = { date: r.date };
      byDate[r.date][campaign] = (r as unknown as Record<string, unknown>)[metric];
    }
  }
  return Object.values(byDate).sort((a, b) =>
    String(a.date).localeCompare(String(b.date))
  );
}

function formatDate(dateStr: unknown): string {
  const d = new Date(String(dateStr));
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

export default function TimeSeriesChart({ data, metric, anomalies = [], height = 280 }: Props) {
  const merged = mergeByDate(data, metric);
  const campaigns = Object.keys(data);

  const anomalyDates = new Set(
    anomalies
      .filter((a) => a.metric === metric)
      .map((a) => a.date)
  );

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={merged} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis
          dataKey="date"
          tickFormatter={formatDate}
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          interval={13}
        />
        <YAxis
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          tickFormatter={(v: number) => v >= 1000 ? `${(v / 1000).toFixed(1)}k` : String(v)}
        />
        <Tooltip
          contentStyle={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: 6 }}
          labelStyle={{ color: "#94a3b8" }}
          formatter={(value: unknown) => [(value as number).toLocaleString(), ""]}
          labelFormatter={formatDate}
        />
        <Legend
          wrapperStyle={{ fontSize: 12, color: "#94a3b8" }}
        />
        {campaigns.map((campaign) => (
          <Line
            key={campaign}
            type="monotone"
            dataKey={campaign}
            stroke={CAMPAIGN_COLORS[campaign] ?? "#888"}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        ))}
        {Array.from(anomalyDates).map((date) => (
          <ReferenceLine
            key={date}
            x={date}
            stroke="#ef4444"
            strokeDasharray="4 2"
            strokeWidth={1.5}
            label={{ value: "!", position: "top", fill: "#ef4444", fontSize: 10 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
