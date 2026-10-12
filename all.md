# ACADEMIA IQ — Complete Build & Launch Plan

## Zero-Cost Implementation Blueprint for the Research Intelligence Platform

---

## 📌 Executive Summary

Academia IQ is a research intelligence platform built on four free APIs — **OpenAlex** (250M+ papers), **Semantic Scholar** (200M+ papers + AI), **Crossref** (140M+ DOIs), and **ORCID** (18M researcher profiles). The entire system — backend, database, search, vector store, AI, hosting, and CI/CD — can be built and hosted for **$0/month** using generous free tiers available in 2026. This document is the complete, actionable blueprint: every phase, every tool, every integration, every line of the business model.

---

# 📅 PHASE PLAN: From Zero to Revenue

## Phase 1: Foundation & MVP (Weeks 1–4)

**Objective:** Build a working research paper search + researcher profile system. Launch a public beta with zero users acquired — get the infrastructure right first.

### Week 1–2: Data Layer & API Integration

**Deliverables:**

| Task | Details | Free Tool |
|------|---------|-----------|
| Set up PostgreSQL | 1 GB storage, 1 CPU, 1 GB RAM | Aiven free tier (no credit card, indefinite) |
| Set up Redis cache | 30 MB, 100 ops/sec | Redis Cloud free tier |
| Set up vector database | 100K objects, free forever | Weaviate Cloud free tier |
| Write OpenAlex ingester | Fetch works, authors, institutions. Use `mailto` param for polite pool. Keyless: 1,000 credits/day | Python + httpx |
| Write Semantic Scholar ingester | 100 req/5min without key; 1,000 req/5min with free key. Get key at semanticscholar.org/product/api | Python + requests |
| Write Crossref ingester | 10 req/sec polite pool with `mailto` param. Higher concurrency (3 concurrent) | Python + requests |
| Write ORCID ingester | Public API, no key needed. Search by name, fetch employments, education, works | Python + requests |
| Entity resolution | Match authors across OpenAlex ↔ Semantic Scholar ↔ ORCID by ORCID iD, name + affiliation, DOI overlap | Python + rapidfuzz |
| Data schema | `works`, `authors`, `institutions`, `venues`, `citations`, `embeddings` tables | SQLAlchemy + Alembic |

**Data Volume Target for MVP:**

- 500,000 works (papers) with full metadata
- 200,000 author profiles
- 50,000 institution records
- 2M citation edges
- 500,000 embeddings (768-dim, SPECTER2 or all-MiniLM-L6-v2)

**Why these APIs and not just one?**

OpenAlex gives the broadest coverage (250M works) but lacks AI recommendations. Semantic Scholar has the best AI/embeddings (SPECTER2) but lower rate limits. Crossref is the authoritative DOI registry — best for citation metadata. ORCID is the only source for verified researcher identity (employment history, education, funding). Together they form a complete picture that no single API provides. Entity resolution across them is the hard part — and your moat.

### Week 3: Search & Intelligence Layer

| Component | Implementation | Free Tool |
|-----------|---------------|-----------|
| Full-text search | Index titles, abstracts, author names, venue names | PostgreSQL `tsvector` + GIN index (built-in, free) |
| Vector search | Semantic similarity on paper abstracts + titles | Weaviate Cloud (100K objects free) OR pgvector on Aiven Postgres |
| Hybrid search | Combine BM25 (keyword) + cosine similarity (semantic) with reciprocal rank fusion | Custom Python (30 lines) |
| LLM summaries | Generate paper summaries, field overviews | Groq free tier (30 RPM, 14,400 req/day, very fast inference) |
| Embedding pipeline | Batch embed abstracts using all-MiniLM-L6-v2 (384-dim) or SPECTER2 | sentence-transformers (local, free) OR HuggingFace Inference API |
| Citation graph | Build DAG of citations, compute PageRank, detect communities | NetworkX (local, free) |

**Tech Stack for Search:**

```
┌─────────────────────────────────────────────────────────────┐
│                    SEARCH ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Query                                                  │
│      │                                                       │
│      ▼                                                       │
│  ┌──────────────┐    ┌──────────────┐                       │
│  │  BM25 Search  │    │ Vector Search │                       │
│  │ (PostgreSQL)  │    │  (Weaviate)   │                       │
│  └──────┬───────┘    └──────┬───────┘                       │
│         │                   │                                │
│         └────────┬──────────┘                                │
│                  ▼                                           │
│         ┌───────────────┐                                    │
│         │ Reciprocal Rank│                                   │
│         │    Fusion      │                                   │
│         └───────┬───────┘                                    │
│                 ▼                                            │
│         ┌───────────────┐                                    │
│         │  LLM Rerank   │  ← Groq (free)                     │
│         └───────┬───────┘                                    │
│                 ▼                                            │
│         ┌───────────────┐                                    │
│         │  Final Results │                                   │
│         └───────────────┘                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Week 4: API Layer & Dashboard

| Component | Implementation | Free Tool |
|-----------|---------------|-----------|
| API framework | REST endpoints for search, authors, institutions, trends | FastAPI (Python) |
| Edge API gateway | Rate limiting, caching, auth, geo-routing | Cloudflare Workers (100K req/day free) |
| Auth | Email/password + magic links + Google OAuth | Supabase Auth (free tier, 50K MAU) |
| Frontend | Search UI, author profiles, citation graphs, trend dashboards | Next.js + Tailwind + Recharts |
| Hosting (frontend) | Static + SSR | Vercel Hobby (free) |
| Hosting (API) | Serverless functions | Cloudflare Workers (free) |
| CI/CD | Auto-deploy on push, run tests, lint, type-check | GitHub Actions (unlimited on public repos) |

**Phase 1 Total Cost: $0/month**

| Service | Free Tier Limit | Enough for MVP? |
|---------|----------------|----------------|
| Aiven PostgreSQL | 1 GB storage, 1 CPU, 1 GB RAM | ✅ Yes (500K papers fits in ~400MB) |
| Redis Cloud | 30 MB, 100 ops/sec | ✅ Yes (cache + rate limit state) |
| Weaviate Cloud | 100K objects, free forever | ✅ Yes (500K embeddings with 384-dim = ~75MB) |
| Cloudflare Workers | 100K req/day, 10ms CPU/req | ✅ Yes (API gateway) |
| Vercel Hobby | 1M edge requests + 1M function invocations/mo | ✅ Yes (frontend) |
| GitHub Actions | Unlimited (public repo) | ✅ Yes |
| Groq | 30 RPM, 14,400 req/day | ✅ Yes (summaries) |
| Supabase Auth | 50K MAU | ✅ Yes |

---

## Phase 2: Growth & Intelligence (Months 2–3)

**Objective:** Add the six modules from the venture plan. Launch publicly. Acquire first 1,000 users.

### Month 2: Core Module Development

| Module | Features | Free Tooling |
|--------|----------|-------------|
| **Research Landscape Mapper** | Interactive field graphs, emerging topic detection, citation flow visualization | D3.js + Recharts (free), NetworkX community detection (Louvain) |
| **Collaboration Matchmaker** | Researcher matching by complementary expertise, co-author suggestions | Weaviate similarity search + custom scoring |
| **Grant Intelligence** | Funding pattern tracking, success probability prediction, competitive analysis | OpenAlex funding data + logistic regression (scikit-learn) |
| **Institutional Benchmarking** | University output comparison, rising star detection, recruitment intelligence | PostgreSQL window functions + materialized views |
| **Literature Review Automation** | One-click systematic reviews, AI summaries, gap analysis | Groq + custom RAG pipeline over Weaviate |
| **API Access Layer** | White-label API for edtech, rate limiting, billing hooks | Cloudflare Workers + Stripe (free until revenue) |

### Month 3: Launch & Distribution

| Channel | Strategy | Cost |
|---------|----------|------|
| Academic Twitter/X | Thread on "how we built a free Scopus alternative" | $0 |
| Reddit (r/academia, r/AskAcademia, r/LadiesofScience) | Authentic posts about solving real problems | $0 |
| Product Hunt | Launch with "Free research intelligence for every researcher" | $0 |
| University department outreach | Cold email to department heads with free pilot offer | $0 |
| SEO | Target "free Scopus alternative," "OpenAlex tutorial," "research paper finder" | $0 |
| Integration | Embed in Overleaf, Zotero, Mendeley workflows | $0 (partnerships) |

**Key Metric Targets (End of Month 3):**

- 1,000 registered users
- 200 daily active users
- 50,000 API calls/day
- 10,000 papers summarized
- 500 literature reviews generated

---

## Phase 3: Scale & Monetization (Months 4–6)

**Objective:** Launch paid tiers. Reach $10K MRR. Build the enterprise pipeline.

### Month 4: Paid Tier Launch

| Tier | Price | Features | Target Segment |
|------|-------|----------|---------------|
| **Free** | $0 | Search, 10 summaries/day, basic profiles | Students, casual researchers |
| **Researcher** | $49/mo | Unlimited summaries, literature reviews, collaboration matching | PhD students, postdocs |
| **Department** | $199/mo | 10 seats, benchmarking, grant intelligence, API access | University departments |
| **Institution** | $999/mo | Unlimited seats, white-label, SSO, dedicated support | Universities, think tanks |

**Payment Infrastructure (Free to Start):**

- **Stripe** — no monthly fee, 2.9% + $0.30 per transaction. Free until you have revenue.
- **LemonSqueezy** — merchant of record, handles VAT/tax globally. 5% + $0.50 per transaction.
- **Paddle** — similar to LemonSqueezy, 5% + $0.50.

### Month 5: Enterprise Pipeline

| Activity | Details | Cost |
|----------|---------|------|
| Build case studies | Document 5 university pilots with metrics (time saved, papers found) | $0 |
| Create sales deck | ROI calculator, feature comparison vs. Scopus/Web of Science | $0 |
| LinkedIn outreach | Target VPs of Research, Library Directors, Provosts | $0 |
| Conference presence | Virtual booths at academic conferences (ACL, NeurIPS, AERA) | $0–500 |
| Webinar series | "The Future of Research Intelligence" — invite librarians | $0 |

### Month 6: Revenue Optimization

| Lever | Action | Expected Impact |
|-------|--------|----------------|
| Annual pricing | 2 months free on annual plans | +30% LTV |
| Usage-based API | $0.01/call for white-label partners | New revenue stream |
| Data products | Custom trend reports ($500–2,000 each) | High-margin one-time revenue |
| Referral program | 1 month free for each referred institution | Viral growth |

**Revenue Projections (End of Month 6):**

| Stream | Customers | Price | MRR |
|--------|-----------|-------|-----|
| Researcher tier | 150 | $49/mo | $7,350 |
| Department tier | 15 | $199/mo | $2,985 |
| Institution tier | 2 | $999/mo | $1,998 |
| API/Data products | — | — | $1,000 |
| **TOTAL** | | | **$13,333** |

---

## Phase 4: Scale to $100K MRR (Months 7–18)

**Objective:** Product-led growth, international expansion, acquisition target.

| Quarter | Focus | Target MRR |
|---------|-------|-----------|
| Q3 2026 | Self-serve onboarding, content marketing, SEO domination | $25K |
| Q4 2026 | Enterprise sales team (commission-only), EU expansion | $50K |
| Q1 2027 | API marketplace, integrations (Zotero, Overleaf, Mendeley) | $75K |
| Q2 2027 | Acquisition conversations with Clarivate, Elsevier, Digital Science | $100K+ |

---

# 🛠️ COMPLETE TECH STACK (100% Free to Start)

## Infrastructure Layer

| Layer | Technology | Free Tier | Why This Choice |
|-------|-----------|-----------|-----------------|
| **Compute (API)** | Cloudflare Workers | 100K req/day, 10ms CPU/req | Edge-deployed, zero cold start, global |
| **Compute (Heavy)** | GitHub Actions (self-hosted runner) | Unlimited (public repo) | Batch processing, data ingestion |
| **Database (Primary)** | Aiven PostgreSQL | 1 GB storage, 1 CPU, 1 GB RAM | Managed, backups, no credit card |
| **Database (Cache)** | Redis Cloud | 30 MB, 100 ops/sec | Session cache, rate limiting, job queue |
| **Vector Store** | Weaviate Cloud | 100K objects, free forever | Purpose-built vector search, hybrid support |
| **Full-Text Search** | PostgreSQL tsvector | Built into Aiven | No extra service needed for MVP |
| **Object Storage** | Cloudflare R2 | 10 GB storage, 10M reads/mo | Paper PDFs, generated reports |
| **CDN** | Cloudflare | Unlimited bandwidth | Static assets, edge caching |

## Application Layer

| Component | Technology | Free Tier |
|-----------|-----------|-----------|
| **Backend Framework** | FastAPI (Python 3.12) | Free, open source |
| **ORM** | SQLAlchemy + Alembic | Free, open source |
| **Task Queue** | Celery + Redis (Upstash) | Redis Cloud free tier |
| **API Gateway** | Cloudflare Workers | 100K req/day |
| **Auth** | Supabase Auth | 50K MAU free |
| **AI/LLM** | Groq (Llama 3, Mixtral) | 30 RPM, 14,400 req/day |
| **Embeddings** | sentence-transformers (local) | Free, runs on your machine |
| **ML** | scikit-learn, NetworkX | Free, open source |
| **Frontend** | Next.js 14 + Tailwind + Recharts | Free, open source |
| **UI Components** | shadcn/ui + Radix | Free, open source |
| **Charts** | Recharts + D3.js | Free, open source |

## AI/ML Stack (Free Alternatives)

| Need | Paid Option | Free Alternative | Quality Trade-off |
|------|-------------|-----------------|-------------------|
| **LLM Summaries** | GPT-4o | Groq (Llama 3 70B) | 90% quality, 10x faster, free |
| **Embeddings** | OpenAI text-embedding-3 | all-MiniLM-L6-v2 (local) | 85% quality, zero cost |
| **Paper Recommendations** | Semantic Scholar API | SPECTER2 embeddings + cosine similarity | 95% quality (same model) |
| **NER/Entity Extraction** | GPT-4 | spaCy + custom rules | 80% quality, fully free |
| **Citation Prediction** | Custom transformer | Gradient boosting (XGBoost) | 70% quality, free |

## DevOps & Monitoring

| Tool | Purpose | Free Tier |
|------|---------|-----------|
| **GitHub Actions** | CI/CD, tests, deployment | Unlimited (public repo) |
| **Sentry** | Error tracking | 5K errors/mo free |
| **UptimeRobot** | Uptime monitoring | 50 monitors, 5-min intervals |
| **Grafana Cloud** | Metrics, logs, dashboards | 10K series, 50GB logs free |
| **PostHog** | Product analytics | 1M events/mo free |

---

# 💰 BUSINESS MODEL (Zero-Cost Until Revenue)

## Revenue Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    REVENUE STREAMS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐                                        │
│  │  SaaS Subscriptions  │  70% of revenue                        │
│  │                     │                                        │
│  │  Researcher $49/mo  │  ← PhD students, postdocs              │
│  │  Department $199/mo │  ← University departments              │
│  │  Institution $999/mo│  ← Universities, think tanks           │
│  └─────────────────────┘                                        │
│                                                                  │
│  ┌─────────────────────┐                                        │
│  │  API Licensing       │  20% of revenue                        │
│  │                     │                                        │
│  │  $0.01/call         │  ← EdTech companies                    │
│  │  Volume discounts   │  ← Publishers, analytics platforms     │
│  └─────────────────────┘                                        │
│                                                                  │
│  ┌─────────────────────┐                                        │
│  │  Data Products       │  10% of revenue                        │
│  │                     │                                        │
│  │  Trend reports      │  ← Custom reports ($500–2,000)         │
│  │  Benchmark data     │  ← Annual subscriptions                │
│  └─────────────────────┘                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Unit Economics (Year 1)

| Metric | Value | Notes |
|--------|-------|-------|
| **CAC (Researcher)** | $15 | Content marketing, SEO |
| **CAC (Department)** | $200 | Cold email + demo |
| **CAC (Institution)** | $2,000 | Sales team + pilots |
| **LTV (Researcher)** | $588 | 12-month avg, $49/mo |
| **LTV (Department)** | $2,388 | 12-month avg, $199/mo |
| **LTV (Institution)** | $11,988 | 12-month avg, $999/mo |
| **LTV:CAC Ratio** | 39:1 / 12:1 / 6:1 | Healthy across all tiers |
| **Gross Margin** | 95%+ | Almost no COGS (free APIs) |
| **Payback Period** | <1 month | For Researcher tier |

## Pricing Psychology

- **Anchoring**: Display Institution tier ($999/mo) first. Researcher tier ($49/mo) looks cheap by comparison.
- **Decoy effect**: Department tier ($199/mo) exists mainly to make Institution tier feel like a bargain.
- **Free tier**: Not a limitation — a lead generation machine. 5% conversion to paid is industry standard.
- **Annual discount**: 2 months free pushes cash flow forward and reduces churn.

---

# 🔒 RISK MITIGATION

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **API rate limits** | High | Medium | Aggressive caching (Redis), batch processing, multiple API keys, fallback chain (OpenAlex → Semantic Scholar → Crossref) |
| **API changes/deprecation** | Medium | High | Abstract data layer, adapter pattern, monitor API changelogs, maintain local backups |
| **Data quality issues** | Medium | Medium | Entity resolution pipeline, confidence scoring, user feedback loop |
| **Competitor launches** | Medium | High | Move fast, build community, focus on UX (existing tools are ugly) |
| **Free tier limits exceeded** | Medium | Medium | Monitor usage, implement graceful degradation, have upgrade path ready |
| **Legal/trademark issues** | Low | High | Use "Academia IQ" (not "OpenAlex IQ"), attribute all data sources, respect licenses |
| **GDPR/privacy** | Medium | High | No personal data storage without consent, anonymize analytics, EU data residency option |
| **Key person risk** | Medium | High | Document everything, use standard technologies, build automation |

---

# 📊 SUCCESS METRICS & MILESTONES

| Milestone | Timeline | KPI |
|-----------|----------|-----|
| MVP live | Week 4 | 500K papers searchable |
| First 100 users | Month 2 | 100 registered users |
| First paying customer | Month 4 | $49 MRR |
| 1,000 users | Month 3 | 1,000 registered |
| $10K MRR | Month 6 | 200 paying customers |
| $50K MRR | Month 12 | 1,000 paying customers |
| $100K MRR | Month 18 | 2,000 paying customers |
| Acquisition conversation | Month 24 | Term sheet from Clarivate/Elsevier |

---

# 🚀 GETTING STARTED TODAY

## Your First 7 Days

| Day | Action | Tool |
|-----|--------|------|
| **Day 1** | Create accounts: Aiven, Redis Cloud, Weaviate Cloud, Cloudflare, GitHub, Vercel, Groq, Supabase | All free |
| **Day 2** | Set up PostgreSQL schema, connect FastAPI, test OpenAlex ingestion | Aiven + Python |
| **Day 3** | Ingest 10,000 papers from OpenAlex, 10,000 from Semantic Scholar, test entity resolution | Python scripts |
| **Day 4** | Set up Weaviate, embed 10,000 abstracts, test vector search | Weaviate + sentence-transformers |
| **Day 5** | Build search API endpoint (BM25 + vector + RRF), deploy to Cloudflare Workers | FastAPI + Workers |
| **Day 6** | Build minimal frontend (search bar, results list, paper detail view), deploy to Vercel | Next.js + Tailwind |
| **Day 7** | Connect Groq for summaries, test end-to-end flow, invite 5 friends to beta | Groq + Cloudflare |

**Total cost for Week 1: $0.**

---

# 📁 PROJECT STRUCTURE

```
academia-iq/
├── .github/
│   └── workflows/
│       ├── ci.yml              # Test, lint, type-check
│       └── deploy.yml          # Deploy to Cloudflare + Vercel
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── search.py
│   │   │   ├── authors.py
│   │   │   ├── institutions.py
│   │   │   └── trends.py
│   │   ├── services/
│   │   │   ├── openalex.py
│   │   │   ├── semantic_scholar.py
│   │   │   ├── crossref.py
│   │   │   └── orcid.py
│   │   ├── models/
│   │   ├── schemas/
│   │   └── core/
│   │       ├── config.py
│   │       ├── cache.py
│   │       └── db.py
│   ├── web/                    # Next.js frontend
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   └── workers/                # Cloudflare Workers (API gateway)
│       └── index.ts
├── packages/
│   ├── ingestion/              # Data ingestion pipelines
│   │   ├── openalex_ingest.py
│   │   ├── semscholar_ingest.py
│   │   ├── crossref_ingest.py
│   │   └── orcid_ingest.py
│   ├── embeddings/             # Embedding generation
│   │   └── embed.py
│   └── ml/                     # ML models
│       ├── recommend.py
│       └── predict.py
├── docker-compose.yml          # Local development
├── requirements.txt
└── README.md
```

---

# 🎯 THE MOAT (Why This Wins)

1. **Entity resolution complexity** — Matching authors across OpenAlex, Semantic Scholar, and ORCID by name + affiliation + DOI overlap is genuinely hard. Most competitors don't do it well.

2. **Network effects** — More users = more collaboration recommendations = more value. The first mover in this space wins.

3. **Switching costs** — Once a university embeds Academia IQ into its research workflow, migration is painful. Data exports, saved searches, team configurations all create lock-in.

4. **Proprietary algorithms** — Citation prediction, collaboration matching, and trend detection models improve with data. Your moat deepens over time.

5. **Free tier foundation** — Zero COGS means you can undercut Scopus ($50K–500K/year) by 10–100x while maintaining 90%+ gross margins.

6. **Community** — Research communities are tight-knit. A beloved tool spreads virally through department Slack channels, Twitter, and conference hallways.

---

This is the complete blueprint. Every tool is free. Every API has a documented free tier. Every phase is actionable. The only thing standing between you and $100K MRR is execution — and that's entirely in your hands.