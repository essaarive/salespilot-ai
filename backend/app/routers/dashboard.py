import os
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db, verify_token
from app.models import Conversation, KnowledgeItem, Lead
from app.schemas import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"], dependencies=[Depends(verify_token)])


def get_app_timezone() -> ZoneInfo:
    timezone_name = os.getenv("APP_TIMEZONE") or "Asia/Shanghai"
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return ZoneInfo("Asia/Shanghai")


@router.get("/summary", response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    local_tz = get_app_timezone()
    today = datetime.now(local_tz).date()
    today_start = datetime.combine(today, time.min, local_tz).astimezone(timezone.utc).replace(tzinfo=None)
    today_end = datetime.combine(today, time.max, local_tz).astimezone(timezone.utc).replace(tzinfo=None)

    recent_conversations = (
        db.query(Conversation).order_by(Conversation.created_at.desc()).limit(5).all()
    )

    return DashboardSummary(
        knowledge_count=db.query(KnowledgeItem).count(),
        today_conversations=db.query(Conversation)
        .filter(Conversation.created_at >= today_start, Conversation.created_at <= today_end)
        .count(),
        high_intent_leads=db.query(Lead).filter(Lead.intent_level == "high").count(),
        total_leads=db.query(Lead).count(),
        recent_conversations=recent_conversations,
    )
