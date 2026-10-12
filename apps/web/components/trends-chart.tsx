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
import { getYearlyTrends, type TrendPoint } from "@/lib/api";

export function TrendsChart({ yearFrom = 2015 }: { yearFrom?: number }) {
  const [data, setData] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getYearlyTrends(yearFrom)
      .then((rows) => setData(rows))
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [yearFrom]);

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <h2 className="mb-4 text-lg font-medium text-slate-100">Research output &amp; citations</h2>
      {loading ? (
        <p className="text-sm text-slate-400">Loading publication trends...</p>
      ) : data.length === 0 ? (
        <p className="text-sm text-slate-400">
          No publication data yet. Import works to populate this chart.
        </p>
      ) : (
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data.map((d) => ({ name: d.year, works: d.works, citations: d.citations }))}>
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
      )}
    </section>
  );
}
