import os
import logging
import re
from dataclasses import dataclass
from typing import Any

import httpx
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.models import AIModelConfig

load_dotenv()

logger = logging.getLogger(__name__)

SPECIFIC_BUSINESS_TERMS = {
    "常规",
    "基础咨询方案",
    "基础方案",
    "咨询方案",
    "企业微信",
    "企微",
    "微信客服",
}


@dataclass(frozen=True)
class RuntimeAIConfig:
    provider: str
    name: str
    api_key: str
    base_url: str
    model: str
    enabled: bool = True


@dataclass(frozen=True)
class AIAnswer:
    answer: str
    ai_source: str
    provider: str
    model: str


def _parse_context_items(context: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    content_lines: list[str] = []

    def flush_current() -> None:
        nonlocal current, content_lines
        if current is None:
            return
        current["content"] = "\n".join(line for line in content_lines if line.strip()).strip()
        if current["content"]:
            items.append(current)
        current = None
        content_lines = []

    for line in context.splitlines():
        if line.startswith("标题："):
            flush_current()
            current = {
                "title": line.replace("标题：", "", 1).strip(),
                "category": "",
                "keywords": "",
                "source_type": "",
                "source_file_name": "",
                "content": "",
            }
            continue
        if current is None:
            continue
        if line.startswith("分类："):
            current["category"] = line.replace("分类：", "", 1).strip()
        elif line.startswith("关键词："):
            current["keywords"] = line.replace("关键词：", "", 1).strip()
        elif line.startswith("来源类型："):
            current["source_type"] = line.replace("来源类型：", "", 1).strip()
        elif line.startswith("来源文件："):
            current["source_file_name"] = line.replace("来源文件：", "", 1).strip()
        elif line.startswith("内容："):
            content_lines.append(line.replace("内容：", "", 1).strip())
        elif line.strip():
            content_lines.append(line.strip())

    flush_current()
    return items


def _parse_company_context(prompt: str) -> dict[str, str]:
    defaults = {
        "company_name": "SalesPilot AI",
        "company_intro": "面向中小企业的 AI 智能获客客服系统。",
        "customer_service_name": "智销助手",
        "business_scope": "AI 客服、知识库问答、销售线索沉淀、多模型接入、企业官网咨询。",
        "business_hours": "周一至周五 09:00-18:00",
        "human_contact": "未配置",
        "forbidden_topics": "未配置",
    }
    marker = "当前服务企业："
    end_marker = "回答时请遵循："
    if marker not in prompt or end_marker not in prompt:
        return defaults

    block = prompt.split(marker, 1)[1].split(end_marker, 1)[0]
    field_map = {
        "企业名称：": "company_name",
        "企业简介：": "company_intro",
        "客服名称：": "customer_service_name",
        "业务范围：": "business_scope",
        "工作时间：": "business_hours",
        "人工联系方式：": "human_contact",
        "禁止回答内容：": "forbidden_topics",
    }
    parsed = defaults.copy()
    for line in block.splitlines():
        for prefix, key in field_map.items():
            if line.startswith(prefix):
                parsed[key] = line.replace(prefix, "", 1).strip() or defaults[key]
    return parsed


def _summarize_items(items: list[dict[str, str]], limit: int = 3) -> str:
    contents = []
    for item in items[:limit]:
        content = _clean_context_content(item["content"]).rstrip("。")
        if content and content not in contents:
            contents.append(content)
    return "；".join(contents)


def _clean_context_content(content: str) -> str:
    cleaned = re.sub(r"^来源文件：.*$", "", content, flags=re.MULTILINE)
    cleaned = re.sub(r"^片段：\d+.*$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^正文：", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\n+", "，", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ，")
    return cleaned


def sanitize_answer(text: str) -> str:
    cleaned = re.sub(r"```[\s\S]*?```", lambda match: match.group(0).replace("```", ""), text)
    cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"__(.*?)__", r"\1", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"^\s{0,3}#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.replace("```", "").replace("**", "")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    if len(cleaned) <= 500:
        return cleaned

    boundary = max(cleaned.rfind("。", 0, 500), cleaned.rfind("！", 0, 500), cleaned.rfind("？", 0, 500))
    if boundary >= 120:
        return cleaned[: boundary + 1]
    return cleaned[:500].rstrip()


def _contains_any(text: str, words: list[str]) -> bool:
    return any(word.lower() in text.lower() for word in words)


def _is_general_intro(question: str) -> bool:
    return _contains_any(
        question,
        ["介绍一下", "了解一下", "你们是做什么", "你们做什么", "什么系统", "什么产品", "简单介绍", "介绍下"],
    )


def _finish(answer: str) -> str:
    return sanitize_answer(answer)


def _specific_terms_from_question(question: str) -> list[str]:
    normalized = re.sub(r"[？?！!。，、\s]+", "", question.lower())
    terms = [
        match.group(1)
        for match in re.finditer(r"([\u4e00-\u9fffA-Za-z0-9_-]{2,}?(?:版|型号|产品|方案|套餐))", normalized)
    ]
    terms.extend(term for term in SPECIFIC_BUSINESS_TERMS if term in normalized)
    cleaned = normalized
    for word in [
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
    ]:
        cleaned = cleaned.replace(word.lower(), "")
    if len(cleaned) >= 3 or cleaned in SPECIFIC_BUSINESS_TERMS:
        terms.append(cleaned)

    unique_terms: list[str] = []
    for term in terms:
        if (len(term) >= 3 or term in SPECIFIC_BUSINESS_TERMS) and term not in unique_terms:
            unique_terms.append(term)
    return unique_terms


def _prioritized_items(items: list[dict[str, str]], question: str) -> list[dict[str, str]]:
    terms = _specific_terms_from_question(question)
    if not terms:
        return items

    def rank(item: dict[str, str]) -> tuple[int, int]:
        haystack = " ".join(
            [
                item.get("title", ""),
                item.get("category", ""),
                item.get("keywords", ""),
                item.get("source_file_name", ""),
                item.get("content", ""),
            ]
        ).lower()
        compact_haystack = re.sub(r"\s+", "", haystack)
        matched = any(term in haystack or term in compact_haystack for term in terms)
        is_document = item.get("source_type") == "document"
        return (1 if matched and is_document else 0, 1 if matched else 0)

    return sorted(items, key=rank, reverse=True)


def _item_matches_terms(item: dict[str, str], terms: list[str]) -> bool:
    haystack = " ".join(
        [
            item.get("title", ""),
            item.get("category", ""),
            item.get("keywords", ""),
            item.get("source_file_name", ""),
            item.get("content", ""),
        ]
    ).lower()
    compact_haystack = re.sub(r"\s+", "", haystack)
    return any(term in haystack or term in compact_haystack for term in terms)


def _question_subject(question: str) -> str:
    terms = _specific_terms_from_question(question)
    return terms[0] if terms else "该方案"


def _extract_price(content: str) -> str:
    compact = _clean_context_content(content)
    patterns = [
        r"(?:价格|报价|费用|收费)[：:\s]*(?:为|是)?\s*([^。；;\n，,]+?元)",
        r"(?:[\u4e00-\u9fffA-Za-z0-9_-]{2,}(?:方案|套餐|版本|版))[：:\s]*(\d[\d,，]*(?:\s*[-~至]\s*\d[\d,，]*)?\s*元)",
        r"([^。；;\n，,]*?\d[\d,，]*(?:\s*[-~至]\s*\d[\d,，]*)?\s*元[^。；;\n，,]*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, compact)
        if match:
            return match.group(1).strip(" ：:，,。")
    return ""


def _extract_wechat_support(content: str) -> str:
    compact = _clean_context_content(content)
    match = re.search(r"(?:企业微信|企微|微信客服|微信)[^。；;\n，,]{0,20}(支持|可支持|可以|已支持|不支持)", compact)
    if match:
        return match.group(1)
    if _contains_any(compact, ["企业微信", "企微", "微信客服", "微信"]) and "支持" in compact:
        return "支持"
    return ""


def _extract_delivery_cycle(content: str) -> str:
    compact = _clean_context_content(content)
    patterns = [
        r"(?:交付周期|上线周期|周期|交付|上线)[：:\s]*(?:为|是)?\s*([^。；;\n，,]+?(?:工作日|天|周|个月))",
        r"(\d+\s*[-~至]\s*\d+\s*个?工作日)",
        r"(\d+\s*[-~至]\s*\d+\s*天)",
    ]
    for pattern in patterns:
        match = re.search(pattern, compact)
        if match:
            return match.group(1).strip(" ：:，,。")
    return ""


def _explicit_facts(items: list[dict[str, str]], question: str) -> dict[str, str]:
    terms = _specific_terms_from_question(question)
    prioritized = _prioritized_items(items, question)
    if terms:
        prioritized = [item for item in prioritized if _item_matches_terms(item, terms)]

    facts = {"price": "", "wechat": "", "delivery": ""}
    for item in prioritized:
        content = item.get("content", "")
        if not facts["price"]:
            facts["price"] = _extract_price(content)
        if not facts["wechat"]:
            facts["wechat"] = _extract_wechat_support(content)
        if not facts["delivery"]:
            facts["delivery"] = _extract_delivery_cycle(content)
        if all(facts.values()):
            break
    return facts


def _mock_answer(prompt: str) -> str:
    context_marker = "知识库内容："
    question_marker = "客户问题："
    context = ""
    question = ""
    if context_marker in prompt and question_marker in prompt:
        context = prompt.split(context_marker, 1)[1].split(question_marker, 1)[0].strip()
        question = prompt.split(question_marker, 1)[1].split("请生成", 1)[0].strip()

    company = _parse_company_context(prompt)
    company_name = company["company_name"]
    service_name = company["customer_service_name"]
    business_scope = company["business_scope"]

    if not context:
        return "目前资料中没有相关信息"

    items = _parse_context_items(context)
    items = _prioritized_items(items, question)
    summary = _summarize_items(items)
    if not summary:
        return "目前资料中没有相关信息。您也可以补充业务场景、使用渠道或想解决的问题，我再帮您判断。"

    guidance = "您可以补充行业、使用渠道、预算和期望上线时间，我可以进一步帮您判断适合的方案。"
    question_lower = question.lower()
    subject = _question_subject(question_lower)
    facts = _explicit_facts(items, question_lower)

    if _is_general_intro(question_lower):
        return _finish(
            f"{company_name}主要提供{business_scope}。我是{service_name}，可以先根据企业资料回答常见问题，并在需求明确或资料不足时引导人工跟进。"
            "您可以告诉我行业、接入渠道或当前客服痛点，我帮您判断适合方案。"
        )

    if _contains_any(question_lower, ["价格", "报价", "多少钱", "费用", "套餐", "收费", "预算"]):
        if facts["price"]:
            extra = []
            if facts["wechat"]:
                extra.append(f"企业微信接入：{facts['wechat']}")
            if facts["delivery"]:
                extra.append(f"交付周期：{facts['delivery']}")
            extra_text = f" 同一份资料还显示，{'；'.join(extra)}。" if extra else ""
            return _finish(f"{subject}价格是 {facts['price']}。{extra_text}{guidance}")
        return _finish(
            f"可以的，根据现有资料：{_summarize_items(items, limit=2)}。具体报价还要结合知识库规模、接入渠道、私有化和维护需求评估。"
            "您可以补充行业、渠道和预算，我帮您判断适合版本。"
        )

    if _contains_any(question_lower, ["私有化", "私有部署", "本地部署", "内网"]):
        return _finish(f"私有化部署可以评估。{_summarize_items(items, limit=2)}。这类需求建议补充服务器环境、数据安全要求和是否需要内网模型。")

    if _contains_any(question_lower, ["多久", "上线", "交付", "部署", "周期", "几天"]):
        if facts["delivery"]:
            return _finish(f"{subject}交付周期是 {facts['delivery']}。如果您能补充接入渠道、资料规模和期望上线时间，我可以继续帮您判断实施优先级。")
        return _finish(f"上线周期主要取决于版本和定制范围。{_summarize_items(items, limit=2)}。如果您告诉我希望接入的渠道和资料规模，我可以帮您预估更贴近的交付时间。")

    if _contains_any(question_lower, ["企微", "企业微信", "微信客服", "微信"]):
        if facts["wechat"]:
            label = "企业微信接入" if subject in {"企业微信", "企微", "微信客服"} else f"{subject}企业微信接入"
            return _finish(f"{label}：{facts['wechat']}。如果您已有企业微信客服流程，可以继续补充接待场景和线索流转方式，我帮您判断接入方案。")
        return _finish(f"企业微信方向可以评估接入。{_summarize_items(items, limit=2)}。建议您补充当前是否已有企业微信客服流程，以及希望 AI 负责接待还是辅助销售跟进。")

    if _contains_any(question_lower, ["飞书"]):
        return _finish(f"飞书接入可以作为高级版或定制能力评估。{_summarize_items(items, limit=2)}。您可以说明是需要飞书机器人、线索通知，还是内部客服协作流程。")

    if _contains_any(question_lower, ["网页", "网站", "官网", "在线客服", "h5"]):
        return _finish(f"网页客服入口适合做公开咨询和官网留资。{_summarize_items(items, limit=2)}。如果您已有官网，可以进一步确认入口样式、表单字段和线索跟进方式。")

    if _contains_any(question_lower, ["excel", "pdf", "word", "导入", "文档", "知识库"]):
        return _finish(f"知识库导入可以按资料形态来设计。{_summarize_items(items, limit=2)}。您可以先整理现有 FAQ、报价说明和产品资料，我再帮您判断适合手动维护还是批量导入。")

    if _contains_any(question_lower, ["行业", "教育", "培训", "电商", "制造业", "本地生活", "企业服务", "招商", "加盟"]):
        return _finish(f"适合的，关键看您的咨询是否高频且需要销售跟进。{_summarize_items(items, limit=2)}。您可以补充行业、客户常问问题和当前接待方式，我帮您判断落地优先级。")

    if _contains_any(question_lower, ["售后", "维护", "使用培训", "迭代", "后续"]):
        return _finish(f"后续维护是可以安排的。{_summarize_items(items, limit=2)}。如果您有长期更新知识库或持续优化回复效果的需求，可以选择维护服务。")

    if _contains_any(question_lower, ["coze", "dify", "区别", "对比"]):
        return _finish(
            f"简单说，{company_name}当前方案更偏销售客服业务闭环。{_summarize_items(items, limit=1)}。"
            "如果您的目标是官网咨询、意向识别、对话记录和线索跟进，这个项目会更贴近销售场景。"
        )

    return _finish(f"可以，我先根据现有资料给您一个简要说明：{_summarize_items(items, limit=2)}。{guidance}")


def _env_config() -> RuntimeAIConfig:
    provider = os.getenv("AI_PROVIDER", "deepseek")
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", os.getenv("AI_API_KEY", ""))
        base_url = os.getenv("OPENAI_BASE_URL", os.getenv("AI_BASE_URL", "https://api.openai.com/v1"))
        model = os.getenv("OPENAI_MODEL", os.getenv("AI_MODEL", "gpt-4o-mini"))
    elif provider == "qwen":
        api_key = os.getenv("QWEN_API_KEY", os.getenv("AI_API_KEY", ""))
        base_url = os.getenv(
            "QWEN_BASE_URL",
            os.getenv("AI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        )
        model = os.getenv("QWEN_MODEL", os.getenv("AI_MODEL", "qwen-plus"))
    elif provider == "zhipu":
        api_key = os.getenv("ZHIPU_API_KEY", os.getenv("AI_API_KEY", ""))
        base_url = os.getenv(
            "ZHIPU_BASE_URL",
            os.getenv("AI_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
        )
        model = os.getenv("ZHIPU_MODEL", os.getenv("AI_MODEL", "glm-4-flash"))
    elif provider == "ollama":
        api_key = os.getenv("OLLAMA_API_KEY", os.getenv("AI_API_KEY", ""))
        base_url = os.getenv("OLLAMA_BASE_URL", os.getenv("AI_BASE_URL", "http://localhost:11434/v1"))
        model = os.getenv("OLLAMA_MODEL", os.getenv("AI_MODEL", "qwen2.5:7b"))
    elif provider == "volcengine_ark":
        api_key = os.getenv("VOLCENGINE_ARK_API_KEY", os.getenv("AI_API_KEY", ""))
        base_url = os.getenv("VOLCENGINE_ARK_BASE_URL", os.getenv("AI_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"))
        model = os.getenv("VOLCENGINE_ARK_MODEL", os.getenv("AI_MODEL", ""))
    else:
        api_key = os.getenv("DEEPSEEK_API_KEY", os.getenv("AI_API_KEY", ""))
        base_url = os.getenv("DEEPSEEK_BASE_URL", os.getenv("AI_BASE_URL", "https://api.deepseek.com"))
        model = os.getenv("DEEPSEEK_MODEL", os.getenv("AI_MODEL", "deepseek-chat"))

    return RuntimeAIConfig(
        provider=provider,
        name="环境变量配置",
        api_key=api_key,
        base_url=base_url,
        model=model,
    )


def _db_default_config(db: Session | None) -> RuntimeAIConfig | None:
    if db is None:
        return None

    config = (
        db.query(AIModelConfig)
        .filter(AIModelConfig.is_default.is_(True), AIModelConfig.enabled.is_(True))
        .first()
    )
    if not config:
        return None

    return RuntimeAIConfig(
        provider=config.provider,
        name=config.name,
        api_key=config.api_key or "",
        base_url=config.base_url,
        model=config.model,
        enabled=config.enabled,
    )


def _coerce_config(config: AIModelConfig | RuntimeAIConfig | dict[str, Any]) -> RuntimeAIConfig:
    if isinstance(config, RuntimeAIConfig):
        return config
    if isinstance(config, dict):
        return RuntimeAIConfig(
            provider=str(config.get("provider", "custom")),
            name=str(config.get("name", "测试配置")),
            api_key=str(config.get("api_key") or ""),
            base_url=str(config.get("base_url", "")),
            model=str(config.get("model", "")),
            enabled=bool(config.get("enabled", True)),
        )
    return RuntimeAIConfig(
        provider=config.provider,
        name=config.name,
        api_key=config.api_key or "",
        base_url=config.base_url,
        model=config.model,
        enabled=config.enabled,
    )


async def _chat_completion(prompt: str, config: RuntimeAIConfig, timeout: float = 20) -> str:
    if not config.enabled:
        raise ValueError("模型配置未启用")
    if not config.base_url or not config.model:
        raise ValueError("模型 Base URL 或 Model 为空")
    if config.provider != "ollama" and not config.api_key:
        raise ValueError("模型 API Key 未配置")

    headers = {"Content-Type": "application/json"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{config.base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json={
                "model": config.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise ValueError("模型返回为空或格式异常")
        return sanitize_answer(content)


def _friendly_model_error(exc: Exception) -> str:
    message = str(exc)
    if "API Key 未配置" in message:
        return "API Key 未配置，请填写当前平台的 API Key。Ollama 本地模型可留空。"
    if "Base URL 或 Model 为空" in message:
        return "Base URL 或 Model 未填写完整，请检查模型配置。"
    if "模型配置未启用" in message:
        return "模型配置未启用，请先启用后再测试连接。"

    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        if status_code == 401:
            return "鉴权失败，请检查 API Key 是否正确、是否带有多余引号/空格，以及该 Key 是否有权限调用当前模型或接入点。"
        if status_code == 403:
            return "无权限调用，请检查账号权限、模型权限、接入点权限或当前模型是否已开通。"
        if status_code == 404:
            return "接口或模型不存在，请检查 Base URL 是否正确，以及 Model 是否填写为正确的模型名或接入点 ID。"
        if status_code == 429:
            return "请求过于频繁或额度不足，请稍后重试，或检查平台额度和限流设置。"
        if status_code in {500, 502, 503, 504}:
            return "模型服务异常，请稍后重试，或检查模型平台服务状态。"
        return f"模型接口请求失败，HTTP 状态码：{status_code}。请检查 Base URL、模型名称和平台配置。"

    if isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.TimeoutException, httpx.NetworkError)):
        return "连接失败，请检查 Base URL、网络连接、代理配置或服务是否可访问。"

    if isinstance(exc, (KeyError, IndexError, TypeError, ValueError)):
        return "模型接口已响应，但返回格式不符合 OpenAI-Compatible Chat Completions 格式，请检查接口兼容性。"

    return "连接失败，请检查 Base URL、网络连接、代理配置或服务是否可访问。"


async def generate_answer(prompt: str, db: Session | None = None) -> str:
    result = await generate_answer_with_meta(prompt, db=db)
    return result.answer


async def generate_answer_with_meta(prompt: str, db: Session | None = None) -> AIAnswer:
    config = _db_default_config(db) or _env_config()
    if config.provider != "ollama" and not config.api_key:
        logger.info("AI API key is empty for provider=%s; using mock answer.", config.provider)
        return AIAnswer(
            answer=_mock_answer(prompt),
            ai_source="mock",
            provider=config.provider,
            model=config.model,
        )

    try:
        return AIAnswer(
            answer=await _chat_completion(prompt, config),
            ai_source="model",
            provider=config.provider,
            model=config.model,
        )
    except Exception as exc:
        logger.warning(
            "AI call failed; provider=%s model=%s base_url=%s error=%s. Falling back to mock answer.",
            config.provider,
            config.model,
            config.base_url,
            exc,
        )
        return AIAnswer(
            answer=_mock_answer(prompt),
            ai_source="mock",
            provider=config.provider,
            model=config.model,
        )


async def test_model_config(config: AIModelConfig | RuntimeAIConfig | dict[str, Any]) -> tuple[bool, str]:
    runtime_config = _coerce_config(config)
    try:
        content = await _chat_completion("请回复：连接成功", runtime_config, timeout=15)
        if not content:
            return False, "模型返回为空"
        return True, content
    except Exception as exc:
        logger.warning(
            "AI config test failed; provider=%s model=%s base_url=%s error=%s",
            runtime_config.provider,
            runtime_config.model,
            runtime_config.base_url,
            exc,
        )
        return False, _friendly_model_error(exc)
