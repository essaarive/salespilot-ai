import os
import logging
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


def _mock_answer(prompt: str) -> str:
    if "目前资料中没有相关信息" in prompt and "知识库内容：\n\n客户问题" in prompt:
        return "目前资料中没有相关信息"

    context_marker = "知识库内容："
    question_marker = "客户问题："
    context = ""
    question = ""
    if context_marker in prompt and question_marker in prompt:
        context = prompt.split(context_marker, 1)[1].split(question_marker, 1)[0].strip()
        question = prompt.split(question_marker, 1)[1].split("请生成", 1)[0].strip()

    if not context:
        return "目前资料中没有相关信息"

    guidance = ""
    if any(word in question for word in ["购买", "报价", "价格", "多少钱", "合作", "搭建"]):
        guidance = " 如果方便的话，您可以补充行业、接入渠道和预计咨询量，我可以进一步帮您判断适合的方案。"

    first_content = ""
    for line in context.splitlines():
        if line.startswith("内容："):
            first_content = line.replace("内容：", "", 1)
            break

    return f"根据现有资料，{first_content or '可以结合您的业务场景提供 AI 销售客服方案。'}{guidance}"


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
        return data["choices"][0]["message"]["content"].strip()


async def generate_answer(prompt: str, db: Session | None = None) -> str:
    config = _db_default_config(db) or _env_config()
    if config.provider != "ollama" and not config.api_key:
        logger.info("AI API key is empty for provider=%s; using mock answer.", config.provider)
        return _mock_answer(prompt)

    try:
        return await _chat_completion(prompt, config)
    except Exception as exc:
        logger.warning(
            "AI call failed; provider=%s model=%s base_url=%s error=%s. Falling back to mock answer.",
            config.provider,
            config.model,
            config.base_url,
            exc,
        )
        return _mock_answer(prompt)


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
        return False, str(exc)
