"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "institutions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("openalex_id", sa.String(64), unique=True, index=True),
        sa.Column("ror_id", sa.String(64), unique=True, index=True),
        sa.Column("name", sa.String(512), index=True, nullable=False),
        sa.Column("country_code", sa.String(2), index=True),
        sa.Column("type", sa.String(64)),
        sa.Column("works_count", sa.Integer, server_default="0"),
        sa.Column("cited_by_count", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "venues",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("openalex_id", sa.String(64), unique=True, index=True),
        sa.Column("issn_l", sa.String(16), index=True),
        sa.Column("name", sa.String(512), index=True, nullable=False),
        sa.Column("type", sa.String(64)),
        sa.Column("works_count", sa.Integer, server_default="0"),
    )

    op.create_table(
        "authors",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("openalex_id", sa.String(64), unique=True, index=True),
        sa.Column("semantic_scholar_id", sa.String(64), unique=True, index=True),
        sa.Column("orcid", sa.String(32), unique=True, index=True),
        sa.Column("display_name", sa.String(512), index=True, nullable=False),
        sa.Column("name_normalized", sa.String(512), index=True, nullable=False),
        sa.Column("works_count", sa.Integer, server_default="0"),
        sa.Column("cited_by_count", sa.Integer, server_default="0"),
        sa.Column("h_index", sa.Integer),
        sa.Column(
            "last_known_institution_id",
            sa.Integer,
            sa.ForeignKey("institutions.id", ondelete="SET NULL"),
        ),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "works",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("openalex_id", sa.String(64), unique=True, index=True),
        sa.Column("doi", sa.String(255), unique=True, index=True),
        sa.Column("semantic_scholar_id", sa.String(64), unique=True, index=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("abstract", sa.Text),
        sa.Column("publication_date", sa.Date, index=True),
        sa.Column("publication_year", sa.Integer, index=True),
        sa.Column("cited_by_count", sa.Integer, server_default="0", index=True),
        sa.Column("reference_count", sa.Integer, server_default="0"),
        sa.Column("type", sa.String(64)),
        sa.Column("language", sa.String(8)),
        sa.Column("is_open_access", sa.Boolean, server_default=sa.false()),
        sa.Column("venue_id", sa.Integer, sa.ForeignKey("venues.id", ondelete="SET NULL")),
        sa.Column("source", sa.String(32), index=True),
        sa.Column("confidence", sa.Float, server_default="1.0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("search_vector", postgresql.TSVECTOR),
    )
    op.create_index(
        "ix_works_search_vector", "works", ["search_vector"], postgresql_using="gin"
    )
    op.create_index(
        "ix_works_title_trgm",
        "works",
        ["title"],
        postgresql_using="gin",
        postgresql_ops={"title": "gin_trgm_ops"},
    )

    op.create_table(
        "work_authors",
        sa.Column("work_id", sa.Integer, sa.ForeignKey("works.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("author_id", sa.Integer, sa.ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("position", sa.Integer),
        sa.Column("author_position", sa.String(16)),
    )

    op.create_table(
        "work_institutions",
        sa.Column("work_id", sa.Integer, sa.ForeignKey("works.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("institution_id", sa.Integer, sa.ForeignKey("institutions.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "citations",
        sa.Column("citing_work_id", sa.Integer, sa.ForeignKey("works.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("cited_work_id", sa.Integer, sa.ForeignKey("works.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("ix_citations_cited", "citations", ["cited_work_id"])
    op.create_index("ix_citations_citing", "citations", ["citing_work_id"])

    op.create_table(
        "embeddings",
        sa.Column("work_id", sa.Integer, sa.ForeignKey("works.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("model", sa.String(128), nullable=False),
        sa.Column("dim", sa.Integer, nullable=False),
        sa.Column("vector", postgresql.ARRAY(sa.Float), nullable=False),
        sa.Column("norm", sa.Float, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    for table in (
        "embeddings",
        "citations",
        "work_institutions",
        "work_authors",
        "works",
        "authors",
        "venues",
        "institutions",
    ):
        op.drop_table(table)
