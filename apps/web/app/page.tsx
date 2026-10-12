import { SearchBar } from "@/components/search-bar";
import { TrendsChart } from "@/components/trends-chart";

export default function Home() {
  return (
    <main className="mx-auto flex max-w-6xl flex-col gap-8 px-4 py-12">
      <header className="flex flex-col gap-4 text-center">
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Academia IQ</h1>
        <p className="text-slate-300">
          Hybrid search across OpenAlex, Semantic Scholar, Crossref, and ORCID. Zero-cost blueprint
          in action.
        </p>
      </header>
      <SearchBar />
      <TrendsChart />
    </main>
  );
}
