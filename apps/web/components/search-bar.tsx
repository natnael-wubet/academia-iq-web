"use client";

import { useState } from "react";

export function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setSummary(null);
    try {
      const params = new URLSearchParams({ q: query, limit: "10", mode: "hybrid", rerank: "true" });
      const base = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";
      const res = await fetch(`${base}/search?${params.toString()}`);
      const data = await res.json();
      setResults(data.hits || []);
      setSummary(data.summary || null);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="flex flex-col gap-6">
      <form onSubmit={onSubmit} className="flex flex-col gap-3 rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl sm:flex-row">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search papers, authors, topics..."
          className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-sky-400"
        />
        <button
          type="submit"
          className="rounded-xl bg-sky-500 px-6 py-3 font-medium text-slate-950 hover:bg-sky-400"
          disabled={loading}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {summary && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-300">
          <h2 className="mb-2 text-base font-medium text-slate-100">Field overview</h2>
          <p>{summary}</p>
        </div>
      )}

      <div className="grid gap-4">
        {results.map((hit) => (
          <article key={hit.id} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <h3 className="text-lg font-medium text-slate-50">{hit.title}</h3>
            {hit.abstract && (
              <p className="mt-2 line-clamp-4 text-sm leading-relaxed text-slate-300">{hit.abstract}</p>
            )}
            <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-400">
              {hit.publication_year && <span>Year: {hit.publication_year}</span>}
              <span>Cited: {hit.cited_by_count}</span>
              {hit.doi && (
                <a
                  href={`https://doi.org/${hit.doi}`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-sky-400 hover:text-sky-300"
                >
                  DOI
                </a>
              )}
              {hit.source && <span>Source: {hit.source}</span>}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
