"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Placeholder } from "@/components/placeholder";
import { getInstitution, getInstitutionStats, type Institution } from "@/lib/api";
import { useQueryParam } from "@/lib/hooks";

type Stats = {
  works_by_year: Record<string, number>;
  top_venue_ids: Record<string, number>;
};

export default function InstitutionPage() {
  const id = useQueryParam("id");
  const [institution, setInstitution] = useState<Institution | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.all([getInstitution(id), getInstitutionStats(id).catch(() => null)])
      .then(([inst, s]) => {
        setInstitution(inst);
        setStats(s);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (!id) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-12">
        <p className="text-slate-300">
          Open this page from an institution link, e.g. /web/institution/?id=1
        </p>
      </main>
    );
  }

  if (loading) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-12">
        <p className="text-slate-400">Loading institution...</p>
      </main>
    );
  }

  if (error || !institution) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-12">
        <Placeholder title="Institution profile">
          {error || "Institution not found."} Import works to populate institutional data.
        </Placeholder>
      </main>
    );
  }

  const byYear = Object.entries(stats?.works_by_year ?? {})
    .map(([year, works]) => ({ name: year, works }))
    .sort((a, b) => Number(a.name) - Number(b.name));

  return (
    <main className="mx-auto flex max-w-4xl flex-col gap-6 px-4 py-12">
      <a href="/web" className="text-sm text-sky-400 hover:text-sky-300">
        ← Back to search
      </a>

      <article className="rounded-2xl border border-slate-800 bg-slate-900/60 p-8">
        <h1 className="text-2xl font-semibold text-slate-50">{institution.name}</h1>
        <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-400">
          {institution.country_code && <span>{institution.country_code}</span>}
          {institution.type && <span>{institution.type}</span>}
          <span>{institution.works_count} works</span>
          <span>{institution.cited_by_count} citations</span>
        </div>
      </article>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="mb-4 text-lg font-medium text-slate-100">Output by year</h2>
        {byYear.length === 0 ? (
          <p className="text-sm text-slate-500">No per-year output recorded yet.</p>
        ) : (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byYear}>
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
                <Bar dataKey="works" fill="#38bdf8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </section>

      <Placeholder title="Institutional benchmarking">
        Rising-star detection, peer comparison, and recruitment intelligence appear here once enough
        institutions are indexed.
      </Placeholder>
    </main>
  );
}
