from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.deps import get_db, verify_token
from app.models import Conversation, Lead
from app.schemas import ChatRequest, ChatResponse
from app.services.ai_service import generate_answer_with_meta
from app.services.intent_service import classify_scope, detect_intent
from app.services.rag_service import build_context, retrieve_knowledge

router = APIRouter(prefix="/api/chat", tags=["chat"], dependencies=[Depends(verify_token)])
public_router = APIRouter(prefix="/api/public/chat", tags=["public-chat"])

GREETING_REPLY = "您好，我是 SalesPilot AI 智销助手，可以为您介绍 AI 客服方案、价格、交付周期、适用行业和售后服务。请问您想了解哪方面？"
IRRELEVANT_REPLY = "您好，我主要用于解答 AI 客服系统、价格方案、交付周期、适用行业和售后服务相关问题。您可以告诉我想了解的业务场景或需求。"
UNSAFE_REPLY = "这个我不能协助。SalesPilot AI 的定位是帮助企业进行合规的客户接待、产品咨询和销售线索管理。如果您想优化正常销售话术或客服回复，我可以帮您整理更专业的表达。"
OUT_OF_SCOPE_REPLY = "这个话题和 AI 销售客服关系不大，我就不展开了。您可以咨询价格、功能、企业微信或飞书接入、交付周期、适用行业和售后维护，我会更有帮助。"


def build_prompt(context: str, question: str) -> str:
    return f"""你是 SalesPilot AI 智销助手，一个面向中小企业的 AI 销售客服顾问。
你的核心任务不是做通用聊天，而是围绕 AI 客服系统、智能获客、知识库问答、客户意向识别、线索沉淀和多模型接入进行咨询回复。
你可以简短回应客户的普通问题，但必须自然引导回 AI 销售客服业务。
回答时请遵循：
1. 业务相关问题：结合知识库认真回答。
2. 弱相关问题：简短建议 + 说明 AI 客服如何帮助。
3. 无关闲聊：最多简单回应一句，然后引导客户咨询 AI 客服相关内容。
4. 高风险或不合规问题：拒绝协助，并引导回合规客服场景。
5. 默认回复控制在 80-180 字，除非用户明确要求详细说明。
6. 不使用 Markdown 加粗符号、复杂标题或长编号列表。
7. 不编造知识库没有的产品能力、价格和交付承诺。
8. 客户明确问价格时，再回答价格范围；明确问交付周期时，再回答上线周期；明确问行业时，再回答适用行业；明确问接入方式时，再回答企业微信、飞书、网页客服等接入。

知识库内容：
{context}

客户问题：
{question}

请生成销售客服回复。"""


def build_sales_adjacent_reply(question: str, intent_level: str) -> str:
    if intent_level == "high":
        return "这个问题很适合用 AI 销售客服来辅助解决。建议先统一常见咨询话术，再用 AI 自动接待、识别高意向客户并沉淀线索。如果您正在考虑搭建，我可以继续帮您评估适合的接入渠道、预算和上线周期。"
    return "销售转化或客服效率低，通常可以先从两点优化：统一高频问题回复话术，并优先跟进高意向客户。SalesPilot AI 可以自动接待咨询、识别购买意向并沉淀线索，帮助销售把时间放在更值得跟进的客户上。"


def build_general_chat_reply(question: str) -> str:
    text = question.strip().lower()
    if "人工智能" in text or "什么是ai" in text or "ai是什么" in text:
        return "人工智能简单来说，就是让系统具备理解、生成、分类和辅助决策的能力。在客服场景里，AI 可以根据企业知识库自动回复客户问题，并识别购买意向。您是想了解 AI 客服的原理，还是想看它怎么落地到业务里？"
    if "吃什么" in text:
        return "这个问题我可以简单聊一句：可以选方便补充能量、适合自己口味的餐食。不过我主要负责 AI 销售客服相关咨询，比如价格、接入方式、交付周期和适用行业。您想了解 AI 客服能帮企业做什么吗？"
    if "写代码" in text:
        return "我可以简单理解代码相关问题，但在这个系统里，我主要负责 AI 销售客服咨询。比如帮您了解知识库问答、客户意向识别、线索沉淀、多模型接入和部署方式。您想看哪个业务场景？"
    if "你是谁" in text:
        return "我是 SalesPilot AI 智销助手，主要帮您了解 AI 销售客服系统的能力、价格、接入方式、交付周期和适用行业。您可以告诉我业务场景，我帮您判断是否适合落地。"
    return "这个问题可以简单聊，但我主要负责 AI 销售客服相关咨询。您可以问我价格套餐、企业微信或飞书接入、知识库导入、交付周期、适用行业和售后维护。"


async def handle_chat(payload: ChatRequest, db: Session) -> ChatResponse:
    matched_knowledge = retrieve_knowledge(payload.question, db)
    scope = classify_scope(payload.question, has_related_knowledge=bool(matched_knowledge))
    intent = detect_intent(payload.question, has_related_knowledge=bool(matched_knowledge), scope_type=scope.scope_type)
    ai_source = "mock"
    provider = None
    model = None

    if scope.scope_type == "unsafe":
        matched_knowledge = []
        answer = UNSAFE_REPLY
    elif scope.scope_type == "out_of_scope":
        matched_knowledge = []
        answer = OUT_OF_SCOPE_REPLY
    elif scope.scope_type == "sales_adjacent":
        matched_knowledge = []
        answer = build_sales_adjacent_reply(payload.question, intent.intent_level)
    elif scope.scope_type == "general_chat" and intent.intent_type == "greeting":
        matched_knowledge = []
        answer = GREETING_REPLY
    elif scope.scope_type == "general_chat":
        matched_knowledge = []
        answer = build_general_chat_reply(payload.question)
    elif intent.intent_type == "irrelevant" and not matched_knowledge:
        answer = IRRELEVANT_REPLY
    elif not matched_knowledge:
        answer = "目前资料中没有相关信息"
    else:
        prompt = build_prompt(build_context(matched_knowledge), payload.question)
        ai_result = await generate_answer_with_meta(prompt, db=db)
        answer = ai_result.answer
        ai_source = ai_result.ai_source
        provider = ai_result.provider
        model = ai_result.model

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
        ai_source=ai_source,
        provider=provider,
        model=model,
        scope_type=scope.scope_type,
    )


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    return await handle_chat(payload, db)


@public_router.post("", response_model=ChatResponse)
async def public_chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    return await handle_chat(payload, db)
