from app.database import SessionLocal, init_db
from app.models import AIModelConfig, KnowledgeItem, User


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
    {
        "title": "套餐选择建议",
        "category": "价格套餐",
        "keywords": "价格, 报价, 多少钱, 费用, 套餐, 收费, 预算, 版本",
        "content": "如果只是做 FAQ 和产品介绍，通常建议从基础版开始；如果需要销售留资、意向识别和后台管理，建议选择标准版；如果涉及多渠道、私有化或复杂流程，建议评估高级版。",
        "status": "active",
    },
    {
        "title": "报价评估维度",
        "category": "价格套餐",
        "keywords": "报价, 费用, 多少钱, 价格, 评估, 预算, 需求",
        "content": "具体报价通常会根据知识库规模、接入渠道数量、是否需要私有化部署、是否需要定制流程和售后维护周期综合评估。",
        "status": "active",
    },
    {
        "title": "渠道接入能力",
        "category": "渠道接入",
        "keywords": "渠道, 接入, 多渠道, 企业微信, 企微, 飞书, 网页客服, 微信客服",
        "content": "系统可根据客户需求对接网页客服、企业微信、飞书等渠道，高级版支持多渠道统一接待、咨询记录保存和销售线索沉淀。",
        "status": "active",
    },
    {
        "title": "企业微信接入",
        "category": "企业微信",
        "keywords": "企业微信, 企微, 微信客服, 微信, 客服, 接入, 渠道",
        "content": "企业微信接入通常适合已经使用企微承接客户咨询的团队，可将 AI 客服能力接入企微客服或相关工作流，具体方式需要根据企业微信账号和现有流程评估。",
        "status": "active",
    },
    {
        "title": "飞书接入",
        "category": "飞书",
        "keywords": "飞书, 飞书机器人, 飞书客服, 接入, 渠道, 多渠道",
        "content": "飞书接入适合内部销售或客服团队在飞书中接收咨询提醒、线索通知和对话摘要，高级版可根据业务流程定制飞书机器人或消息推送。",
        "status": "active",
    },
    {
        "title": "网页客服入口",
        "category": "网页客服",
        "keywords": "网页客服, 官网, 网站, 在线客服, H5, 咨询入口, 嵌入",
        "content": "网页客服入口适合放在官网、落地页或产品介绍页中，客户无需登录即可提交咨询，系统会自动回复、记录对话并识别高意向线索。",
        "status": "active",
    },
    {
        "title": "知识库导入方式",
        "category": "知识库导入",
        "keywords": "知识库, 导入, Excel, PDF, Word, 文档, 批量导入, FAQ, 资料",
        "content": "第一版支持在后台手动维护知识库内容；如需 Excel、PDF、Word 或批量导入，可作为标准版或高级版的定制能力评估。",
        "status": "active",
    },
    {
        "title": "知识库更新维护",
        "category": "知识库导入",
        "keywords": "知识库, 更新, 维护, 修改, 迭代, FAQ, 资料",
        "content": "知识库可以根据产品价格、服务政策和常见问题持续更新。交付后可由企业自行维护，也可以购买长期维护服务协助更新内容。",
        "status": "active",
    },
    {
        "title": "数据安全说明",
        "category": "数据安全",
        "keywords": "数据安全, 安全, 隐私, 数据, 客户信息, API Key, 权限",
        "content": "MVP Demo 使用 SQLite 保存知识库、对话和线索。生产环境建议增加 JWT、权限控制、API Key 加密存储、访问日志、数据备份和敏感信息脱敏。",
        "status": "active",
    },
    {
        "title": "私有化部署",
        "category": "私有化部署",
        "keywords": "私有化, 私有部署, 本地部署, 内网, Docker, 服务器, 部署",
        "content": "高级版可评估私有化部署，将系统部署到企业自有服务器或内网环境中，适合对数据安全、网络环境和系统集成有更高要求的客户。",
        "status": "active",
    },
    {
        "title": "售后维护范围",
        "category": "售后维护",
        "keywords": "售后, 维护, 培训, 修改, 迭代, 支持, 后续维护",
        "content": "交付后通常包含基础使用培训、问题排查和一定周期的售后支持。长期维护可覆盖知识库更新、提示词优化、模型配置调整和小功能迭代。",
        "status": "active",
    },
    {
        "title": "人工接管机制",
        "category": "人工接管",
        "keywords": "人工接管, 转人工, 人工客服, 销售跟进, 高意向, 留资",
        "content": "当客户表现出报价、购买、合作、上线等高意向时，系统会自动沉淀线索，销售人员可在后台查看联系方式、需求和对话记录后人工跟进。",
        "status": "active",
    },
    {
        "title": "电商行业场景",
        "category": "适用行业",
        "keywords": "电商, 店铺, 商品, 售前, 客服, 订单, 行业",
        "content": "电商行业可用于商品介绍、活动规则、发货说明、售前问题和高意向客户留资，适合咨询量较高但问题重复度较高的店铺或品牌。",
        "status": "active",
    },
    {
        "title": "教育培训行业场景",
        "category": "适用行业",
        "keywords": "教育, 培训, 课程, 学员, 报名, 咨询, 行业",
        "content": "教育培训行业可用于课程介绍、价格区间、适合人群、开课时间和报名咨询，帮助顾问筛选高意向学员并沉淀线索。",
        "status": "active",
    },
    {
        "title": "制造业报价场景",
        "category": "适用行业",
        "keywords": "制造业, 工厂, 报价, 采购, 交付, 定制, 行业",
        "content": "制造业可用 AI 客服收集采购需求、产品规格、数量、交付时间和联系方式，再由销售或工程人员进行正式报价和方案确认。",
        "status": "active",
    },
    {
        "title": "企业服务售前场景",
        "category": "适用行业",
        "keywords": "企业服务, SaaS, 软件, 售前, 咨询, 方案, 行业",
        "content": "企业服务类业务可用系统完成第一轮售前接待，解答功能、价格、部署、案例和售后问题，并识别值得销售优先跟进的客户。",
        "status": "active",
    },
    {
        "title": "和 Coze/Dify 的区别",
        "category": "和 Coze/Dify 区别",
        "keywords": "Coze, Dify, 区别, 对比, 智能体, 工作流, 业务系统",
        "content": "Coze 和 Dify 更偏通用智能体或 AI 应用搭建平台；SalesPilot AI 更聚焦销售客服业务闭环，内置知识库、意向识别、对话记录、线索沉淀和后台跟进流程。",
        "status": "active",
    },
    {
        "title": "客户案例：本地生活服务",
        "category": "客户案例",
        "keywords": "案例, 本地生活, 门店, 预约, 咨询, 客服",
        "content": "本地生活服务商可将门店服务、套餐价格、预约方式和售后说明配置到知识库，让客户先由 AI 接待，再把有预约或购买意向的客户沉淀给销售跟进。",
        "status": "active",
    },
    {
        "title": "客户案例：招商加盟",
        "category": "客户案例",
        "keywords": "案例, 招商, 加盟, 加盟费, 合作, 留资, 咨询",
        "content": "招商加盟场景中，AI 客服可先回答加盟预算、合作条件、区域政策和资料领取问题，并将留下联系方式或询问合作方式的客户标记为高意向线索。",
        "status": "active",
    },
    {
        "title": "异议处理：担心回答不准",
        "category": "常见异议处理",
        "keywords": "不准, 胡说, 幻觉, 回答错误, 异议, 准确率",
        "content": "系统会优先基于企业知识库内容回复，并在没有资料时提示资料不足。生产环境可通过知识库维护、提示词约束、人工复核和低置信度转人工降低错误回复风险。",
        "status": "active",
    },
    {
        "title": "异议处理：已经有人工客服",
        "category": "常见异议处理",
        "keywords": "人工客服, 已有客服, 替代人工, 效率, 异议",
        "content": "AI 客服并不是完全替代人工，而是先处理重复咨询、收集基础需求和筛选高意向客户，让人工客服和销售把时间集中在更有价值的跟进上。",
        "status": "active",
    },
    {
        "title": "异议处理：不知道适不适合",
        "category": "常见异议处理",
        "keywords": "适不适合, 不确定, 评估, 业务场景, 异议, 需求",
        "content": "如果暂时不确定是否适合，可以先用标准版 Demo 验证 3 类问题：客户最常问什么、是否需要留资、销售是否需要根据意向优先跟进。",
        "status": "active",
    },
]

SEED_AI_MODEL_CONFIGS = [
    {
        "provider": "deepseek",
        "name": "DeepSeek 默认配置",
        "api_key": "",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "enabled": True,
        "is_default": True,
    },
    {
        "provider": "openai",
        "name": "OpenAI 默认配置",
        "api_key": "",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "enabled": True,
        "is_default": False,
    },
    {
        "provider": "qwen",
        "name": "通义千问兼容模式",
        "api_key": "",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
        "enabled": True,
        "is_default": False,
    },
    {
        "provider": "zhipu",
        "name": "智谱 GLM 默认配置",
        "api_key": "",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash",
        "enabled": True,
        "is_default": False,
    },
    {
        "provider": "ollama",
        "name": "Ollama 本地模型",
        "api_key": "",
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5:7b",
        "enabled": True,
        "is_default": False,
    },
    {
        "provider": "volcengine_ark",
        "name": "火山方舟 DeepSeek",
        "api_key": "",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "ep-xxxx",
        "enabled": True,
        "is_default": False,
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

        for payload in SEED_AI_MODEL_CONFIGS:
            exists = db.query(AIModelConfig).filter(AIModelConfig.provider == payload["provider"]).first()
            if not exists:
                db.add(AIModelConfig(**payload))

        db.commit()
        print("Seed data initialized.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
