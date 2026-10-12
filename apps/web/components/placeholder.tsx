export function Placeholder({ title, children }: { title: string; children?: React.ReactNode }) {
  return (
    <section className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-6">
      <h2 className="mb-2 text-sm font-medium uppercase tracking-wide text-slate-400">{title}</h2>
      <div className="text-sm text-slate-400">
        {children ?? "No data available yet — populate the database via the ingestion pipelines."}
      </div>
    </section>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-8 text-center text-slate-400">
      {message}
    </div>
  );
}

export function Loading({ label = "Loading..." }: { label?: string }) {
  return <div className="p-8 text-center text-sm text-slate-400">{label}</div>;
}

export function ErrorNote({ message }: { message: string }) {
  return (
    <div className="rounded-2xl border border-rose-900 bg-rose-950/40 p-6 text-sm text-rose-200">
      {message}
    </div>
  );
}
