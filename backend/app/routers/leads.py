from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.deps import get_db, verify_token
from app.models import Lead
from app.schemas import LeadCreate, LeadOut, LeadUpdate, MessageResponse

router = APIRouter(prefix="/api/leads", tags=["leads"], dependencies=[Depends(verify_token)])


@router.get("", response_model=list[LeadOut])
def list_leads(db: Session = Depends(get_db)) -> list[Lead]:
    return db.query(Lead).order_by(Lead.created_at.desc()).all()


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int, db: Session = Depends(get_db)) -> Lead:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="线索不存在")
    return lead


@router.post("", response_model=LeadOut)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)) -> Lead:
    lead = Lead(**payload.model_dump())
    try:
        db.add(lead)
        db.commit()
        db.refresh(lead)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="创建线索失败，请检查输入后重试") from exc
    return lead


@router.put("/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: int, payload: LeadUpdate, db: Session = Depends(get_db)) -> Lead:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="线索不存在")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)
    try:
        db.commit()
        db.refresh(lead)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="更新线索失败，请检查输入后重试") from exc
    return lead


@router.delete("/{lead_id}", response_model=MessageResponse)
def delete_lead(lead_id: int, db: Session = Depends(get_db)) -> MessageResponse:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="线索不存在")
    try:
        db.delete(lead)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="删除线索失败，请稍后重试") from exc
    return MessageResponse(message="删除成功")
