from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import CompanySettings

DEFAULT_COMPANY_SETTINGS = {
    "company_name": "SalesPilot AI",
    "company_short_name": "SalesPilot AI",
    "company_logo_url": "",
    "company_intro": "面向中小企业的 AI 智能获客客服系统。",
    "customer_service_name": "智销助手",
    "customer_service_avatar_url": "",
    "welcome_message": "您好，我是 SalesPilot AI 智销助手，可以为您介绍 AI 客服方案、知识库能力、价格、交付周期和接入方式。",
    "brand_color": "#2563EB",
    "business_scope": "AI 客服、知识库问答、销售线索沉淀、多模型接入、企业官网咨询。",
    "human_contact_phone": "",
    "human_contact_wechat": "",
    "human_contact_email": "",
    "business_hours": "周一至周五 09:00-18:00",
    "handoff_message": "您的问题已记录，我们建议由工作人员进一步确认并跟进。",
    "forbidden_topics": "",
}


def get_or_create_company_settings(db: Session) -> CompanySettings:
    settings = db.query(CompanySettings).order_by(CompanySettings.id.asc()).first()
    if settings:
        return settings

    settings = CompanySettings(**DEFAULT_COMPANY_SETTINGS)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def ensure_company_settings(db: Session) -> None:
    try:
        get_or_create_company_settings(db)
    except SQLAlchemyError:
        db.rollback()
        raise


def public_contact_lines(settings: CompanySettings) -> list[str]:
    lines = []
    if settings.human_contact_phone:
        lines.append(f"电话：{settings.human_contact_phone}")
    if settings.human_contact_wechat:
        lines.append(f"微信：{settings.human_contact_wechat}")
    if settings.human_contact_email:
        lines.append(f"邮箱：{settings.human_contact_email}")
    if settings.business_hours:
        lines.append(f"工作时间：{settings.business_hours}")
    return lines


def has_human_contact(settings: CompanySettings) -> bool:
    return any(
        [
            settings.human_contact_phone.strip(),
            settings.human_contact_wechat.strip(),
            settings.human_contact_email.strip(),
        ]
    )
