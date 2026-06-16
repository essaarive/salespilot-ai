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
public_router = APIRouter(prefix="/api/public/chat", tags=["public-chat"])

GREETING_REPLY = "您好，我是 SalesPilot AI 智销助手，可以为您介绍 AI 客服方案、价格、交付周期、适用行业和售后服务。请问您想了解哪方面？"
IRRELEVANT_REPLY = "您好，我主要用于解答 AI 客服系统、价格方案、交付周期、适用行业和售后服务相关问题。您可以告诉我想了解的业务场景或需求。"


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


async def handle_chat(payload: ChatRequest, db: Session) -> ChatResponse:
    matched_knowledge = retrieve_knowledge(payload.question, db)
    intent = detect_intent(payload.question, has_related_knowledge=bool(matched_knowledge))

    if intent.intent_type == "greeting":
        answer = GREETING_REPLY
    elif intent.intent_type == "irrelevant" and not matched_knowledge:
        answer = IRRELEVANT_REPLY
    elif not matched_knowledge:
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


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    return await handle_chat(payload, db)


@public_router.post("", response_model=ChatResponse)
async def public_chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    return await handle_chat(payload, db)
