from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.deps import get_db, verify_token
from app.models import KnowledgeItem
from app.schemas import KnowledgeCreate, KnowledgeOut, KnowledgeUpdate, MessageResponse

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"], dependencies=[Depends(verify_token)])


@router.get("", response_model=list[KnowledgeOut])
def list_knowledge(
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[KnowledgeItem]:
    query = db.query(KnowledgeItem).order_by(KnowledgeItem.created_at.desc())
    if category:
        query = query.filter(KnowledgeItem.category == category)
    return query.all()


@router.get("/{knowledge_id}", response_model=KnowledgeOut)
def get_knowledge(knowledge_id: int, db: Session = Depends(get_db)) -> KnowledgeItem:
    item = db.get(KnowledgeItem, knowledge_id)
    if not item:
        raise HTTPException(status_code=404, detail="知识不存在")
    return item


@router.post("", response_model=KnowledgeOut)
def create_knowledge(payload: KnowledgeCreate, db: Session = Depends(get_db)) -> KnowledgeItem:
    item = KnowledgeItem(**payload.model_dump())
    try:
        db.add(item)
        db.commit()
        db.refresh(item)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="创建知识失败，请检查输入后重试") from exc
    return item


@router.put("/{knowledge_id}", response_model=KnowledgeOut)
def update_knowledge(
    knowledge_id: int,
    payload: KnowledgeUpdate,
    db: Session = Depends(get_db),
) -> KnowledgeItem:
    item = db.get(KnowledgeItem, knowledge_id)
    if not item:
        raise HTTPException(status_code=404, detail="知识不存在")

    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
        db.refresh(item)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="更新知识失败，请检查输入后重试") from exc
    return item


@router.delete("/{knowledge_id}", response_model=MessageResponse)
def delete_knowledge(knowledge_id: int, db: Session = Depends(get_db)) -> MessageResponse:
    item = db.get(KnowledgeItem, knowledge_id)
    if not item:
        raise HTTPException(status_code=404, detail="知识不存在")

    try:
        db.delete(item)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="删除知识失败，请稍后重试") from exc
    return MessageResponse(message="删除成功")
