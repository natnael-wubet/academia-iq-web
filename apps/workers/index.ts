export interface Env {
  API_BASE: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const apiBase = env.API_BASE || "http://localhost:8000/api/v1";
    const upstream = new URL(url.pathname + url.search, apiBase);
    const resp = await fetch(upstream, {
      method: request.method,
      headers: request.headers,
      body: request.body,
    });
    return new Response(resp.body, {
      status: resp.status,
      headers: resp.headers,
    });
  },
};
