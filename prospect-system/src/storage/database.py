from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from src.storage.db_models import Base


_engine = None
_SessionLocal = None


def init_db(database_url: str) -> None:
    global _engine, _SessionLocal

    if database_url.startswith("sqlite"):
        db_path = database_url.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    _engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
        echo=False,
    )

    if "sqlite" in database_url:
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    Base.metadata.create_all(_engine)

    if "sqlite" in database_url:
        _run_sqlite_migrations(_engine)

    _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


def _run_sqlite_migrations(engine) -> None:
    """Add columns introduced after the initial schema without dropping data."""
    new_lead_columns = [
        ("whatsapp_sent_at", "DATETIME"),
        ("whatsapp_status", "TEXT"),
    ]
    with engine.connect() as conn:
        existing = {
            row[1]
            for row in conn.execute(
                __import__("sqlalchemy").text("PRAGMA table_info(leads)")
            )
        }
        for col_name, col_type in new_lead_columns:
            if col_name not in existing:
                conn.execute(
                    __import__("sqlalchemy").text(
                        f"ALTER TABLE leads ADD COLUMN {col_name} {col_type}"
                    )
                )
                conn.commit()


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager that yields a Session and closes it automatically."""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized — call init_db() first.")
    session: Session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()
