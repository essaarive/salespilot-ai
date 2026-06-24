import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.deps import get_db, verify_token
from app.models import Conversation, Lead
from app.schemas import ChatRequest, ChatResponse
from app.services.ai_service import generate_answer_with_meta
from app.services.intent_service import classify_scope, detect_intent
from app.services.rag_service import build_context, retrieve_knowledge_result

router = APIRouter(prefix="/api/chat", tags=["chat"], dependencies=[Depends(verify_token)])
public_router = APIRouter(prefix="/api/public/chat", tags=["public-chat"])

GREETING_REPLY = "您好，我是 SalesPilot AI 智销助手，可以为您介绍 AI 客服方案、价格、交付周期、适用行业和售后服务。请问您想了解哪方面？"
IRRELEVANT_REPLY = "您好，我主要用于解答 AI 客服系统、价格方案、交付周期、适用行业和售后服务相关问题。您可以告诉我想了解的业务场景或需求。"
UNSAFE_REPLY = "这个我不能协助。SalesPilot AI 的定位是帮助企业进行合规的客户接待、产品咨询和销售线索管理。如果您想优化正常销售话术或客服回复，我可以帮您整理更专业的表达。"
OUT_OF_SCOPE_REPLY = "这个话题和 AI 销售客服关系不大，我就不展开了。您可以咨询价格、功能、企业微信或飞书接入、交付周期、适用行业和售后维护，我会更有帮助。"
KNOWLEDGE_NOT_FOUND_REPLY = "这个问题目前在企业资料中没有找到明确说明。您可以留下联系方式，我们安排工作人员进一步确认后回复您。"
CUSTOMER_REQUESTED_HUMAN_REPLY = "您的问题已记录，我们建议由工作人员进一步确认并跟进。我们会根据您填写的联系方式安排后续沟通。"
SPECIAL_QUOTE_REPLY = "这类需求涉及定制报价或特殊合作条件，建议由工作人员结合团队规模、使用场景和接入范围进一步确认。您的问题已记录，后续可由人工跟进。"
COMPLAINT_RISK_REPLY = "您的问题已记录。这类情况建议由工作人员进一步核实和处理，避免仅凭自动回复造成误解。"

CUSTOMER_HUMAN_WORDS = ["转人工", "找人工", "人工客服", "真人客服", "联系销售", "找销售"]
SPECIAL_QUOTE_WORDS = ["定制报价", "特殊折扣", "大批量", "500 人", "500人", "招标", "合同"]
CUSTOM_REQUIREMENT_WORDS = ["代理合作", "项目合作", "复杂定制"]
COMPLAINT_RISK_WORDS = ["投诉", "退款", "赔偿", "纠纷", "严重问题"]
UNANSWERED_SPECIAL_TERMS = ["海外", "多语言", "sap", "SAP", "深度集成"]
SUBJECT_INTENT_WORDS = [
    "多少钱",
    "价格",
    "报价",
    "费用",
    "套餐",
    "收费",
    "预算",
    "能接",
    "接入",
    "支持",
    "企业微信",
    "企微",
    "微信客服",
    "微信",
    "多久",
    "上线",
    "交付",
    "部署",
    "周期",
    "几天",
    "可以",
    "能不能",
    "是否",
    "吗",
]


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
9. 如果知识库中同时有通用套餐资料和文件上传资料，且文件资料包含客户提到的具体产品名、方案名称、标题关键词、价格、交付周期或接入支持，必须优先使用文件资料中的明确事实；具体事实优先于通用套餐说明。
10. 回答价格、交付周期、接入支持等明确事实时，必须保留知识库中的具体数值或结论，不要用其他通用价格或默认模板覆盖。
11. 只有在提供的知识库上下文明确支持时，才能给出具体价格、交期、功能、接入和售后承诺。
12. 如果知识库不足，请明确说明当前企业资料中没有找到可靠信息，并建议人工确认；不要将通用建议伪装成企业事实。

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


def detect_handoff_reason(question: str) -> str | None:
    text = question.strip().lower()
    if any(word.lower() in text for word in CUSTOMER_HUMAN_WORDS):
        return "customer_requested_human"
    if any(word.lower() in text for word in SPECIAL_QUOTE_WORDS):
        return "special_quote"
    if any(word.lower() in text for word in CUSTOM_REQUIREMENT_WORDS):
        return "custom_requirement"
    if any(word.lower() in text for word in COMPLAINT_RISK_WORDS):
        return "complaint_or_risk"
    return None


def handoff_reply(reason: str) -> str:
    if reason == "customer_requested_human":
        return CUSTOMER_REQUESTED_HUMAN_REPLY
    if reason in {"special_quote", "custom_requirement"}:
        return SPECIAL_QUOTE_REPLY
    if reason == "complaint_or_risk":
        return COMPLAINT_RISK_REPLY
    return KNOWLEDGE_NOT_FOUND_REPLY


def has_unanswered_special_terms(question: str, matched_knowledge: list) -> bool:
    text = question.strip().lower()
    terms = [term.lower() for term in UNANSWERED_SPECIAL_TERMS if term.lower() in text]
    if not terms:
        return False

    knowledge_text = "\n".join(
        " ".join(
            [
                getattr(item, "title", ""),
                getattr(item, "category", ""),
                getattr(item, "keywords", ""),
                getattr(item, "content", ""),
            ]
        )
        for item in matched_knowledge
    ).lower()
    return not any(term in knowledge_text for term in terms)


def has_unanswered_subject_terms(question: str, matched_knowledge: list) -> bool:
    normalized = re.sub(r"[？?！!。，、\s]+", "", question.lower())
    cleaned = normalized
    for word in SUBJECT_INTENT_WORDS:
        cleaned = cleaned.replace(word.lower(), "")

    terms = {
        match.group(1)
        for match in re.finditer(r"([\u4e00-\u9fffA-Za-z0-9_-]{2,}?(?:版|型号|产品|方案|套餐))", cleaned)
    }
    if "产品" in cleaned and len(cleaned) >= 3:
        terms.add(cleaned)
    if "方案" in cleaned and len(cleaned) >= 3:
        terms.add(cleaned)
    terms = {term for term in terms if term not in {"产品", "方案", "套餐", "版本", "型号"}}
    if not terms:
        return False

    knowledge_text = re.sub(
        r"\s+",
        "",
        "\n".join(
            " ".join(
                [
                    getattr(item, "title", ""),
                    getattr(item, "category", ""),
                    getattr(item, "keywords", ""),
                    getattr(item, "content", ""),
                ]
            )
            for item in matched_knowledge
        ).lower(),
    )
    return not any(term in knowledge_text for term in terms)


async def handle_chat(payload: ChatRequest, db: Session) -> ChatResponse:
    retrieval = retrieve_knowledge_result(payload.question, db)
    matched_knowledge = retrieval.items
    scope = classify_scope(payload.question, has_related_knowledge=bool(matched_knowledge))
    reliable_knowledge = retrieval.has_reliable_knowledge
    intent = detect_intent(payload.question, has_related_knowledge=reliable_knowledge, scope_type=scope.scope_type)
    ai_source = "mock"
    provider = None
    model = None
    retrieval_confidence = retrieval.retrieval_confidence
    answer_basis = "general_guidance"
    requires_handoff = False
    handoff_reason = detect_handoff_reason(payload.question)

    if scope.scope_type == "unsafe":
        matched_knowledge = []
        answer = UNSAFE_REPLY
        retrieval_confidence = "none"
    elif handoff_reason:
        requires_handoff = True
        answer = handoff_reply(handoff_reason)
        answer_basis = "fallback"
    elif scope.scope_type == "out_of_scope":
        matched_knowledge = []
        answer = OUT_OF_SCOPE_REPLY
        retrieval_confidence = "none"
    elif scope.scope_type == "sales_adjacent":
        matched_knowledge = []
        answer = build_sales_adjacent_reply(payload.question, intent.intent_level)
        retrieval_confidence = "none"
    elif scope.scope_type == "general_chat" and intent.intent_type == "greeting":
        matched_knowledge = []
        answer = GREETING_REPLY
        retrieval_confidence = "none"
    elif scope.scope_type == "general_chat":
        matched_knowledge = []
        answer = build_general_chat_reply(payload.question)
        retrieval_confidence = "none"
    elif intent.intent_type == "irrelevant" and not matched_knowledge:
        answer = IRRELEVANT_REPLY
        retrieval_confidence = "none"
    elif scope.scope_type == "business_related" and (
        has_unanswered_special_terms(payload.question, matched_knowledge)
        or has_unanswered_subject_terms(payload.question, matched_knowledge)
    ):
        matched_knowledge = []
        answer = KNOWLEDGE_NOT_FOUND_REPLY
        answer_basis = "fallback"
        retrieval_confidence = "low"
        requires_handoff = True
        handoff_reason = "knowledge_not_found"
    elif not matched_knowledge:
        answer = KNOWLEDGE_NOT_FOUND_REPLY
        answer_basis = "fallback"
        retrieval_confidence = "none"
        if scope.scope_type == "business_related":
            requires_handoff = True
            handoff_reason = "knowledge_not_found"
    elif scope.scope_type == "business_related" and not reliable_knowledge:
        answer = KNOWLEDGE_NOT_FOUND_REPLY
        answer_basis = "fallback"
        requires_handoff = True
        handoff_reason = "knowledge_not_found"
    else:
        prompt = build_prompt(build_context(matched_knowledge), payload.question)
        ai_result = await generate_answer_with_meta(prompt, db=db)
        answer = ai_result.answer
        ai_source = ai_result.ai_source
        provider = ai_result.provider
        model = ai_result.model
        answer_basis = "knowledge"

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

    should_create_lead = intent.intent_level == "high" or (
        requires_handoff and bool(payload.customer_name.strip() or payload.customer_contact.strip())
    )

    if should_create_lead:
        db.add(
            Lead(
                customer_name=payload.customer_name,
                customer_contact=payload.customer_contact,
                requirement=payload.question,
                intent_level=intent.intent_level,
                status="new",
                remark="AI 对话自动沉淀" if intent.intent_level == "high" else "人工跟进自动沉淀",
                requires_handoff=requires_handoff,
                handoff_reason=handoff_reason,
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
        retrieval_confidence=retrieval_confidence,
        answer_basis=answer_basis,
        requires_handoff=requires_handoff,
        handoff_reason=handoff_reason,
    )


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    return await handle_chat(payload, db)


@public_router.post("", response_model=ChatResponse)
async def public_chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    return await handle_chat(payload, db)
