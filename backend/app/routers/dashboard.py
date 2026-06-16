from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.timezone import local_day_bounds_utc_naive
from app.deps import get_db, verify_token
from app.models import Conversation, KnowledgeItem, Lead
from app.schemas import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"], dependencies=[Depends(verify_token)])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    today_start, today_end = local_day_bounds_utc_naive()

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
