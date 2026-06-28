from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.deps import get_db, verify_token
from app.models import CompanySettings
from app.schemas import CompanySettingsOut, CompanySettingsUpdate, PublicCompanySettings
from app.services.company_service import (
    DEFAULT_COMPANY_SETTINGS,
    get_or_create_company_settings,
    normalize_embed_domains,
    normalize_widget_position,
)

router = APIRouter(prefix="/api/company-settings", tags=["company-settings"])


def to_public_settings(settings: CompanySettings) -> PublicCompanySettings:
    return PublicCompanySettings(
        company_name=settings.company_name,
        company_short_name=settings.company_short_name,
        company_logo_url=settings.company_logo_url,
        company_intro=settings.company_intro,
        customer_service_name=settings.customer_service_name,
        customer_service_avatar_url=settings.customer_service_avatar_url,
        welcome_message=settings.welcome_message,
        brand_color=settings.brand_color,
        business_scope=settings.business_scope,
        human_contact_phone=settings.human_contact_phone,
        human_contact_wechat=settings.human_contact_wechat,
        human_contact_email=settings.human_contact_email,
        business_hours=settings.business_hours,
        handoff_message=settings.handoff_message,
    )


@router.get("", response_model=CompanySettingsOut, dependencies=[Depends(verify_token)])
def get_company_settings(db: Session = Depends(get_db)) -> CompanySettings:
    try:
        return get_or_create_company_settings(db)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="读取企业设置失败，请稍后重试") from exc


@router.put("", response_model=CompanySettingsOut, dependencies=[Depends(verify_token)])
def update_company_settings(payload: CompanySettingsUpdate, db: Session = Depends(get_db)) -> CompanySettings:
    try:
        settings = get_or_create_company_settings(db)
        data = payload.model_dump()
        if not data.get("company_short_name"):
            data["company_short_name"] = data["company_name"]
        data["allowed_embed_domains"] = normalize_embed_domains(data.get("allowed_embed_domains", ""))
        data["widget_position"] = normalize_widget_position(data.get("widget_position", "right"))
        for key in DEFAULT_COMPANY_SETTINGS:
            setattr(settings, key, data.get(key, ""))
        db.commit()
        db.refresh(settings)
        return settings
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="保存企业设置失败，请稍后重试") from exc


@router.get("/public", response_model=PublicCompanySettings)
def get_public_company_settings(db: Session = Depends(get_db)) -> PublicCompanySettings:
    try:
        return to_public_settings(get_or_create_company_settings(db))
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="读取企业公开设置失败，请稍后重试") from exc
