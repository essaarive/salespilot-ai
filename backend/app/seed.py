from app.database import SessionLocal, init_db
from app.models import KnowledgeItem, User


SEED_KNOWLEDGE = [
    {
        "title": "AI 客服基础版",
        "category": "价格",
        "keywords": "价格, 多少钱, 基础版, FAQ, 问答",
        "content": "基础版价格为 800-3000 元，适合简单 FAQ 问答、产品介绍、基础客服回复等场景。",
        "status": "active",
    },
    {
        "title": "AI 客服标准版",
        "category": "价格",
        "keywords": "标准版, 知识库, 销售留资, 报价",
        "content": "标准版价格为 3000-8000 元，适合企业知识库问答、销售线索收集、客户意向识别、后台管理等场景。",
        "status": "active",
    },
    {
        "title": "AI 客服高级版",
        "category": "价格",
        "keywords": "高级版, 私有化, 多渠道, 企业微信, 飞书",
        "content": "高级版价格为 8000-20000 元，适合多渠道接入、企业微信或飞书集成、私有化部署、复杂业务流程自动化等场景。",
        "status": "active",
    },
    {
        "title": "交付周期",
        "category": "交付",
        "keywords": "多久上线, 交付, 周期, 部署",
        "content": "基础版通常 3-5 天可交付，标准版通常 1-2 周可交付，高级定制版需要根据需求评估，一般为 2-4 周。",
        "status": "active",
    },
    {
        "title": "售后服务",
        "category": "售后",
        "keywords": "售后, 维护, 修改, 迭代, 培训",
        "content": "项目交付后提供基础使用培训和一定周期的售后支持，可根据客户需求提供长期维护、知识库更新和功能迭代服务。",
        "status": "active",
    },
    {
        "title": "适用行业",
        "category": "行业",
        "keywords": "行业, 电商, 教育, 制造业, 本地生活, 企业服务",
        "content": "系统适用于电商、教育培训、本地生活、制造业、企业服务、招商加盟等需要客服接待和销售咨询的行业。",
        "status": "active",
    },
]


def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(username="admin", password_hash="admin123", role="admin"))

        for payload in SEED_KNOWLEDGE:
            exists = db.query(KnowledgeItem).filter(KnowledgeItem.title == payload["title"]).first()
            if not exists:
                db.add(KnowledgeItem(**payload))

        db.commit()
        print("Seed data initialized.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
