from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.deps import get_db, verify_token
from app.models import Conversation, Lead
from app.schemas import ChatRequest, ChatResponse
from app.services.ai_service import generate_answer
from app.services.intent_service import detect_intent
from app.services.rag_service import build_context, retrieve_knowledge

router = APIRouter(prefix="/api/chat", tags=["chat"], dependencies=[Depends(verify_token)])


def build_prompt(context: str, question: str) -> str:
    return f"""你是一个专业、简洁、可靠的中文 AI 销售客服顾问。
你只能根据知识库内容回答用户问题。
如果知识库没有相关内容，必须回答“目前资料中没有相关信息”，不要编造。
回答要简洁、专业、适合销售客服场景。
当用户表现出购买、报价、合作、搭建等意向时，在回答问题后，引导用户补充需求信息。

知识库内容：
{context}

客户问题：
{question}

请生成销售客服回复。"""


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    matched_knowledge = retrieve_knowledge(payload.question, db)
    intent = detect_intent(payload.question, has_related_knowledge=bool(matched_knowledge))

    if not matched_knowledge:
        answer = "目前资料中没有相关信息"
    else:
        prompt = build_prompt(build_context(matched_knowledge), payload.question)
        answer = await generate_answer(prompt, db=db)

    conversation = Conversation(
        customer_name=payload.customer_name,
        customer_contact=payload.customer_contact,
        question=payload.question,
        answer=answer,
        intent_type=intent.intent_type,
        intent_level=intent.intent_level,
        source="web",
    )
    db.add(conversation)

    if intent.intent_level == "high":
        db.add(
            Lead(
                customer_name=payload.customer_name,
                customer_contact=payload.customer_contact,
                requirement=payload.question,
                intent_level=intent.intent_level,
                status="new",
                remark="AI 对话自动沉淀",
            )
        )

    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="保存对话或线索失败，请稍后重试") from exc

    return ChatResponse(
        answer=answer,
        intent_type=intent.intent_type,
        intent_level=intent.intent_level,
        matched_knowledge=matched_knowledge,
    )
