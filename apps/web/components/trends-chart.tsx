"use client";

import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function TrendsChart() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";
    fetch(`${base}/trends/yearly?year_from=2015`)
      .then((r) => r.json())
      .then((d) => {
        setData(d.map((x: any) => ({ name: x.year, works: x.works, citations: x.citations })));
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-sm text-slate-400">Loading publication trends...</p>;
  }

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <h2 className="mb-4 text-lg font-medium text-slate-100">Research output & citations (2015–present)</h2>
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                background: "#020617",
                border: "1px solid #1e293b",
                borderRadius: "0.75rem",
                color: "#e2e8f0",
              }}
            />
            <Line type="monotone" dataKey="works" stroke="#38bdf8" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="citations" stroke="#22d3ee" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
