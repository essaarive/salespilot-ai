import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import KnowledgeItem


@dataclass
class ScoredKnowledge:
    item: KnowledgeItem
    score: int


SYNONYM_GROUPS = [
    {"价格", "报价", "多少钱", "费用", "套餐", "收费", "预算", "版本"},
    {"上线", "交付", "部署", "多久", "几天", "周期"},
    {"企业微信", "企微", "微信客服", "微信", "渠道接入", "接入"},
    {"飞书", "飞书机器人", "飞书客服", "渠道接入", "接入"},
    {"网页客服", "官网", "网站", "在线客服", "咨询入口", "嵌入"},
    {"知识库", "导入", "Excel", "PDF", "Word", "文档", "批量导入", "资料"},
    {"私有化", "私有部署", "本地部署", "内网", "Docker", "服务器"},
    {"售后", "维护", "使用培训", "修改", "迭代", "后续维护"},
    {"人工接管", "转人工", "人工客服", "销售跟进", "留资"},
    {"行业", "电商", "教育", "培训", "制造业", "本地生活", "企业服务", "招商加盟"},
    {"Coze", "Dify", "区别", "对比", "智能体", "工作流"},
    {"案例", "客户案例", "门店", "招商", "加盟"},
    {"不准", "幻觉", "回答错误", "准确率", "异议"},
    {"介绍", "介绍一下", "了解一下", "你们是做什么", "产品", "系统", "功能", "客服"},
]

STOP_TOKENS = {
    "可以",
    "支持",
    "我们",
    "你们",
    "这个",
    "那个",
    "什么",
    "怎么",
    "是否",
    "有没有",
    "吗",
    "呢",
    "啊",
}

SPECIFIC_INTENT_WORDS = [
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
]

SPECIFIC_BUSINESS_TERMS = {
    "常规",
    "基础咨询方案",
    "基础方案",
    "咨询方案",
    "企业微信",
    "企微",
    "微信客服",
}


class KnowledgeRetriever:
    """Simple keyword retriever; replace this class with vector search later."""

    def retrieve(self, question: str, db: Session, limit: int = 5) -> list[KnowledgeItem]:
        normalized_question = question.strip().lower()
        if not normalized_question:
            return []

        terms = self._expanded_terms(normalized_question)
        items = db.query(KnowledgeItem).filter(KnowledgeItem.status == "active").all()
        scored: list[ScoredKnowledge] = []

        for item in items:
            score = self._score_item(normalized_question, terms, item)
            if score >= 4:
                scored.append(ScoredKnowledge(item=item, score=score))

        scored.sort(key=lambda entry: entry.score, reverse=True)
        return [entry.item for entry in scored[:limit]]

    def _score_item(self, question: str, terms: set[str], item: KnowledgeItem) -> int:
        haystack = " ".join([item.title, item.category, item.keywords, item.content]).lower()
        score = 0
        specific_terms = self._specific_terms(question)
        is_document = getattr(item, "source_type", "manual") == "document"

        if item.title.lower() in question:
            score += 10
        if item.category.lower() in question:
            score += 7

        for term in specific_terms:
            if term in haystack:
                score += 28
                if is_document:
                    score += 90

        for keyword in self._split_keywords(item.keywords):
            keyword = keyword.lower()
            if keyword and keyword in question:
                score += 12
            elif keyword and keyword in terms:
                score += 8

        for term in terms:
            if term in haystack:
                score += 4

        for token in self._question_tokens(question):
            if token and token in haystack:
                score += 2

        return score

    @staticmethod
    def _expanded_terms(question: str) -> set[str]:
        terms = set(KnowledgeRetriever._question_tokens(question))
        terms.add(question)

        for group in SYNONYM_GROUPS:
            normalized_group = {term.lower() for term in group}
            if any(term in question for term in normalized_group):
                terms.update(normalized_group)

        return {term for term in terms if term and term not in STOP_TOKENS}

    @staticmethod
    def _split_keywords(keywords: str) -> list[str]:
        return [part.strip() for part in re.split(r"[,，、\s]+", keywords) if part.strip()]

    @staticmethod
    def _question_tokens(question: str) -> list[str]:
        tokens = [part.strip() for part in re.split(r"[,，。！？、/\s]+", question) if part.strip()]
        tokens.extend([question[index : index + 2] for index in range(max(len(question) - 1, 0))])
        return [token for token in tokens if len(token) >= 2 and token not in STOP_TOKENS]

    @staticmethod
    def _specific_terms(question: str) -> set[str]:
        """Extract product/model-like terms so uploaded docs can beat generic seeds."""
        normalized = re.sub(r"[？?！!。，、\s]+", "", question.lower())
        terms = set(
            match.group(1)
            for match in re.finditer(r"([\u4e00-\u9fffA-Za-z0-9_-]{2,}?(?:版|型号|产品|方案|套餐))", normalized)
        )
        terms.update(term for term in SPECIFIC_BUSINESS_TERMS if term in normalized)

        cleaned = normalized
        for word in SPECIFIC_INTENT_WORDS:
            cleaned = cleaned.replace(word.lower(), "")
        cleaned = cleaned.strip()
        if (len(cleaned) >= 3 or cleaned in SPECIFIC_BUSINESS_TERMS) and cleaned not in STOP_TOKENS:
            terms.add(cleaned)

        return {
            term
            for term in terms
            if (len(term) >= 3 or term in SPECIFIC_BUSINESS_TERMS) and term not in STOP_TOKENS
        }


retriever = KnowledgeRetriever()


def retrieve_knowledge(question: str, db: Session) -> list[KnowledgeItem]:
    return retriever.retrieve(question=question, db=db)


def build_context(items: list[KnowledgeItem]) -> str:
    return "\n\n".join(
        "\n".join(
            [
                f"标题：{item.title}",
                f"分类：{item.category}",
                f"关键词：{item.keywords}",
                f"来源类型：{getattr(item, 'source_type', 'manual')}",
                f"来源文件：{getattr(item, 'source_file_name', '') or ''}",
                f"内容：{item.content}",
            ]
        )
        for item in items
    )
