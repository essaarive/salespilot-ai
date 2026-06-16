from dataclasses import dataclass


@dataclass(frozen=True)
class IntentResult:
    intent_type: str
    intent_level: str


@dataclass(frozen=True)
class ScopeResult:
    scope_type: str


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
    "接入",
    "对接",
    "企微",
    "企业微信",
    "飞书",
    "私有化",
    "想做",
    "想接入",
    "怎么接入",
    "如何接入",
]

GREETING_WORDS = ["你好", "您好", "在吗", "hello", "hi", "hey", "早上好", "下午好", "晚上好"]
AFTER_SALES_WORDS = ["售后", "故障", "维护", "修改", "迭代", "使用培训", "不会用", "使用问题"]
DELIVERY_WORDS = ["多久", "上线", "交付", "周期", "部署"]
COOPERATION_WORDS = ["合作", "能不能做", "搭建", "定制", "私有化", "接入", "对接", "企微", "企业微信", "飞书"]
PRICING_WORDS = ["多少钱", "价格", "报价", "套餐", "费用", "收费", "购买"]
PRODUCT_WORDS = ["功能", "产品", "适合", "行业", "知识库", "客服", "系统", "导入", "coze", "dify", "介绍", "了解一下", "做什么"]
BUSINESS_SCOPE_WORDS = [
    "ai客服",
    "ai 客服",
    "智能客服",
    "销售客服",
    "价格",
    "套餐",
    "报价",
    "费用",
    "交付",
    "上线",
    "接入",
    "企业微信",
    "企微",
    "飞书",
    "网页客服",
    "知识库",
    "私有化",
    "售后",
    "维护",
    "行业",
    "coze",
    "dify",
]
SALES_ADJACENT_WORDS = [
    "销售",
    "获客",
    "转化率",
    "转化",
    "客户跟进",
    "跟进",
    "客服效率",
    "私域",
    "crm",
    "线索",
    "留资",
    "客户咨询多",
]
GENERAL_CHAT_WORDS = [
    "人工智能",
    "ai是什么",
    "什么是ai",
    "你是谁",
    "你会写代码",
    "写代码",
    "今天吃什么",
    "吃什么",
    "天气",
    "讲个笑话",
]
UNSAFE_WORDS = [
    "诈骗",
    "钓鱼",
    "盗号",
    "木马",
    "攻击",
    "入侵",
    "窃取",
    "偷取",
    "绕过",
    "破解",
    "洗钱",
    "伪造",
    "隐私",
    "密码",
]
OUT_OF_SCOPE_WORDS = ["彩票", "算命", "星座", "八字", "炒股内幕", "博彩"]


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


def classify_scope(question: str, has_related_knowledge: bool) -> ScopeResult:
    text = question.strip().lower()

    if any(word in text for word in UNSAFE_WORDS):
        return ScopeResult(scope_type="unsafe")

    if any(word in text for word in BUSINESS_SCOPE_WORDS):
        return ScopeResult(scope_type="business_related")

    if any(word in text for word in SALES_ADJACENT_WORDS):
        return ScopeResult(scope_type="sales_adjacent")

    if is_greeting(text) or any(word in text for word in GENERAL_CHAT_WORDS):
        return ScopeResult(scope_type="general_chat")

    if any(word in text for word in OUT_OF_SCOPE_WORDS):
        return ScopeResult(scope_type="out_of_scope")

    if has_related_knowledge:
        return ScopeResult(scope_type="business_related")

    return ScopeResult(scope_type="general_chat")


def detect_intent(question: str, has_related_knowledge: bool, scope_type: str | None = None) -> IntentResult:
    text = question.strip()

    if scope_type in {"unsafe", "out_of_scope", "general_chat"}:
        if is_greeting(text):
            return IntentResult(intent_type="greeting", intent_level="low")
        return IntentResult(intent_type="irrelevant", intent_level="low")

    if scope_type == "sales_adjacent":
        if any(word in text for word in HIGH_INTENT_WORDS):
            return IntentResult(intent_type="product", intent_level="high")
        return IntentResult(intent_type="product", intent_level="medium")

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
