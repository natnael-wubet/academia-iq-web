export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "/api/v1";
export const WEB_BASE = "/web";

export type Venue = {
  id: number;
  name: string;
  issn_l: string | null;
  type: string | null;
  works_count: number;
};

export type Author = {
  id: number;
  display_name: string;
  orcid: string | null;
  h_index: number | null;
  works_count: number;
  cited_by_count: number;
  institution: Institution | null;
};

export type Institution = {
  id: number;
  name: string;
  country_code: string | null;
  type: string | null;
  works_count: number;
  cited_by_count: number;
};

export type Work = {
  id: number;
  title: string;
  abstract: string | null;
  doi: string | null;
  publication_date: string | null;
  publication_year: number | null;
  cited_by_count: number;
  is_open_access: boolean;
  source: string | null;
  venue: Venue | null;
  authors: Author[];
};

export type SearchHit = {
  id: number;
  title: string;
  abstract: string | null;
  publication_year: number | null;
  cited_by_count: number;
  doi: string | null;
  score: number;
  source: string | null;
};

export type SearchResponse = {
  query: string;
  mode: string;
  count: number;
  took_ms: number;
  hits: SearchHit[];
  summary: string | null;
};

export type Page<T> = {
  total: number;
  limit: number;
  offset: number;
  items: T[];
};

export type TrendPoint = {
  year: number;
  works: number;
  citations: number;
};

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`Request failed (${res.status}): ${path}`);
  }
  return (await res.json()) as T;
}

export function searchPapers(params: {
  q: string;
  limit?: number;
  mode?: string;
  rerank?: boolean;
}): Promise<SearchResponse> {
  const qs = new URLSearchParams({
    q: params.q,
    limit: String(params.limit ?? 10),
    mode: params.mode ?? "hybrid",
    rerank: String(params.rerank ?? true),
  });
  return get<SearchResponse>(`/search?${qs.toString()}`);
}

export function listWorks(limit = 25, offset = 0): Promise<Page<Work>> {
  return get<Page<Work>>(`/works?limit=${limit}&offset=${offset}`);
}

export function getWork(id: number | string): Promise<Work> {
  return get<Work>(`/works/${id}`);
}

export function getWorkReferences(id: number | string): Promise<Page<Work>> {
  return get<Page<Work>>(`/works/${id}/references`);
}

export function getWorkCitations(id: number | string): Promise<Page<Work>> {
  return get<Page<Work>>(`/works/${id}/cited-by`);
}

export function getAuthor(id: number | string): Promise<Author> {
  return get<Author>(`/authors/${id}`);
}

export function getAuthorWorks(id: number | string, limit = 25): Promise<Work[]> {
  return get<Work[]>(`/authors/${id}/works?limit=${limit}`);
}

export function getInstitution(id: number | string): Promise<Institution> {
  return get<Institution>(`/institutions/${id}`);
}

export function getInstitutionStats(id: number | string): Promise<{
  works_by_year: Record<string, number>;
  top_venue_ids: Record<string, number>;
}> {
  return get(`/institutions/${id}/stats`);
}

export function getYearlyTrends(yearFrom = 2000): Promise<TrendPoint[]> {
  return get<TrendPoint[]>(`/trends/yearly?year_from=${yearFrom}`);
}
