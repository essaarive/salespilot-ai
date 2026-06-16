from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="admin", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    category = Column(String(60), index=True, nullable=False)
    content = Column(Text, nullable=False)
    keywords = Column(String(255), default="", nullable=False)
    status = Column(String(30), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(80), nullable=False)
    customer_contact = Column(String(120), default="", nullable=False)
    requirement = Column(Text, nullable=False)
    intent_level = Column(String(30), default="high", nullable=False)
    status = Column(String(50), default="new", nullable=False)
    remark = Column(Text, default="", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(120), unique=True, index=True, nullable=False)
    value = Column(Text, default="", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
