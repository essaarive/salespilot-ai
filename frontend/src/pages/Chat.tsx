import { Send } from "lucide-react";
import { FormEvent, useState } from "react";

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

export default function Chat() {
  const [customerName, setCustomerName] = useState("张三");
  const [customerContact, setCustomerContact] = useState("13800000000");
  const [question, setQuestion] = useState("你们做 AI 客服多少钱？");
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(
        await api.chat({
          customer_name: customerName,
          customer_contact: customerContact,
          question,
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-950">AI 对话测试</h2>
        <p className="mt-1 text-sm text-slate-500">模拟客户咨询，验证知识库检索、AI 回复和线索沉淀。</p>
      </div>

      <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
        <form className="space-y-4 rounded-lg border border-slate-200 bg-white p-5" onSubmit={handleSubmit}>
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-slate-700">客户姓名</span>
            <input className="field" value={customerName} onChange={(event) => setCustomerName(event.target.value)} required />
          </label>
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-slate-700">联系方式</span>
            <input className="field" value={customerContact} onChange={(event) => setCustomerContact(event.target.value)} />
          </label>
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-slate-700">客户问题</span>
            <textarea
              className="field min-h-36"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              required
            />
          </label>
          <div>
            <p className="mb-2 text-sm font-medium text-slate-700">预设测试问题</p>
            <div className="flex flex-wrap gap-2">
              {presetQuestions.map((item) => (
                <button
                  key={item}
                  className="rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 transition hover:bg-slate-50"
                  type="button"
                  onClick={() => setQuestion(item)}
                  disabled={loading}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
          <p className="rounded-md bg-brand-50 px-3 py-2 text-xs leading-5 text-brand-700">
            未配置 DeepSeek API Key 时会自动使用 mock 回复，方便本地演示完整流程。
          </p>
          {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
          <button className="btn-primary w-full" type="submit" disabled={loading}>
            <Send size={16} />
            {loading ? "生成中..." : "生成回复"}
          </button>
        </form>

        <section className="rounded-lg border border-slate-200 bg-white p-5">
          {!result ? (
            <div className="flex min-h-80 items-center justify-center text-sm text-slate-500">
              生成后将在这里展示 AI 回复、意向识别和命中知识。
            </div>
          ) : (
            <div className="space-y-5">
              <div>
                <p className="mb-2 text-sm font-medium text-slate-700">AI 回复</p>
                <div className="rounded-md bg-slate-50 p-4 text-sm leading-7 text-slate-700">{result.answer}</div>
              </div>
              <div className="flex flex-wrap gap-3">
                <span className="rounded bg-brand-50 px-3 py-1.5 text-sm text-brand-700">
                  意向类型：{formatIntentType(result.intent_type)}
                </span>
                <span className="rounded bg-emerald-50 px-3 py-1.5 text-sm text-emerald-700">
                  意向等级：{formatIntentLevel(result.intent_level)}
                </span>
              </div>
              {result.intent_level === "high" && (
                <p className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                  已自动沉淀为客户线索，可前往客户线索页面查看跟进。
                </p>
              )}
              <div>
                <p className="mb-3 text-sm font-medium text-slate-700">命中的知识库内容</p>
                <div className="space-y-3">
                  {result.matched_knowledge.length === 0 ? (
                    <p className="text-sm text-slate-500">未命中知识库内容</p>
                  ) : (
                    result.matched_knowledge.map((item) => (
                      <article key={item.id} className="rounded-md border border-slate-200 p-4">
                        <div className="mb-2 flex flex-wrap items-center gap-2">
                          <h3 className="font-medium text-slate-950">{item.title}</h3>
                          <span className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-600">{item.category}</span>
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
      </div>
    </div>
  );
}
