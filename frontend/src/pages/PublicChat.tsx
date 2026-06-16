import { ArrowLeft, Bot, CheckCircle2, LockKeyhole, MessageCircle, Send, Sparkles } from "lucide-react";
import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/client";
import type { ChatResponse } from "../types";
import { formatIntentLevel, formatIntentType } from "./helpers";

const presetQuestions = [
  "你们做 AI 客服多少钱？",
  "多久可以上线？",
  "能接企业微信吗？",
  "后续可以维护吗？",
  "适合哪些行业？",
];

const consultationTopics = ["价格和套餐", "交付周期", "行业适配", "企业微信 / 飞书接入", "售后维护"];
const demoPoints = ["AI 根据知识库回复", "自动识别客户意向", "high 意向进入后台线索池", "后台可查看完整对话"];

function levelClass(level: string) {
  if (level === "high") return "bg-amber-50 text-amber-700 border-amber-200";
  if (level === "medium") return "bg-sky-50 text-sky-700 border-sky-200";
  return "bg-slate-100 text-slate-600 border-slate-200";
}

export default function PublicChat() {
  const [customerName, setCustomerName] = useState("");
  const [customerContact, setCustomerContact] = useState("");
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const validate = () => {
    if (!customerName.trim()) return "请输入您的姓名";
    if (!customerContact.trim()) return "请输入联系方式";
    if (!question.trim()) return "请输入咨询问题";
    return "";
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await api.publicChat({
        customer_name: customerName.trim(),
        customer_contact: customerContact.trim(),
        question: question.trim(),
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "提交咨询失败，请稍后重试");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-brand-50 text-slate-900">
      <header className="border-b border-slate-200/80 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <Link className="flex items-center gap-3" to="/">
            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600 text-white">
              <Bot size={21} />
            </span>
            <span>
              <span className="block text-base font-semibold text-slate-950">SalesPilot AI</span>
              <span className="block text-xs text-slate-500">公开咨询</span>
            </span>
          </Link>
          <div className="flex items-center gap-2">
            <Link className="btn-secondary px-3" to="/">
              <ArrowLeft size={16} />
              返回首页
            </Link>
            <Link className="btn-primary px-3" to="/login">
              <LockKeyhole size={16} />
              企业后台登录
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl gap-6 px-4 py-10 sm:px-6 lg:grid-cols-[minmax(0,1fr)_360px] lg:px-8">
        <section className="space-y-6">
          <div>
            <p className="inline-flex items-center gap-2 rounded-full border border-brand-100 bg-white px-3 py-1 text-sm font-medium text-brand-700 shadow-sm">
              <Sparkles size={15} />
              AI 销售客服在线
            </p>
            <h1 className="mt-5 text-3xl font-semibold tracking-normal text-slate-950 md:text-4xl">提交咨询，立即获得 AI 回复</h1>
            <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600">
              本页会模拟真实客户咨询入口：AI 基于知识库回复问题，识别客户意向，并将 high 意向自动沉淀到后台客户线索。
            </p>
          </div>

          <form className="space-y-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm" onSubmit={handleSubmit}>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">客户姓名</span>
                <input
                  className="field"
                  value={customerName}
                  onChange={(event) => setCustomerName(event.target.value)}
                  placeholder="请输入您的姓名"
                />
              </label>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">联系方式</span>
                <input
                  className="field"
                  value={customerContact}
                  onChange={(event) => setCustomerContact(event.target.value)}
                  placeholder="手机号 / 微信 / 邮箱"
                />
              </label>
            </div>

            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">咨询问题</span>
              <textarea
                className="field min-h-36"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="例如：你们能接企业微信吗？多少钱？"
              />
            </label>

            <div>
              <p className="mb-2 text-sm font-medium text-slate-700">示例问题</p>
              <div className="flex flex-wrap gap-2">
                {presetQuestions.map((item) => (
                  <button
                    key={item}
                    className="rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                    type="button"
                    onClick={() => setQuestion(item)}
                    disabled={loading}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>

            {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}

            <button className="btn-primary w-full py-3" type="submit" disabled={loading}>
              <Send size={16} />
              {loading ? "AI 正在回复..." : "提交咨询"}
            </button>
          </form>

          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            {!result ? (
              <div className="flex min-h-72 flex-col items-center justify-center text-center text-sm text-slate-500">
                <MessageCircle className="mb-3 text-slate-300" size={34} />
                提交咨询后，这里会展示 AI 回复、意向识别和命中的知识库内容。
              </div>
            ) : (
              <div className="space-y-5">
                <div>
                  <p className="mb-2 text-sm font-medium text-slate-700">AI 回复</p>
                  <div className="rounded-lg bg-slate-50 p-4 text-sm leading-7 text-slate-700">{result.answer}</div>
                </div>

                <div className="flex flex-wrap gap-3">
                  <span className="rounded-full border border-brand-100 bg-brand-50 px-3 py-1.5 text-sm font-medium text-brand-700">
                    意向类型：{formatIntentType(result.intent_type)}
                  </span>
                  <span className={["rounded-full border px-3 py-1.5 text-sm font-medium", levelClass(result.intent_level)].join(" ")}>
                    意向等级：{formatIntentLevel(result.intent_level)}
                  </span>
                </div>

                {result.intent_level === "high" ? (
                  <p className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-800">
                    系统已将您的咨询标记为高意向线索，销售人员可在后台继续跟进。
                  </p>
                ) : (
                  <p className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
                    系统已记录本次咨询，企业可在后台查看对话记录。
                  </p>
                )}

                <div>
                  <p className="mb-3 text-sm font-medium text-slate-700">命中的知识库内容</p>
                  <div className="space-y-3">
                    {result.matched_knowledge.length === 0 ? (
                      <p className="rounded-lg bg-slate-50 px-4 py-3 text-sm text-slate-500">未命中知识库内容</p>
                    ) : (
                      result.matched_knowledge.map((item) => (
                        <article key={item.id} className="rounded-lg border border-slate-200 p-4">
                          <div className="mb-2 flex flex-wrap items-center gap-2">
                            <h3 className="font-medium text-slate-950">{item.title}</h3>
                            <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">{item.category}</span>
                          </div>
                          <p className="text-sm leading-6 text-slate-600">{item.content}</p>
                        </article>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}
          </section>
        </section>

        <aside className="space-y-5">
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="font-semibold text-slate-950">你可以咨询</h2>
            <ul className="mt-4 space-y-3">
              {consultationTopics.map((item) => (
                <li key={item} className="flex items-center gap-2 text-sm text-slate-600">
                  <CheckCircle2 size={16} className="text-emerald-600" />
                  {item}
                </li>
              ))}
            </ul>
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="font-semibold text-slate-950">本页会演示</h2>
            <ul className="mt-4 space-y-3">
              {demoPoints.map((item) => (
                <li key={item} className="flex items-center gap-2 text-sm text-slate-600">
                  <CheckCircle2 size={16} className="text-brand-600" />
                  {item}
                </li>
              ))}
            </ul>
          </section>

          <section className="rounded-xl bg-slate-950 p-5 text-white shadow-soft">
            <h2 className="font-semibold">演示提示</h2>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              未配置当前模型 API Key 时，系统会使用 mock fallback，仍可完整演示 AI 回复、意向识别和线索沉淀。
            </p>
            <div className="mt-5 flex flex-col gap-2">
              <Link className="inline-flex items-center justify-center gap-2 rounded-md bg-white px-4 py-2 text-sm font-medium text-slate-950 transition hover:bg-slate-100" to="/">
                返回官网首页
              </Link>
              <Link className="inline-flex items-center justify-center gap-2 rounded-md border border-white/20 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/10" to="/login">
                企业后台登录
              </Link>
            </div>
          </section>
        </aside>
      </main>
    </div>
  );
}
