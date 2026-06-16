import { ArrowRight, Bot, BrainCircuit, CheckCircle2, Database, LineChart, LockKeyhole, MessagesSquare, Route, UsersRound, Zap } from "lucide-react";
import { Link } from "react-router-dom";

const features = [
  {
    icon: Database,
    title: "企业知识库问答",
    description: "将产品介绍、报价说明、交付周期、售后规则等资料维护到知识库，AI 回复时优先基于企业资料生成答案。",
  },
  {
    icon: BrainCircuit,
    title: "客户意向识别",
    description: "自动识别询价、合作、交付、售后、问候、无关问题等不同咨询类型，并判断 high / medium / low 意向等级。",
  },
  {
    icon: UsersRound,
    title: "高意向线索沉淀",
    description: "当客户咨询价格、合作、上线周期等强需求问题时，系统会自动生成客户线索，方便销售后续跟进。",
  },
  {
    icon: Zap,
    title: "多模型 API 接入",
    description: "后台可配置 DeepSeek、OpenAI、通义千问、智谱 GLM、Ollama、火山方舟或自定义 OpenAI-Compatible API。",
  },
];

const workflow = [
  ["企业维护知识库", "录入产品、价格、交付、售后、行业方案等资料。"],
  ["客户提交咨询", "客户在官网或咨询入口填写问题和联系方式。"],
  ["AI 自动回复并识别意向", "系统检索知识库，生成回复，并判断客户意向等级。"],
  ["销售后台跟进线索", "高意向客户自动进入线索池，销售可在后台查看和跟进。"],
];

const scenarios = [
  ["电商客服", "快速回答售前咨询、物流规则和活动报价问题。"],
  ["教育培训咨询", "自动介绍课程体系、价格区间和报名流程。"],
  ["本地生活服务", "接待预约、门店服务、套餐和售后咨询。"],
  ["制造业报价咨询", "收集采购需求、数量、交付周期和联系方式。"],
  ["企业服务售前", "围绕方案、功能、部署和合作方式完成初筛。"],
  ["招商加盟咨询", "介绍加盟政策、预算范围和区域合作流程。"],
];

const plans = [
  {
    name: "基础版",
    price: "800-3000 元",
    fit: "简单 FAQ 问答、产品介绍、基础客服回复",
    points: ["知识库问答", "基础咨询接待", "本地 Demo 部署"],
  },
  {
    name: "标准版",
    price: "3000-8000 元",
    fit: "企业知识库问答、销售线索收集、客户意向识别、后台管理",
    points: ["知识库管理", "AI 回复生成", "意向识别", "线索沉淀", "对话记录"],
    highlight: true,
  },
  {
    name: "高级版",
    price: "8000-20000 元",
    fit: "多渠道接入、企业微信/飞书集成、私有化部署、复杂业务流程自动化",
    points: ["多模型 API 接入", "多渠道接入预留", "私有化部署", "定制业务流程", "长期维护支持"],
  },
];

const faqs = [
  ["没有 API Key 可以演示吗？", "可以。系统内置 mock fallback，本地未配置模型 API Key 时也能完整演示客户咨询、AI 回复、意向识别和线索沉淀流程。"],
  ["能接入不同模型吗？", "可以。后台支持 DeepSeek、OpenAI、通义千问、智谱 GLM、Ollama、火山方舟和自定义 OpenAI-Compatible API，并可以选择当前默认模型。"],
  ["客户咨询会保存吗？", "会。系统会保存对话记录；当客户被识别为高意向时，会自动沉淀为客户线索。"],
  ["这个项目可以直接生产上线吗？", "当前版本是 MVP Demo，适合作品展示和业务验证。生产环境建议补充 JWT、密码哈希、RBAC、API Key 加密存储、日志审计、限流等能力。"],
];

function SectionTitle({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div className="mx-auto mb-10 max-w-2xl text-center">
      <p className="text-sm font-semibold text-brand-600">{eyebrow}</p>
      <h2 className="mt-3 text-2xl font-semibold tracking-normal text-slate-950 md:text-3xl">{title}</h2>
    </div>
  );
}

export default function PublicHome() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <Link className="flex items-center gap-3" to="/">
            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600 text-white">
              <Bot size={21} />
            </span>
            <span>
              <span className="block text-base font-semibold text-slate-950">SalesPilot AI</span>
              <span className="block text-xs text-slate-500">智销助手</span>
            </span>
          </Link>
          <nav className="hidden items-center gap-6 text-sm text-slate-600 lg:flex">
            <a className="hover:text-brand-600" href="#features">产品能力</a>
            <a className="hover:text-brand-600" href="#workflow">使用流程</a>
            <a className="hover:text-brand-600" href="#scenarios">适用场景</a>
            <a className="hover:text-brand-600" href="#pricing">套餐方案</a>
            <a className="hover:text-brand-600" href="#faq">常见问题</a>
          </nav>
          <div className="flex items-center gap-2">
            <Link className="btn-primary px-3" to="/public-chat">免费咨询</Link>
            <Link className="btn-secondary px-3" to="/login">后台登录</Link>
          </div>
        </div>
      </header>

      <main>
        <section className="overflow-hidden bg-gradient-to-br from-white via-brand-50 to-cyan-50">
          <div className="mx-auto grid max-w-7xl items-center gap-10 px-4 py-16 sm:px-6 md:py-20 lg:grid-cols-[1fr_460px] lg:px-8">
            <div>
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-brand-100 bg-white px-3 py-1 text-sm font-medium text-brand-700 shadow-sm">
                <LineChart size={15} />
                AI 销售客服系统 MVP Demo
              </div>
              <h1 className="max-w-3xl text-4xl font-semibold leading-tight tracking-normal text-slate-950 md:text-5xl">
                让 AI 自动接待客户，沉淀高意向销售线索
              </h1>
              <p className="mt-6 max-w-2xl text-base leading-8 text-slate-600 md:text-lg">
                SalesPilot AI 帮助中小企业把产品资料、报价说明和 FAQ 接入 AI 客服流程，自动回复客户问题、识别购买意向，并将高意向客户沉淀到销售后台。
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link className="btn-primary px-5 py-3" to="/public-chat">
                  立即咨询
                  <ArrowRight size={17} />
                </Link>
                <Link className="btn-secondary px-5 py-3" to="/login">
                  查看后台演示
                  <LockKeyhole size={17} />
                </Link>
              </div>
            </div>

            <div className="rounded-2xl border border-white bg-white/85 p-5 shadow-soft">
              <div className="mb-4 flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                  <p className="text-sm font-semibold text-slate-950">公开咨询入口</p>
                  <p className="text-xs text-slate-500">自动回复 + 意向识别</p>
                </div>
                <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">在线</span>
              </div>
              <div className="space-y-4">
                <div className="ml-auto max-w-[86%] rounded-2xl rounded-tr-sm bg-brand-600 px-4 py-3 text-sm leading-6 text-white">
                  你们做 AI 客服多少钱？多久能上线？
                </div>
                <div className="max-w-[92%] rounded-2xl rounded-tl-sm bg-slate-100 px-4 py-3 text-sm leading-6 text-slate-700">
                  基础版 800-3000 元，标准版 3000-8000 元。基础版通常 3-5 天交付，标准版通常 1-2 周交付。可以补充您的行业和需求，我帮您推荐合适方案。
                </div>
                <div className="flex flex-wrap gap-2 pt-1">
                  <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700">意向等级：high</span>
                  <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">已自动生成线索</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="scroll-mt-24 px-4 py-16 sm:px-6 lg:px-8">
          <SectionTitle eyebrow="产品能力" title="从咨询到线索，AI 帮销售完成第一轮接待" />
          <div className="mx-auto grid max-w-7xl gap-5 md:grid-cols-2 xl:grid-cols-4">
            {features.map((item) => (
              <article key={item.title} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-lg bg-brand-50 text-brand-700">
                  <item.icon size={22} />
                </div>
                <h3 className="text-base font-semibold text-slate-950">{item.title}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">{item.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="workflow" className="scroll-mt-24 bg-white px-4 py-16 sm:px-6 lg:px-8">
          <SectionTitle eyebrow="使用流程" title="4 步完成 AI 销售接待闭环" />
          <div className="mx-auto grid max-w-6xl gap-5 md:grid-cols-4">
            {workflow.map(([title, description], index) => (
              <article key={title} className="rounded-xl border border-slate-200 bg-slate-50 p-6">
                <div className="mb-5 flex h-10 w-10 items-center justify-center rounded-full bg-brand-600 text-sm font-semibold text-white">
                  {index + 1}
                </div>
                <h3 className="font-semibold text-slate-950">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="scenarios" className="scroll-mt-24 px-4 py-16 sm:px-6 lg:px-8">
          <SectionTitle eyebrow="适用场景" title="适合这些需要销售接待的业务场景" />
          <div className="mx-auto grid max-w-7xl gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {scenarios.map(([title, description]) => (
              <article key={title} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <h3 className="font-semibold text-slate-950">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="pricing" className="scroll-mt-24 bg-white px-4 py-16 sm:px-6 lg:px-8">
          <SectionTitle eyebrow="套餐方案" title="按业务复杂度选择合适方案" />
          <div className="mx-auto grid max-w-7xl items-stretch gap-5 lg:grid-cols-3">
            {plans.map((plan) => (
              <article
                key={plan.name}
                className={[
                  "flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:shadow-md",
                  plan.highlight ? "relative overflow-hidden" : "",
                ].join(" ")}
              >
                {plan.highlight && <div className="absolute inset-x-0 top-0 h-1 bg-brand-500" />}
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-950">{plan.name}</h3>
                    <p className="mt-3 text-2xl font-semibold text-brand-700">{plan.price}</p>
                  </div>
                  {plan.highlight && <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">推荐</span>}
                </div>
                <p className="mt-4 min-h-12 text-sm leading-6 text-slate-600">适合：{plan.fit}</p>
                <ul className="mt-5 flex-1 space-y-3">
                  {plan.points.map((point) => (
                    <li key={point} className="flex items-center gap-2 text-sm text-slate-700">
                      <CheckCircle2 size={16} className="text-emerald-600" />
                      {point}
                    </li>
                  ))}
                </ul>
                <Link className="btn-primary mt-6 w-full" to="/public-chat">咨询方案</Link>
              </article>
            ))}
          </div>
        </section>

        <section id="faq" className="scroll-mt-24 px-4 py-16 sm:px-6 lg:px-8">
          <SectionTitle eyebrow="常见问题" title="常见问题" />
          <div className="mx-auto grid max-w-5xl gap-4 md:grid-cols-2">
            {faqs.map(([question, answer]) => (
              <article key={question} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="font-semibold text-slate-950">Q：{question}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">A：{answer}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="px-4 pb-16 sm:px-6 lg:px-8">
          <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-6 rounded-2xl bg-slate-950 p-8 text-white shadow-soft md:flex-row md:items-center">
            <div>
              <h2 className="text-2xl font-semibold tracking-normal">让 AI 帮你接待第一个客户</h2>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
                从一个公开咨询入口开始，快速验证 AI 销售客服是否适合你的业务。
              </p>
            </div>
            <Link className="inline-flex items-center justify-center gap-2 rounded-md bg-white px-5 py-3 text-sm font-medium text-slate-950 transition hover:bg-slate-100" to="/public-chat">
              立即发起咨询
              <ArrowRight size={17} />
            </Link>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-200 bg-white px-4 py-8 sm:px-6 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 text-sm text-slate-500 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="font-semibold text-slate-900">SalesPilot AI / 智销助手</p>
            <p className="mt-1">AI 销售客服系统 MVP Demo</p>
          </div>
          <Link className="inline-flex items-center gap-2 font-medium text-brand-700 hover:text-brand-600" to="/login">
            后台登录
            <ArrowRight size={15} />
          </Link>
        </div>
      </footer>
    </div>
  );
}
