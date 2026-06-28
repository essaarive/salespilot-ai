import { Bot, Loader2, Send, UserRound, X } from "lucide-react";
import { FormEvent, useEffect, useRef, useState } from "react";

import { api } from "../api/client";
import type { ChatResponse, PublicCompanySettings } from "../types";
import {
  cleanAIText,
  defaultCompanySettings,
  formatHandoffReason,
  getCompanyDisplayName,
  hasHumanContact,
  normalizeBrandColor,
} from "./helpers";

type ChatMessage = {
  id: string;
  role: "assistant" | "user";
  content: string;
  response?: ChatResponse;
};

const quickQuestions = ["你们提供哪些服务？", "怎么接入？", "交付周期多久？", "可以人工咨询吗？"];

function createMessageId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function fallbackInitial(name: string) {
  return (name || "S").slice(0, 1).toUpperCase();
}

export default function EmbedChat() {
  const [company, setCompany] = useState<PublicCompanySettings>(defaultCompanySettings);
  const [companyLoaded, setCompanyLoaded] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [customerContact, setCustomerContact] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [logoError, setLogoError] = useState(false);
  const [avatarError, setAvatarError] = useState(false);
  const messageEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    api.getPublicCompanySettings()
      .then((settings) => {
        setCompany({ ...defaultCompanySettings, ...settings });
        setCompanyLoaded(true);
      })
      .catch(() => {
        setCompany(defaultCompanySettings);
        setCompanyLoaded(false);
      });
  }, []);

  useEffect(() => {
    document.title = companyLoaded ? `${getCompanyDisplayName(company)} 在线咨询` : "在线咨询";
  }, [company, companyLoaded]);

  useEffect(() => {
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content: company.welcome_message || defaultCompanySettings.welcome_message,
      },
    ]);
  }, [company.welcome_message]);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  const brandColor = normalizeBrandColor(company.brand_color);
  const displayName = getCompanyDisplayName(company);
  const contactConfigured = hasHumanContact(company);

  const closeWidget = () => {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage("salespilot:close", "*");
    }
  };

  const sendQuestion = async (value = question) => {
    const trimmedQuestion = value.trim();
    if (!trimmedQuestion || loading) {
      setError(trimmedQuestion ? "" : "请输入您的问题");
      return;
    }

    setLoading(true);
    setError("");
    setQuestion("");
    setMessages((current) => [
      ...current,
      { id: createMessageId(), role: "user", content: trimmedQuestion },
    ]);

    try {
      const response = await api.publicChat({
        customer_name: customerName.trim(),
        customer_contact: customerContact.trim(),
        question: trimmedQuestion,
      });
      setMessages((current) => [
        ...current,
        {
          id: createMessageId(),
          role: "assistant",
          content: cleanAIText(response.answer),
          response,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "发送失败，请稍后重试");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    sendQuestion();
  };

  return (
    <div className="flex h-screen min-h-[520px] flex-col overflow-hidden bg-slate-50 text-slate-900">
      <header className="flex items-center justify-between gap-3 border-b border-slate-200 bg-white px-4 py-3">
        <div className="flex min-w-0 items-center gap-3">
          {company.company_logo_url && !logoError ? (
            <img
              className="h-10 w-10 rounded-xl border border-slate-200 object-cover"
              src={company.company_logo_url}
              alt={displayName}
              onError={() => setLogoError(true)}
            />
          ) : (
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-sm font-semibold text-white" style={{ backgroundColor: brandColor }}>
              {fallbackInitial(displayName)}
            </span>
          )}
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-slate-950">{displayName}</p>
            <p className="truncate text-xs text-slate-500">{company.customer_service_name || "AI 客服"} · 在线咨询</p>
          </div>
        </div>
        <button
          className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-500 transition hover:bg-slate-50"
          type="button"
          onClick={closeWidget}
          aria-label="关闭客服窗口"
        >
          <X size={17} />
        </button>
      </header>

      <main className="flex-1 overflow-y-auto px-4 py-4">
        <div className="space-y-3">
          {messages.map((message) => (
            <div key={message.id} className={message.role === "user" ? "flex justify-end" : "flex justify-start"}>
              <div className={["flex max-w-[88%] gap-2", message.role === "user" ? "flex-row-reverse" : ""].join(" ")}>
                <span
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-white"
                  style={{ backgroundColor: message.role === "user" ? "#64748B" : brandColor }}
                >
                  {message.role === "user" ? <UserRound size={15} /> : company.customer_service_avatar_url && !avatarError ? (
                    <img
                      className="h-8 w-8 rounded-full object-cover"
                      src={company.customer_service_avatar_url}
                      alt={company.customer_service_name || "AI 客服"}
                      onError={() => setAvatarError(true)}
                    />
                  ) : (
                    <Bot size={15} />
                  )}
                </span>
                <div
                  className={[
                    "rounded-2xl px-3 py-2 text-sm leading-6 shadow-sm",
                    message.role === "user"
                      ? "rounded-tr-sm bg-slate-900 text-white"
                      : "rounded-tl-sm border border-slate-200 bg-white text-slate-700",
                  ].join(" ")}
                >
                  <p className="whitespace-pre-line">{message.content}</p>
                  {message.response?.requires_handoff && (
                    <div className="mt-3 rounded-xl border border-orange-200 bg-orange-50 p-3 text-xs leading-5 text-orange-800">
                      <p>{company.handoff_message || "您的问题已记录，我们建议由工作人员进一步确认并跟进。"}</p>
                      {message.response.handoff_reason && <p className="mt-1">原因：{formatHandoffReason(message.response.handoff_reason)}</p>}
                      {contactConfigured && (
                        <div className="mt-2 space-y-1 text-slate-700">
                          {company.human_contact_phone && <p>电话：{company.human_contact_phone}</p>}
                          {company.human_contact_wechat && <p>微信：{company.human_contact_wechat}</p>}
                          {company.human_contact_email && <p>邮箱：{company.human_contact_email}</p>}
                          {company.business_hours && <p>工作时间：{company.business_hours}</p>}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Loader2 className="animate-spin" size={16} />
              {company.customer_service_name || "AI 客服"}正在回复...
            </div>
          )}
          <div ref={messageEndRef} />
        </div>
      </main>

      <section className="border-t border-slate-200 bg-white px-4 py-3">
        <div className="mb-3 flex flex-wrap gap-2">
          {quickQuestions.map((item) => (
            <button
              key={item}
              className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-600 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              disabled={loading}
              onClick={() => sendQuestion(item)}
            >
              {item}
            </button>
          ))}
        </div>

        <div className="mb-2 grid grid-cols-2 gap-2">
          <input
            className="rounded-lg border border-slate-200 px-3 py-2 text-xs outline-none transition focus:border-slate-400"
            value={customerName}
            onChange={(event) => setCustomerName(event.target.value)}
            placeholder="姓名（选填）"
          />
          <input
            className="rounded-lg border border-slate-200 px-3 py-2 text-xs outline-none transition focus:border-slate-400"
            value={customerContact}
            onChange={(event) => setCustomerContact(event.target.value)}
            placeholder="联系方式（选填）"
          />
        </div>

        <form className="flex gap-2" onSubmit={handleSubmit}>
          <input
            className="min-w-0 flex-1 rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none transition focus:border-slate-400"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="请输入您的问题..."
            disabled={loading}
          />
          <button
            className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-white transition disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            disabled={loading}
            style={{ backgroundColor: brandColor }}
            aria-label="发送"
          >
            <Send size={16} />
          </button>
        </form>
        {error && <p className="mt-2 rounded-md bg-red-50 px-3 py-2 text-xs text-red-600">{error}</p>}
      </section>
    </div>
  );
}
