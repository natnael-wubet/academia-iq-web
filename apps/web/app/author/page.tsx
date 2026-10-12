"use client";

import { useEffect, useState } from "react";
import { Placeholder } from "@/components/placeholder";
import { getAuthor, getAuthorWorks, type Author, type Work } from "@/lib/api";
import { institutionHref, useQueryParam } from "@/lib/hooks";

export default function AuthorPage() {
  const id = useQueryParam("id");
  const [author, setAuthor] = useState<Author | null>(null);
  const [works, setWorks] = useState<Work[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.all([getAuthor(id), getAuthorWorks(id).catch(() => [])])
      .then(([a, w]) => {
        setAuthor(a);
        setWorks(w);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (!id) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-12">
        <p className="text-slate-300">Open this page from an author link, e.g. /web/author/?id=1</p>
      </main>
    );
  }

  if (loading) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-12">
        <p className="text-slate-400">Loading author...</p>
      </main>
    );
  }

  if (error || !author) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-12">
        <Placeholder title="Author profile">
          {error || "Author not found."} Import works to populate researcher profiles.
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
        <h1 className="text-2xl font-semibold text-slate-50">{author.display_name}</h1>
        <div className="mt-4 flex flex-wrap gap-6 text-sm text-slate-300">
          <span>Works: {author.works_count}</span>
          <span>Citations: {author.cited_by_count}</span>
          <span>h-index: {author.h_index ?? "—"}</span>
          {author.orcid && (
            <a
              href={`https://orcid.org/${author.orcid}`}
              target="_blank"
              rel="noreferrer"
              className="text-sky-400 hover:text-sky-300"
            >
              ORCID {author.orcid}
            </a>
          )}
          {author.institution && (
            <a href={institutionHref(author.institution.id)} className="text-sky-400 hover:text-sky-300">
              {author.institution.name}
            </a>
          )}
        </div>
      </article>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="mb-3 text-lg font-medium text-slate-100">Publications</h2>
        {works.length === 0 ? (
          <p className="text-sm text-slate-500">No works linked to this author yet.</p>
        ) : (
          <ul className="flex flex-col gap-3">
            {works.map((w) => (
              <li key={w.id} className="border-b border-slate-800 pb-3 last:border-0 last:pb-0">
                <a href={`/web/paper/?id=${w.id}`} className="text-slate-200 hover:text-sky-400">
                  {w.title}
                </a>
                <div className="mt-1 text-xs text-slate-500">
                  {w.publication_year ?? "—"}
                  {w.venue ? ` · ${w.venue.name}` : ""} · cited by {w.cited_by_count}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <Placeholder title="Collaboration matchmaker">
        Complementary-expertise suggestions and co-author recommendations appear here once
        embeddings are indexed in Weaviate.
      </Placeholder>
    </main>
  );
}
