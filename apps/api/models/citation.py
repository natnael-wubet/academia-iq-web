from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.core.db import Base


class Citation(Base):
    """A directed edge: citing_work -> cited_work."""

    __tablename__ = "citations"

    citing_work_id: Mapped[int] = mapped_column(
        ForeignKey("works.id", ondelete="CASCADE"), primary_key=True
    )
    cited_work_id: Mapped[int] = mapped_column(
        ForeignKey("works.id", ondelete="CASCADE"), primary_key=True
    )

    __table_args__ = (
        Index("ix_citations_cited", "cited_work_id"),
        Index("ix_citations_citing", "citing_work_id"),
    )
