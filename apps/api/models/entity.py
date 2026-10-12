from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.core.db import Base


class Institution(Base):
    __tablename__ = "institutions"

    id: Mapped[int] = mapped_column(primary_key=True)
    openalex_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    ror_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(512), index=True)
    country_code: Mapped[str | None] = mapped_column(String(2), index=True)
    type: Mapped[str | None] = mapped_column(String(64))
    works_count: Mapped[int] = mapped_column(Integer, default=0)
    cited_by_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    authors: Mapped[list["Author"]] = relationship(back_populates="institution")


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    openalex_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    semantic_scholar_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    orcid: Mapped[str | None] = mapped_column(String(32), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(512), index=True)
    name_normalized: Mapped[str] = mapped_column(String(512), index=True)
    works_count: Mapped[int] = mapped_column(Integer, default=0)
    cited_by_count: Mapped[int] = mapped_column(Integer, default=0)
    h_index: Mapped[int | None] = mapped_column(Integer)
    last_known_institution_id: Mapped[int | None] = mapped_column(
        ForeignKey("institutions.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    institution: Mapped[Institution | None] = relationship(back_populates="authors")
    works: Mapped[list["Work"]] = relationship(
        secondary="work_authors", back_populates="authors"
    )


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True)
    openalex_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    issn_l: Mapped[str | None] = mapped_column(String(16), index=True)
    name: Mapped[str] = mapped_column(String(512), index=True)
    type: Mapped[str | None] = mapped_column(String(64))
    works_count: Mapped[int] = mapped_column(Integer, default=0)


class Work(Base):
    __tablename__ = "works"

    id: Mapped[int] = mapped_column(primary_key=True)
    openalex_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    doi: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    semantic_scholar_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(Text)
    abstract: Mapped[str | None] = mapped_column(Text)
    publication_date: Mapped[date | None] = mapped_column(Date, index=True)
    publication_year: Mapped[int | None] = mapped_column(Integer, index=True)
    cited_by_count: Mapped[int] = mapped_column(Integer, default=0, index=True)
    reference_count: Mapped[int] = mapped_column(Integer, default=0)
    type: Mapped[str | None] = mapped_column(String(64))
    language: Mapped[str | None] = mapped_column(String(8))
    is_open_access: Mapped[bool] = mapped_column(default=False)
    venue_id: Mapped[int | None] = mapped_column(ForeignKey("venues.id", ondelete="SET NULL"))
    source: Mapped[str | None] = mapped_column(String(32), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    venue: Mapped[Venue | None] = relationship()
    authors: Mapped[list[Author]] = relationship(
        secondary="work_authors", back_populates="works"
    )
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)

    __table_args__ = (
        Index("ix_works_search_vector", "search_vector", postgresql_using="gin"),
        Index("ix_works_title_trgm", "title", postgresql_using="gin",
              postgresql_ops={"title": "gin_trgm_ops"}),
    )
