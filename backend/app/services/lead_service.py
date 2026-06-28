import re
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.timezone import now_utc_naive
from app.models import Lead

LEAD_DEDUP_WINDOW_HOURS = 24
MAX_REMARK_LENGTH = 2000
MAX_QUESTION_NOTE_LENGTH = 500

HANDOFF_REASON_PRIORITY = {
    None: 0,
    "knowledge_not_found": 1,
    "customer_requested_human": 2,
    "custom_requirement": 3,
    "special_quote": 4,
    "complaint_or_risk": 5,
}

GENERIC_CONTACT_VALUES = {
    "电话",
    "手机",
    "微信",
    "企微",
    "邮箱",
    "phone",
    "wechat",
    "email",
}


def normalize_contact_keys(value: str) -> set[str]:
    text = value.strip().lower()
    if not text:
        return set()

    keys: set[str] = set()
    compact = re.sub(r"\s+", "", text)
    if len(compact) >= 3 and compact not in GENERIC_CONTACT_VALUES:
        keys.add(f"raw:{compact}")

    for email in re.findall(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", text):
        keys.add(f"email:{email}")

    for phone in re.findall(r"\+?\d[\d\s()\-]{5,}\d", text):
        digits = re.sub(r"\D", "", phone)
        if len(digits) >= 7:
            keys.add(f"phone:{digits}")

    for segment in re.split(r"[,，;；|/\n]+", text):
        cleaned = re.sub(
            r"^(?:电话|手机|微信|企微|邮箱|phone|wechat|email)\s*[:：=]?\s*",
            "",
            segment.strip(),
        )
        cleaned = re.sub(r"\s+", "", cleaned)
        if len(cleaned) >= 3 and cleaned not in GENERIC_CONTACT_VALUES:
            keys.add(f"contact:{cleaned}")

    return keys


def find_recent_lead_by_contact(db: Session, customer_contact: str) -> Lead | None:
    target_keys = normalize_contact_keys(customer_contact)
    if not target_keys:
        return None

    cutoff = now_utc_naive() - timedelta(hours=LEAD_DEDUP_WINDOW_HOURS)
    candidates = (
        db.query(Lead)
        .filter(Lead.updated_at >= cutoff, Lead.customer_contact != "")
        .order_by(Lead.updated_at.desc())
        .all()
    )
    return next(
        (
            lead
            for lead in candidates
            if target_keys.intersection(normalize_contact_keys(lead.customer_contact))
        ),
        None,
    )


def append_latest_question(remark: str, question: str) -> str:
    latest = question.strip()[:MAX_QUESTION_NOTE_LENGTH]
    if not latest:
        return remark

    note = f"最近咨询：{latest}"
    current = remark.strip()
    if note in current:
        return current

    combined = f"{current}\n{note}" if current else note
    if len(combined) <= MAX_REMARK_LENGTH:
        return combined
    return f"{current[:1400].rstrip()}\n...\n{note[-550:]}"


def should_replace_handoff_reason(current: str | None, incoming: str | None) -> bool:
    if not incoming:
        return False
    return HANDOFF_REASON_PRIORITY.get(incoming, 1) >= HANDOFF_REASON_PRIORITY.get(current, 0)


def create_or_update_chat_lead(
    db: Session,
    *,
    customer_name: str,
    customer_contact: str,
    question: str,
    intent_level: str,
    requires_handoff: bool,
    handoff_reason: str | None,
) -> Lead:
    existing = find_recent_lead_by_contact(db, customer_contact)
    if not existing:
        lead = Lead(
            customer_name=customer_name,
            customer_contact=customer_contact,
            requirement=question,
            intent_level=intent_level,
            status="new",
            remark="AI 对话自动沉淀" if intent_level == "high" else "人工跟进自动沉淀",
            requires_handoff=requires_handoff,
            handoff_reason=handoff_reason,
        )
        db.add(lead)
        return lead

    if customer_name.strip():
        existing.customer_name = customer_name.strip()
    existing.requirement = question.strip()
    if intent_level == "high":
        existing.intent_level = "high"
    existing.requires_handoff = existing.requires_handoff or requires_handoff
    if should_replace_handoff_reason(existing.handoff_reason, handoff_reason):
        existing.handoff_reason = handoff_reason
    existing.remark = append_latest_question(existing.remark, question)
    return existing
