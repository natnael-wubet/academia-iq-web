"use client";

import { useEffect, useState } from "react";
import { Placeholder } from "@/components/placeholder";
import {
  getWork,
  getWorkCitations,
  getWorkReferences,
  type Page,
  type Work,
} from "@/lib/api";
import { authorHref, institutionHref, useQueryParam } from "@/lib/hooks";

export default function PaperPage() {
  const id = useQueryParam("id");
  const [work, setWork] = useState<Work | null>(null);
  const [references, setReferences] = useState<Page<Work> | null>(null);
  const [citations, setCitations] = useState<Page<Work> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.all([
      getWork(id),
      getWorkReferences(id).catch(() => null),
      getWorkCitations(id).catch(() => null),
    ])
      .then(([w, refs, cites]) => {
        setWork(w);
        setReferences(refs);
        setCitations(cites);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (!id) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-12">
        <p className="text-slate-300">Open this page from a paper link, e.g. /web/paper/?id=1</p>
      </main>
    );
  }

  if (loading) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-12">
        <p className="text-slate-400">Loading paper...</p>
      </main>
    );
  }

  if (error || !work) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-12">
        <Placeholder title="Paper details">
          {error || "Paper not found."} Import papers, then open a result from search.
        </Placeholder>
      </main>
    );
  }

  return (
    <main className="mx-auto flex max-w-4xl flex-col gap-6 px-4 py-12">
      <a href="/web" className="text-sm text-sky-400 hover:text-sky-300">
        ← Back to search
      </a>

      <article className="rounded-2xl border border-slate-800 bg-slate-900/60 p-8">
        <h1 className="text-2xl font-semibold text-slate-50">{work.title}</h1>
        <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-400">
          {work.publication_year && <span>{work.publication_year}</span>}
          <span>Cited by {work.cited_by_count}</span>
          {work.venue && <span>{work.venue.name}</span>}
          {work.is_open_access && (
            <span className="rounded-full bg-emerald-900/50 px-2 py-0.5 text-emerald-300">
              Open Access
            </span>
          )}
          {work.source && <span>via {work.source}</span>}
          {work.doi && (
            <a
              href={`https://doi.org/${work.doi}`}
              target="_blank"
              rel="noreferrer"
              className="text-sky-400 hover:text-sky-300"
            >
              doi:{work.doi}
            </a>
          )}
        </div>

        {work.abstract ? (
          <p className="mt-6 leading-relaxed text-slate-200">{work.abstract}</p>
        ) : (
          <p className="mt-6 text-sm italic text-slate-500">
            No abstract stored for this work.
          </p>
        )}

        {work.authors.length > 0 && (
          <div className="mt-6">
            <h2 className="mb-2 text-sm font-medium text-slate-400">Authors</h2>
            <div className="flex flex-wrap gap-2">
              {work.authors.map((a) => (
                <a
                  key={a.id}
                  href={authorHref(a.id)}
                  className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-sm text-slate-200 hover:border-sky-500 hover:text-sky-400"
                >
                  {a.display_name}
                </a>
              ))}
            </div>
          </div>
        )}
      </article>

      <Placeholder title="AI summary">
        One-click abstract summarisation appears here once GROQ_API_KEY is configured.
      </Placeholder>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="mb-3 text-lg font-medium text-slate-100">
          References <span className="text-sm text-slate-500">({references?.total ?? 0})</span>
        </h2>
        <WorkList works={references?.items ?? []} empty="No reference links stored for this paper." />
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="mb-3 text-lg font-medium text-slate-100">
          Cited by <span className="text-sm text-slate-500">({citations?.total ?? 0})</span>
        </h2>
        <WorkList works={citations?.items ?? []} empty="No citing works recorded yet." />
      </section>
    </main>
  );
}

function WorkList({ works, empty }: { works: Work[]; empty: string }) {
  if (works.length === 0) {
    return <p className="text-sm text-slate-500">{empty}</p>;
  }
  return (
    <ul className="flex flex-col gap-3">
      {works.map((w) => (
        <li key={w.id} className="border-b border-slate-800 pb-3 last:border-0 last:pb-0">
          <a href={`/web/paper/?id=${w.id}`} className="text-slate-200 hover:text-sky-400">
            {w.title}
          </a>
          <div className="mt-1 text-xs text-slate-500">
            {w.publication_year ?? "—"} · cited by {w.cited_by_count}
          </div>
        </li>
      ))}
    </ul>
  );
}
