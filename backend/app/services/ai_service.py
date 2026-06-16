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
    for block in [part.strip() for part in context.split("\n\n") if part.strip()]:
        item = {"title": "", "category": "", "content": ""}
        for line in block.splitlines():
            if line.startswith("标题："):
                item["title"] = line.replace("标题：", "", 1).strip()
            elif line.startswith("分类："):
                item["category"] = line.replace("分类：", "", 1).strip()
            elif line.startswith("内容："):
                item["content"] = line.replace("内容：", "", 1).strip()
        if item["content"]:
            items.append(item)
    return items


def _summarize_items(items: list[dict[str, str]], limit: int = 3) -> str:
    contents = []
    for item in items[:limit]:
        content = item["content"].rstrip("。")
        if content and content not in contents:
            contents.append(content)
    return "；".join(contents)


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


def _mock_answer(prompt: str) -> str:
    context_marker = "知识库内容："
    question_marker = "客户问题："
    context = ""
    question = ""
    if context_marker in prompt and question_marker in prompt:
        context = prompt.split(context_marker, 1)[1].split(question_marker, 1)[0].strip()
        question = prompt.split(question_marker, 1)[1].split("请生成", 1)[0].strip()

    if not context:
        return "目前资料中没有相关信息"

    items = _parse_context_items(context)
    summary = _summarize_items(items)
    if not summary:
        return "目前资料中没有相关信息。您也可以补充业务场景、使用渠道或想解决的问题，我再帮您判断。"

    guidance = "您可以补充行业、使用渠道、预算和期望上线时间，我可以进一步帮您判断适合的方案。"
    question_lower = question.lower()

    if _is_general_intro(question_lower):
        return _finish(
            "SalesPilot AI 是面向中小企业的 AI 销售客服系统，主要用于官网咨询接待、企业知识库问答、客户意向识别和高意向线索沉淀。"
            "它适合先帮销售完成第一轮接待，再把值得跟进的客户交给人工。您可以告诉我行业、接入渠道或当前客服痛点，我帮您判断适合方案。"
        )

    if _contains_any(question_lower, ["价格", "报价", "多少钱", "费用", "套餐", "收费", "预算"]):
        return _finish(
            "可以的，基础版约 800-3000 元，标准版约 3000-8000 元，高级版约 8000-20000 元。"
            "具体会根据知识库规模、接入渠道、私有化和维护需求评估。您可以补充行业、渠道和预算，我帮您判断适合版本。"
        )

    if _contains_any(question_lower, ["私有化", "私有部署", "本地部署", "内网"]):
        return _finish(f"私有化部署可以评估。{_summarize_items(items, limit=2)}。这类需求建议补充服务器环境、数据安全要求和是否需要内网模型。")

    if _contains_any(question_lower, ["多久", "上线", "交付", "部署", "周期", "几天"]):
        return _finish(f"上线周期主要取决于版本和定制范围。{_summarize_items(items, limit=2)}。如果您告诉我希望接入的渠道和资料规模，我可以帮您预估更贴近的交付时间。")

    if _contains_any(question_lower, ["企微", "企业微信", "微信客服", "微信"]):
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
            f"简单说，SalesPilot AI 更偏销售客服业务闭环。{_summarize_items(items, limit=1)}。"
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
