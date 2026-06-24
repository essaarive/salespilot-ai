from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.core.timezone import now_utc_naive
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="admin", nullable=False)
    created_at = Column(DateTime, default=now_utc_naive, nullable=False)


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    category = Column(String(60), index=True, nullable=False)
    content = Column(Text, nullable=False)
    keywords = Column(String(255), default="", nullable=False)
    status = Column(String(30), default="active", nullable=False)
    source_type = Column(String(30), default="manual", nullable=False)
    source_document_id = Column(Integer, nullable=True)
    source_file_name = Column(String(255), nullable=True)
    chunk_index = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=now_utc_naive, nullable=False)
    updated_at = Column(DateTime, default=now_utc_naive, onupdate=now_utc_naive, nullable=False)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_extension = Column(String(20), index=True, nullable=False)
    mime_type = Column(String(120), default="", nullable=False)
    file_size = Column(Integer, default=0, nullable=False)
    storage_path = Column(String(500), default="", nullable=False)
    parse_status = Column(String(30), default="pending", index=True, nullable=False)
    parse_error = Column(Text, default="", nullable=False)
    extracted_text_length = Column(Integer, default=0, nullable=False)
    chunk_count = Column(Integer, default=0, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=now_utc_naive, nullable=False)
    updated_at = Column(DateTime, default=now_utc_naive, onupdate=now_utc_naive, nullable=False)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(80), nullable=False)
    customer_contact = Column(String(120), default="", nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    intent_type = Column(String(50), index=True, nullable=False)
    intent_level = Column(String(30), index=True, nullable=False)
    source = Column(String(50), default="web", nullable=False)
    created_at = Column(DateTime, default=now_utc_naive, nullable=False)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(80), nullable=False)
    customer_contact = Column(String(120), default="", nullable=False)
    requirement = Column(Text, nullable=False)
    intent_level = Column(String(30), default="high", nullable=False)
    status = Column(String(50), default="new", nullable=False)
    remark = Column(Text, default="", nullable=False)
    requires_handoff = Column(Boolean, default=False, nullable=False)
    handoff_reason = Column(String(80), nullable=True)
    created_at = Column(DateTime, default=now_utc_naive, nullable=False)
    updated_at = Column(DateTime, default=now_utc_naive, onupdate=now_utc_naive, nullable=False)


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(120), unique=True, index=True, nullable=False)
    value = Column(Text, default="", nullable=False)
    created_at = Column(DateTime, default=now_utc_naive, nullable=False)
    updated_at = Column(DateTime, default=now_utc_naive, onupdate=now_utc_naive, nullable=False)


class AIModelConfig(Base):
    __tablename__ = "ai_model_configs"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(40), index=True, nullable=False)
    name = Column(String(120), nullable=False)
    api_key = Column(Text, default="", nullable=False)
    base_url = Column(String(255), nullable=False)
    model = Column(String(120), nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, index=True, nullable=False)
    created_at = Column(DateTime, default=now_utc_naive, nullable=False)
    updated_at = Column(DateTime, default=now_utc_naive, onupdate=now_utc_naive, nullable=False)


class CompanySettings(Base):
    __tablename__ = "company_settings"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(160), nullable=False)
    company_short_name = Column(String(80), default="", nullable=False)
    company_logo_url = Column(String(500), default="", nullable=False)
    company_intro = Column(Text, default="", nullable=False)
    customer_service_name = Column(String(80), nullable=False)
    customer_service_avatar_url = Column(String(500), default="", nullable=False)
    welcome_message = Column(Text, default="", nullable=False)
    brand_color = Column(String(20), default="#2563EB", nullable=False)
    business_scope = Column(Text, default="", nullable=False)
    human_contact_phone = Column(String(80), default="", nullable=False)
    human_contact_wechat = Column(String(120), default="", nullable=False)
    human_contact_email = Column(String(160), default="", nullable=False)
    business_hours = Column(String(160), default="", nullable=False)
    handoff_message = Column(Text, default="", nullable=False)
    forbidden_topics = Column(Text, default="", nullable=False)
    created_at = Column(DateTime, default=now_utc_naive, nullable=False)
    updated_at = Column(DateTime, default=now_utc_naive, onupdate=now_utc_naive, nullable=False)
