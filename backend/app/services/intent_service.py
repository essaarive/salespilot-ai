from dataclasses import dataclass


@dataclass(frozen=True)
class IntentResult:
    intent_type: str
    intent_level: str


HIGH_INTENT_WORDS = [
    "多少钱",
    "价格",
    "报价",
    "套餐",
    "怎么合作",
    "能不能做",
    "多久上线",
    "联系方式",
    "购买",
    "搭建",
]

GREETING_WORDS = ["你好", "您好", "在吗", "hello", "hi", "hey", "早上好", "下午好", "晚上好"]
AFTER_SALES_WORDS = ["售后", "故障", "维护", "修改", "迭代", "培训", "不会用", "使用问题"]
DELIVERY_WORDS = ["多久", "上线", "交付", "周期", "部署"]
COOPERATION_WORDS = ["合作", "能不能做", "搭建", "定制", "私有化"]
PRICING_WORDS = ["多少钱", "价格", "报价", "套餐", "费用", "收费", "购买"]
PRODUCT_WORDS = ["功能", "产品", "适合", "行业", "知识库", "客服", "系统"]


def is_greeting(question: str) -> bool:
    normalized = (
        question.strip()
        .lower()
        .replace(" ", "")
        .replace("，", "")
        .replace(",", "")
        .replace("。", "")
        .replace("！", "")
        .replace("!", "")
        .replace("？", "")
        .replace("?", "")
        .replace("~", "")
    )
    return normalized in GREETING_WORDS


def detect_intent(question: str, has_related_knowledge: bool) -> IntentResult:
    text = question.strip()

    if any(word in text for word in AFTER_SALES_WORDS):
        level = "medium" if has_related_knowledge else "low"
        return IntentResult(intent_type="after_sales", intent_level=level)

    if any(word in text for word in PRICING_WORDS):
        return IntentResult(intent_type="pricing", intent_level="high")

    if any(word in text for word in COOPERATION_WORDS):
        return IntentResult(intent_type="cooperation", intent_level="high")

    if any(word in text for word in DELIVERY_WORDS):
        return IntentResult(intent_type="delivery", intent_level="high")

    if any(word in text for word in PRODUCT_WORDS):
        return IntentResult(intent_type="product", intent_level="medium" if has_related_knowledge else "low")

    if any(word in text for word in HIGH_INTENT_WORDS):
        return IntentResult(intent_type="product", intent_level="high")

    if is_greeting(text):
        return IntentResult(intent_type="greeting", intent_level="low")

    if not has_related_knowledge:
        return IntentResult(intent_type="irrelevant", intent_level="low")

    return IntentResult(intent_type="product", intent_level="medium")
