from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.api.core.db import get_db
from apps.api.models import Citation, Work
from apps.api.schemas.entities import CitationGraphOut, TrendPoint

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/yearly", response_model=list[TrendPoint])
def yearly_trends(
    q: str | None = None,
    year_from: int = 2000,
    db: Session = Depends(get_db),
) -> list[TrendPoint]:
    stmt = (
        select(
            Work.publication_year,
            func.count(Work.id),
            func.coalesce(func.sum(Work.cited_by_count), 0),
        )
        .where(Work.publication_year >= year_from)
        .group_by(Work.publication_year)
        .order_by(Work.publication_year)
    )
    if q:
        from sqlalchemy import text

        stmt = stmt.where(
            Work.search_vector.op("@@")(
                func.websearch_to_tsquery("english", q)
            )
        )
        _ = text  # keep import explicit for clarity
    rows = db.execute(stmt).all()
    return [
        TrendPoint(year=year, works=works, citations=int(citations))
        for year, works, citations in rows
        if year is not None
    ]


@router.get("/citation-graph/{work_id}", response_model=CitationGraphOut)
def citation_graph(work_id: int, depth: int = 1, db: Session = Depends(get_db)) -> CitationGraphOut:
    if db.get(Work, work_id) is None:
        raise HTTPException(status_code=404, detail="Work not found")

    import networkx as nx

    frontier = {work_id}
    visited = {work_id}
    for _ in range(depth):
        next_frontier: set[int] = set()
        edges = db.execute(
            select(Citation.citing_work_id, Citation.cited_work_id).where(
                (Citation.citing_work_id.in_(frontier))
                | (Citation.cited_work_id.in_(frontier))
            )
        ).all()
        for citing, cited in edges:
            next_frontier.update({citing, cited})
        frontier = next_frontier - visited
        visited |= next_frontier

    edge_rows = db.execute(
        select(Citation.citing_work_id, Citation.cited_work_id).where(
            Citation.citing_work_id.in_(visited), Citation.cited_work_id.in_(visited)
        )
    ).all()

    graph = nx.DiGraph()
    graph.add_nodes_from(visited)
    graph.add_edges_from(edge_rows)

    pagerank = nx.pagerank(graph) if graph.number_of_nodes() else {}
    communities: dict[int, int] = {}
    if graph.number_of_nodes():
        try:
            undirected = graph.to_undirected()
            groups = nx.community.louvain_communities(undirected, seed=42)
            for cid, group in enumerate(groups):
                for node in group:
                    communities[node] = cid
        except Exception:
            communities = {node: 0 for node in graph.nodes}

    works = {
        w.id: w
        for w in db.execute(select(Work).where(Work.id.in_(visited))).scalars()
    }
    nodes = [
        {
            "id": nid,
            "title": works[nid].title if nid in works else str(nid),
            "cited_by_count": works[nid].cited_by_count if nid in works else 0,
            "year": works[nid].publication_year if nid in works else None,
        }
        for nid in graph.nodes
    ]
    edges = [{"source": s, "target": t} for s, t in graph.edges]
    return CitationGraphOut(
        nodes=nodes,
        edges=edges,
        pagerank={int(k): float(v) for k, v in pagerank.items()},
        communities={int(k): int(v) for k, v in communities.items()},
    )
