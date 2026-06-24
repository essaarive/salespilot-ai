import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.deps import get_db, verify_token
from app.models import CompanySettings, Conversation, Lead
from app.schemas import ChatRequest, ChatResponse
from app.services.ai_service import generate_answer_with_meta
from app.services.company_service import get_or_create_company_settings, public_contact_lines
from app.services.intent_service import classify_scope, detect_intent
from app.services.rag_service import build_context, retrieve_knowledge_result

router = APIRouter(prefix="/api/chat", tags=["chat"], dependencies=[Depends(verify_token)])
public_router = APIRouter(prefix="/api/public/chat", tags=["public-chat"])

DEFAULT_SCOPE_HINT = "价格、功能、交付周期、适用场景、接入方式和售后维护"

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


def company_display_name(company: CompanySettings) -> str:
    return company.company_short_name or company.company_name or "SalesPilot AI"


def company_scope(company: CompanySettings) -> str:
    return (company.business_scope or DEFAULT_SCOPE_HINT).strip(" ，,。.")


def company_contact_text(company: CompanySettings) -> str:
    lines = public_contact_lines(company)
    return "；".join(lines) if lines else "未配置"


def build_company_context(company: CompanySettings) -> str:
    return "\n".join(
        [
            f"企业名称：{company.company_name or 'SalesPilot AI'}",
            f"企业简介：{company.company_intro or '面向中小企业的 AI 智能获客客服系统。'}",
            f"客服名称：{company.customer_service_name or '智销助手'}",
            f"业务范围：{company_scope(company)}",
            f"工作时间：{company.business_hours or '未配置'}",
            f"人工联系方式：{company_contact_text(company)}",
            f"禁止回答内容：{company.forbidden_topics or '未配置'}",
        ]
    )


def build_prompt(context: str, question: str, company: CompanySettings) -> str:
    return f"""你是当前企业的 AI 客服顾问，不是通用聊天机器人。
你必须使用当前企业身份回答，不要自称为 SalesPilot AI，除非当前企业名称就是 SalesPilot AI。
当前服务企业：
{build_company_context(company)}

你的核心任务不是做通用聊天，而是围绕当前企业业务范围、智能获客、知识库问答、客户意向识别、线索沉淀和人工跟进进行咨询回复。
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
13. 只围绕当前企业业务范围和有效知识库回答；不要编造企业名称、联系方式、业务能力或承诺。
14. 如果客户问题命中禁止回答内容，不展开回答，建议由工作人员确认。

知识库内容：
{context}

客户问题：
{question}

请生成销售客服回复。"""


def build_greeting_reply(company: CompanySettings) -> str:
    return company.welcome_message or (
        f"您好，我是{company_display_name(company)}的{company.customer_service_name or 'AI 客服'}，"
        f"可以协助您了解{company_scope(company)}。请问您想先了解哪方面？"
    )


def build_irrelevant_reply(company: CompanySettings) -> str:
    return f"您好，我主要负责{company_display_name(company)}相关咨询，例如{company_scope(company)}。您可以告诉我想了解的业务场景或需求。"


def build_unsafe_reply(company: CompanySettings) -> str:
    return f"这个我不能协助。{company_display_name(company)}的 AI 客服定位是帮助企业进行合规的客户接待、产品咨询和销售线索管理。如果您想优化正常客服或销售表达，我可以帮您整理更专业的说法。"


def build_out_of_scope_reply(company: CompanySettings) -> str:
    return f"这个话题和{company_display_name(company)}的业务咨询关系不大，我就不展开了。您可以咨询{company_scope(company)}，我会更有帮助。"


def build_knowledge_not_found_reply(company: CompanySettings) -> str:
    return company.handoff_message or "这个问题目前在企业资料中没有找到明确说明。您可以留下联系方式，我们安排工作人员进一步确认后回复您。"


def append_contact_if_available(message: str, company: CompanySettings) -> str:
    contact_lines = public_contact_lines(company)
    if not contact_lines:
        return message
    return f"{message} 您也可以通过{ '；'.join(contact_lines) } 进一步联系人工客服。"


def build_sales_adjacent_reply(question: str, intent_level: str, company: CompanySettings) -> str:
    if intent_level == "high":
        return f"这个问题很适合结合{company_display_name(company)}的业务流程来评估。建议先统一常见咨询话术，再用 AI 自动接待、识别高意向客户并沉淀线索。如果您正在考虑落地，可以继续补充渠道、预算和上线时间。"
    return f"销售转化或客服效率低，通常可以先从两点优化：统一高频问题回复话术，并优先跟进高意向客户。{company_display_name(company)}的 AI 客服可以围绕{company_scope(company)}进行自动接待和线索沉淀。"


def build_general_chat_reply(question: str, company: CompanySettings) -> str:
    text = question.strip().lower()
    if "人工智能" in text or "什么是ai" in text or "ai是什么" in text:
        return f"人工智能简单来说，就是让系统具备理解、生成、分类和辅助决策的能力。在客服场景里，AI 可以根据企业知识库自动回复客户问题，并识别购买意向。您是想了解它怎么落地到{company_display_name(company)}的业务里吗？"
    if "吃什么" in text:
        return f"这个问题我可以简单聊一句：可以选方便补充能量、适合自己口味的餐食。不过我主要负责{company_display_name(company)}相关咨询，比如{company_scope(company)}。您想了解哪项业务吗？"
    if "写代码" in text:
        return f"我可以简单理解代码相关问题，但在这个系统里，我主要负责{company_display_name(company)}的业务咨询。您可以问我{company_scope(company)}。"
    if "你是谁" in text:
        return f"我是{company.company_name or company_display_name(company)}的{company.customer_service_name or 'AI 客服'}，主要协助您了解{company_scope(company)}。您可以告诉我具体需求，我帮您判断下一步。"
    return f"这个问题可以简单聊，但我主要负责{company_display_name(company)}相关咨询。您可以问我{company_scope(company)}。"


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


def handoff_reply(reason: str, company: CompanySettings) -> str:
    if reason == "customer_requested_human":
        return append_contact_if_available(build_knowledge_not_found_reply(company), company)
    if reason in {"special_quote", "custom_requirement"}:
        return append_contact_if_available(
            "这类需求涉及定制报价或特殊合作条件，建议由工作人员结合团队规模、使用场景和接入范围进一步确认。您的问题已记录，后续可由人工跟进。",
            company,
        )
    if reason == "complaint_or_risk":
        return append_contact_if_available("您的问题已记录。这类情况建议由工作人员进一步核实和处理，避免仅凭自动回复造成误解。", company)
    return append_contact_if_available(build_knowledge_not_found_reply(company), company)


def split_forbidden_topics(company: CompanySettings) -> list[str]:
    return [
        part.strip().lower()
        for part in re.split(r"[,，、\n;；]+", company.forbidden_topics or "")
        if part.strip()
    ]


def detect_forbidden_topic(question: str, company: CompanySettings) -> bool:
    text = question.strip().lower()
    return any(topic in text for topic in split_forbidden_topics(company))


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
    try:
        company = get_or_create_company_settings(db)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="读取企业设置失败，请稍后重试") from exc

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

    if detect_forbidden_topic(payload.question, company):
        matched_knowledge = []
        requires_handoff = True
        handoff_reason = "custom_requirement"
        answer = append_contact_if_available(build_knowledge_not_found_reply(company), company)
        answer_basis = "fallback"
        retrieval_confidence = "none"
    elif scope.scope_type == "unsafe":
        matched_knowledge = []
        answer = build_unsafe_reply(company)
        retrieval_confidence = "none"
    elif handoff_reason:
        requires_handoff = True
        answer = handoff_reply(handoff_reason, company)
        answer_basis = "fallback"
    elif scope.scope_type == "out_of_scope":
        matched_knowledge = []
        answer = build_out_of_scope_reply(company)
        retrieval_confidence = "none"
    elif scope.scope_type == "sales_adjacent":
        matched_knowledge = []
        answer = build_sales_adjacent_reply(payload.question, intent.intent_level, company)
        retrieval_confidence = "none"
    elif scope.scope_type == "general_chat" and intent.intent_type == "greeting":
        matched_knowledge = []
        answer = build_greeting_reply(company)
        retrieval_confidence = "none"
    elif scope.scope_type == "general_chat":
        matched_knowledge = []
        answer = build_general_chat_reply(payload.question, company)
        retrieval_confidence = "none"
    elif intent.intent_type == "irrelevant" and not matched_knowledge:
        answer = build_irrelevant_reply(company)
        retrieval_confidence = "none"
    elif scope.scope_type == "business_related" and (
        has_unanswered_special_terms(payload.question, matched_knowledge)
        or has_unanswered_subject_terms(payload.question, matched_knowledge)
    ):
        matched_knowledge = []
        answer = append_contact_if_available(build_knowledge_not_found_reply(company), company)
        answer_basis = "fallback"
        retrieval_confidence = "low"
        requires_handoff = True
        handoff_reason = "knowledge_not_found"
    elif not matched_knowledge:
        answer = append_contact_if_available(build_knowledge_not_found_reply(company), company)
        answer_basis = "fallback"
        retrieval_confidence = "none"
        if scope.scope_type == "business_related":
            requires_handoff = True
            handoff_reason = "knowledge_not_found"
    elif scope.scope_type == "business_related" and not reliable_knowledge:
        answer = append_contact_if_available(build_knowledge_not_found_reply(company), company)
        answer_basis = "fallback"
        requires_handoff = True
        handoff_reason = "knowledge_not_found"
    else:
        prompt = build_prompt(build_context(matched_knowledge), payload.question, company)
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
