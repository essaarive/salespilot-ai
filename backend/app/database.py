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

        company_columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info(company_settings)")).fetchall()
        }
        if company_columns:
            company_migrations = {
                "company_name": "ALTER TABLE company_settings ADD COLUMN company_name VARCHAR(160) DEFAULT 'SalesPilot AI' NOT NULL",
                "company_short_name": "ALTER TABLE company_settings ADD COLUMN company_short_name VARCHAR(80) DEFAULT 'SalesPilot AI' NOT NULL",
                "company_logo_url": "ALTER TABLE company_settings ADD COLUMN company_logo_url VARCHAR(500) DEFAULT '' NOT NULL",
                "company_intro": "ALTER TABLE company_settings ADD COLUMN company_intro TEXT DEFAULT '面向中小企业的 AI 智能获客客服系统。' NOT NULL",
                "customer_service_name": "ALTER TABLE company_settings ADD COLUMN customer_service_name VARCHAR(80) DEFAULT '智销助手' NOT NULL",
                "customer_service_avatar_url": "ALTER TABLE company_settings ADD COLUMN customer_service_avatar_url VARCHAR(500) DEFAULT '' NOT NULL",
                "welcome_message": "ALTER TABLE company_settings ADD COLUMN welcome_message TEXT DEFAULT '您好，我是 SalesPilot AI 智销助手，可以为您介绍 AI 客服方案、知识库能力、价格、交付周期和接入方式。' NOT NULL",
                "brand_color": "ALTER TABLE company_settings ADD COLUMN brand_color VARCHAR(20) DEFAULT '#2563EB' NOT NULL",
                "business_scope": "ALTER TABLE company_settings ADD COLUMN business_scope TEXT DEFAULT 'AI 客服、知识库问答、销售线索沉淀、多模型接入、企业官网咨询。' NOT NULL",
                "human_contact_phone": "ALTER TABLE company_settings ADD COLUMN human_contact_phone VARCHAR(80) DEFAULT '' NOT NULL",
                "human_contact_wechat": "ALTER TABLE company_settings ADD COLUMN human_contact_wechat VARCHAR(120) DEFAULT '' NOT NULL",
                "human_contact_email": "ALTER TABLE company_settings ADD COLUMN human_contact_email VARCHAR(160) DEFAULT '' NOT NULL",
                "business_hours": "ALTER TABLE company_settings ADD COLUMN business_hours VARCHAR(160) DEFAULT '周一至周五 09:00-18:00' NOT NULL",
                "handoff_message": "ALTER TABLE company_settings ADD COLUMN handoff_message TEXT DEFAULT '您的问题已记录，我们建议由工作人员进一步确认并跟进。' NOT NULL",
                "forbidden_topics": "ALTER TABLE company_settings ADD COLUMN forbidden_topics TEXT DEFAULT '' NOT NULL",
                "allowed_embed_domains": "ALTER TABLE company_settings ADD COLUMN allowed_embed_domains TEXT DEFAULT '' NOT NULL",
                "widget_position": "ALTER TABLE company_settings ADD COLUMN widget_position VARCHAR(20) DEFAULT 'right' NOT NULL",
                "created_at": "ALTER TABLE company_settings ADD COLUMN created_at DATETIME",
                "updated_at": "ALTER TABLE company_settings ADD COLUMN updated_at DATETIME",
            }
            for column_name, statement in company_migrations.items():
                if column_name not in company_columns:
                    connection.execute(text(statement))
