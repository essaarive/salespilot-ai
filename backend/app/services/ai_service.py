import os

import httpx
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


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


async def generate_answer(prompt: str) -> str:
    if not DEEPSEEK_API_KEY:
        return _mock_answer(prompt)

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": DEEPSEEK_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return _mock_answer(prompt)
