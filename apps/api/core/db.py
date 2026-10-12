from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from apps.api.core.config import get_settings

settings = get_settings()

kwargs = {
    "pool_pre_ping": True,
    "future": True,
}
if settings.database_url.startswith("sqlite"):
    kwargs["connect_args"] = {"check_same_thread": False}
else:
    kwargs["pool_size"] = 5
    kwargs["max_overflow"] = 5
engine = create_engine(settings.database_url, **kwargs)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
