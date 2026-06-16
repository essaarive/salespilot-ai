from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.deps import get_db, verify_token
from app.models import Conversation
from app.schemas import ConversationOut, MessageResponse

router = APIRouter(prefix="/api/conversations", tags=["conversations"], dependencies=[Depends(verify_token)])


@router.get("", response_model=list[ConversationOut])
def list_conversations(db: Session = Depends(get_db)) -> list[Conversation]:
    return db.query(Conversation).order_by(Conversation.created_at.desc()).all()


@router.get("/{conversation_id}", response_model=ConversationOut)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    return conversation


@router.delete("/{conversation_id}", response_model=MessageResponse)
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)) -> MessageResponse:
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    try:
        db.delete(conversation)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="删除对话失败，请稍后重试") from exc
    return MessageResponse(message="删除成功")
