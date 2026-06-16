import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import KnowledgeItem


@dataclass
class ScoredKnowledge:
    item: KnowledgeItem
    score: int


class KnowledgeRetriever:
    """Simple keyword retriever; replace this class with vector search later."""

    def retrieve(self, question: str, db: Session, limit: int = 3) -> list[KnowledgeItem]:
        normalized_question = question.strip().lower()
        if not normalized_question:
            return []

        items = db.query(KnowledgeItem).filter(KnowledgeItem.status == "active").all()
        scored: list[ScoredKnowledge] = []

        for item in items:
            score = self._score_item(normalized_question, item)
            if score > 0:
                scored.append(ScoredKnowledge(item=item, score=score))

        scored.sort(key=lambda entry: entry.score, reverse=True)
        return [entry.item for entry in scored[:limit]]

    def _score_item(self, question: str, item: KnowledgeItem) -> int:
        haystack = " ".join([item.title, item.category, item.keywords, item.content]).lower()
        score = 0

        if item.title.lower() in question:
            score += 6
        if item.category.lower() in question:
            score += 4

        for keyword in self._split_keywords(item.keywords):
            if keyword and keyword.lower() in question:
                score += 8

        for token in self._question_tokens(question):
            if token and token in haystack:
                score += 2

        return score

    @staticmethod
    def _split_keywords(keywords: str) -> list[str]:
        return [part.strip() for part in re.split(r"[,，、\s]+", keywords) if part.strip()]

    @staticmethod
    def _question_tokens(question: str) -> list[str]:
        tokens = re.split(r"[,，。！？\s]+", question)
        tokens.extend([question[index : index + 2] for index in range(max(len(question) - 1, 0))])
        return [token for token in tokens if len(token) >= 2]


retriever = KnowledgeRetriever()


def retrieve_knowledge(question: str, db: Session) -> list[KnowledgeItem]:
    return retriever.retrieve(question=question, db=db)


def build_context(items: list[KnowledgeItem]) -> str:
    return "\n\n".join(
        f"标题：{item.title}\n分类：{item.category}\n关键词：{item.keywords}\n内容：{item.content}"
        for item in items
    )
