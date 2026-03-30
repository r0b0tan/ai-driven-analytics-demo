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
import type { SegmentPerformance } from "../types";

const LABEL_COLORS: Record<string, string> = {
  best: "#10b981",
  worst: "#ef4444",
  average: "#6366f1",
  "": "#6366f1",
};

interface Props {
  segments: SegmentPerformance[];
  metric?: string;
  height?: number;
}

export default function SegmentChart({
  segments,
  metric = "clicks",
  height = 220,
}: Props) {
  const data = segments.map((s) => ({
    name: s.segment,
    value: s.metrics[metric] ?? 0,
    label: s.label,
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 24 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis
          dataKey="name"
          tick={{ fill: "#94a3b8", fontSize: 10 }}
          angle={-30}
          textAnchor="end"
          interval={0}
        />
        <YAxis
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          tickFormatter={(v: number) => v >= 1000 ? `${(v / 1000).toFixed(1)}k` : String(v)}
        />
        <Tooltip
          contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 6 }}
          labelStyle={{ color: "#cbd5e1" }}
          itemStyle={{ color: "#f1f5f9" }}
          cursor={false}
          formatter={(v: unknown) => [(v as number).toLocaleString(), metric]}
        />
        <Bar dataKey="value" radius={[3, 3, 0, 0]} activeBar={{ filter: "brightness(1.4)" }}>
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={LABEL_COLORS[entry.label] ?? "#6366f1"}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
