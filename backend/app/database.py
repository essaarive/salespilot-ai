import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./salespilot.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    ensure_schema_compatibility()


def ensure_schema_compatibility() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        return

    with engine.begin() as connection:
        knowledge_columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info(knowledge_items)")).fetchall()
        }
        knowledge_migrations = {
            "source_type": "ALTER TABLE knowledge_items ADD COLUMN source_type VARCHAR(30) DEFAULT 'manual' NOT NULL",
            "source_document_id": "ALTER TABLE knowledge_items ADD COLUMN source_document_id INTEGER",
            "source_file_name": "ALTER TABLE knowledge_items ADD COLUMN source_file_name VARCHAR(255)",
            "chunk_index": "ALTER TABLE knowledge_items ADD COLUMN chunk_index INTEGER",
        }
        for column_name, statement in knowledge_migrations.items():
            if column_name not in knowledge_columns:
                connection.execute(text(statement))

        document_columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info(documents)")).fetchall()
        }
        document_migrations = {
            "is_enabled": "ALTER TABLE documents ADD COLUMN is_enabled BOOLEAN DEFAULT 1 NOT NULL",
        }
        for column_name, statement in document_migrations.items():
            if column_name not in document_columns:
                connection.execute(text(statement))

        lead_columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info(leads)")).fetchall()
        }
        lead_migrations = {
            "requires_handoff": "ALTER TABLE leads ADD COLUMN requires_handoff BOOLEAN DEFAULT 0 NOT NULL",
            "handoff_reason": "ALTER TABLE leads ADD COLUMN handoff_reason VARCHAR(80)",
        }
        for column_name, statement in lead_migrations.items():
            if column_name not in lead_columns:
                connection.execute(text(statement))
