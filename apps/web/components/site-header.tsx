export function SiteHeader() {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <a href="/web" className="flex items-baseline gap-2">
          <span className="text-xl font-semibold tracking-tight text-slate-50">Academia IQ</span>
          <span className="hidden text-xs text-slate-400 sm:inline">research intelligence</span>
        </a>
        <nav className="flex items-center gap-6 text-sm text-slate-300">
          <a href="/web" className="hover:text-sky-400">
            Search
          </a>
          <a href="/web/paper/" className="hover:text-sky-400">
            Papers
          </a>
          <a href="/api/v1/docs" className="hover:text-sky-400">
            API
          </a>
        </nav>
      </div>
    </header>
  );
}
