import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import Document, KnowledgeItem


@dataclass
class ScoredKnowledge:
    item: KnowledgeItem
    score: int
    strong_match: bool = False
    explicit_fact_match: bool = False


@dataclass(frozen=True)
class RetrievalResult:
    items: list[KnowledgeItem]
    top_score: int
    retrieval_confidence: str
    has_reliable_knowledge: bool
    scored_items: list[ScoredKnowledge]


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
    "吗",
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

EXPLICIT_FACT_WORDS = {
    "价格",
    "报价",
    "费用",
    "收费",
    "元",
    "交付周期",
    "上线周期",
    "工作日",
    "企业微信接入",
    "支持",
    "不支持",
    "私有化",
    "售后",
}


class KnowledgeRetriever:
    """Simple keyword retriever; replace this class with vector search later."""

    def retrieve(self, question: str, db: Session, limit: int = 5) -> list[KnowledgeItem]:
        return self.retrieve_with_meta(question=question, db=db, limit=limit).items

    def retrieve_with_meta(self, question: str, db: Session, limit: int = 5) -> RetrievalResult:
        normalized_question = question.strip().lower()
        if not normalized_question:
            return RetrievalResult(
                items=[],
                top_score=0,
                retrieval_confidence="none",
                has_reliable_knowledge=False,
                scored_items=[],
            )

        terms = self._expanded_terms(normalized_question)
        disabled_document_ids = {
            document_id
            for (document_id,) in db.query(Document.id)
            .filter(Document.is_enabled.is_(False))
            .all()
        }
        items = db.query(KnowledgeItem).filter(KnowledgeItem.status == "active").all()
        scored: list[ScoredKnowledge] = []

        for item in items:
            if (
                getattr(item, "source_type", "manual") == "document"
                and item.source_document_id in disabled_document_ids
            ):
                continue
            scored_item = self._score_item(normalized_question, terms, item)
            score = scored_item.score
            if score >= 4:
                scored.append(scored_item)

        scored.sort(key=lambda entry: entry.score, reverse=True)
        selected = scored[:limit]
        confidence = self._classify_confidence(selected)
        return RetrievalResult(
            items=[entry.item for entry in selected],
            top_score=selected[0].score if selected else 0,
            retrieval_confidence=confidence,
            has_reliable_knowledge=confidence in {"high", "medium"},
            scored_items=selected,
        )

    def _score_item(self, question: str, terms: set[str], item: KnowledgeItem) -> ScoredKnowledge:
        haystack = " ".join([item.title, item.category, item.keywords, item.content]).lower()
        compact_haystack = re.sub(r"\s+", "", haystack)
        score = 0
        specific_terms = self._specific_terms(question)
        is_document = getattr(item, "source_type", "manual") == "document"
        strong_match = False

        if item.title.lower() in question:
            score += 10
        if item.category.lower() in question:
            score += 7

        for term in specific_terms:
            if term in haystack or term in compact_haystack:
                strong_match = True
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

        explicit_fact_match = strong_match and self._has_explicit_fact(haystack)
        if explicit_fact_match:
            score += 18 if is_document else 8

        return ScoredKnowledge(
            item=item,
            score=score,
            strong_match=strong_match,
            explicit_fact_match=explicit_fact_match,
        )

    @staticmethod
    def _classify_confidence(scored: list[ScoredKnowledge]) -> str:
        if not scored:
            return "none"

        top = scored[0]
        if top.explicit_fact_match and top.score >= 42:
            return "high"
        if top.strong_match and getattr(top.item, "source_type", "manual") == "document" and top.score >= 40:
            return "high"
        if top.score >= 36 and (
            top.explicit_fact_match
            or any(word in top.item.content for word in EXPLICIT_FACT_WORDS)
        ):
            return "high"
        if top.score >= 22:
            return "medium"
        return "low"

    @staticmethod
    def _has_explicit_fact(haystack: str) -> bool:
        return any(word.lower() in haystack for word in EXPLICIT_FACT_WORDS)

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


def retrieve_knowledge_result(question: str, db: Session) -> RetrievalResult:
    return retriever.retrieve_with_meta(question=question, db=db)


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
