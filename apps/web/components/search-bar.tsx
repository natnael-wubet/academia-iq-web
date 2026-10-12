"use client";

import { useState } from "react";
import { searchPapers, type SearchResponse, type SearchHit } from "@/lib/api";
import { paperHref } from "@/lib/hooks";

export function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      setResults(await searchPapers({ q: query, limit: 10 }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="flex flex-col gap-6">
      <form
        onSubmit={onSubmit}
        className="flex flex-col gap-3 rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl sm:flex-row"
      >
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search papers, authors, topics..."
          className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-sky-400"
        />
        <button
          type="submit"
          className="rounded-xl bg-sky-500 px-6 py-3 font-medium text-slate-950 hover:bg-sky-400 disabled:opacity-60"
          disabled={loading}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {results?.summary && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-300">
          <h2 className="mb-2 text-base font-medium text-slate-100">Field overview</h2>
          <p>{results.summary}</p>
        </div>
      )}

      {results && !results.summary && results.hits.length > 0 && (
        <p className="text-xs text-slate-500">
          {results.count} results in {results.took_ms} ms · set GROQ_API_KEY for AI summaries and
          reranking
        </p>
      )}

      {results && results.hits.length === 0 && (
        <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-8 text-center text-sm text-slate-400">
          No results yet. Ingest data with{" "}
          <code className="rounded bg-slate-800 px-1.5 py-0.5 text-slate-200">
            python -m packages.ingestion.openalex_ingest &quot;machine learning&quot; --pages 2
          </code>
        </div>
      )}

      <div className="grid gap-4">
        {results?.hits.map((hit) => (
          <ResultCard key={hit.id} hit={hit} />
        ))}
      </div>
    </section>
  );
}

function ResultCard({ hit }: { hit: SearchHit }) {
  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <a href={paperHref(hit.id)} className="text-lg font-medium text-slate-50 hover:text-sky-400">
        {hit.title}
      </a>
      {hit.abstract && (
        <p className="mt-2 line-clamp-4 text-sm leading-relaxed text-slate-300">{hit.abstract}</p>
      )}
      <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-400">
        {hit.publication_year && <span>Year: {hit.publication_year}</span>}
        <span>Cited: {hit.cited_by_count}</span>
        {hit.source && <span>Source: {hit.source}</span>}
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
        <a href={paperHref(hit.id)} className="text-sky-400 hover:text-sky-300">
          Details →
        </a>
      </div>
    </article>
  );
}
