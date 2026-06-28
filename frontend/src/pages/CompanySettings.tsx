import { Building2, CheckCircle2, Code2, Copy, ExternalLink, Palette, Save, UserRound } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { api } from "../api/client";
import type { AIModelConfig, CompanySettings, CompanySettingsPayload, DocumentRecord } from "../types";
import { defaultCompanySettings, hasHumanContact, normalizeBrandColor } from "./helpers";

const emptyForm: CompanySettingsPayload = {
  ...defaultCompanySettings,
  forbidden_topics: "",
  allowed_embed_domains: "",
  widget_position: "right",
};

const providerLabels: Record<string, string> = {
  deepseek: "DeepSeek",
  openai: "OpenAI",
  qwen: "通义千问",
  zhipu: "智谱 GLM",
  ollama: "Ollama",
  volcengine_ark: "火山方舟",
  custom: "Custom",
};

function fieldValue(value: string | undefined) {
  return value ?? "";
}

function toForm(settings: CompanySettings): CompanySettingsPayload {
  return {
    company_name: fieldValue(settings.company_name),
    company_short_name: fieldValue(settings.company_short_name),
    company_logo_url: fieldValue(settings.company_logo_url),
    company_intro: fieldValue(settings.company_intro),
    customer_service_name: fieldValue(settings.customer_service_name),
    customer_service_avatar_url: fieldValue(settings.customer_service_avatar_url),
    welcome_message: fieldValue(settings.welcome_message),
    brand_color: fieldValue(settings.brand_color) || defaultCompanySettings.brand_color,
    business_scope: fieldValue(settings.business_scope),
    human_contact_phone: fieldValue(settings.human_contact_phone),
    human_contact_wechat: fieldValue(settings.human_contact_wechat),
    human_contact_email: fieldValue(settings.human_contact_email),
    business_hours: fieldValue(settings.business_hours),
    handoff_message: fieldValue(settings.handoff_message),
    forbidden_topics: fieldValue(settings.forbidden_topics),
    allowed_embed_domains: fieldValue(settings.allowed_embed_domains),
    widget_position: settings.widget_position === "left" ? "left" : "right",
  };
}

function getDefaultEmbedBaseUrl() {
  if (typeof window === "undefined") return "";
  return window.location.origin;
}

function normalizeEmbedBaseUrl(value: string) {
  return value.trim().replace(/\/+$/, "");
}

export default function CompanySettingsPage() {
  const [form, setForm] = useState<CompanySettingsPayload>(emptyForm);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [currentModel, setCurrentModel] = useState<AIModelConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [logoError, setLogoError] = useState(false);
  const [copyMessage, setCopyMessage] = useState("");
  const [embedBaseUrl, setEmbedBaseUrl] = useState(getDefaultEmbedBaseUrl);

  const brandColor = normalizeBrandColor(form.brand_color);
  const contactConfigured = hasHumanContact(form);
  const embedDomains = form.allowed_embed_domains.trim();
  const normalizedEmbedBaseUrl = normalizeEmbedBaseUrl(embedBaseUrl || getDefaultEmbedBaseUrl());
  const embedCode = useMemo(() => {
    const attrs = [
      `  src="${normalizedEmbedBaseUrl}/widget.js"`,
      `  data-api-base="${normalizedEmbedBaseUrl}"`,
      `  data-position="${form.widget_position}"`,
      `  data-brand-color="${brandColor}"`,
    ];
    if (embedDomains) {
      attrs.push(`  data-allowed-domains="${embedDomains}"`);
    }
    return `<script\n${attrs.join("\n")}\n></script>`;
  }, [brandColor, embedDomains, form.widget_position, normalizedEmbedBaseUrl]);

  const modelLabel = useMemo(() => {
    if (!currentModel) return "暂无默认模型";
    return `${providerLabels[currentModel.provider] ?? currentModel.provider} / ${currentModel.model}`;
  }, [currentModel]);

  const loadData = async () => {
    setError("");
    try {
      const [settings, documentList, model] = await Promise.all([
        api.getCompanySettings(),
        api.listDocuments().catch(() => []),
        api.getCurrentAIConfig().catch(() => null),
      ]);
      setForm(toForm(settings));
      setDocuments(documentList);
      setCurrentModel(model);
    } catch (err) {
      setError(err instanceof Error ? err.message : "企业设置加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const setField = <K extends keyof CompanySettingsPayload>(key: K, value: CompanySettingsPayload[K]) => {
    setForm((current) => ({ ...current, [key]: value }));
    setCopyMessage("");
  };

  const validate = () => {
    if (!form.company_name.trim()) return "企业名称不能为空";
    if (!form.customer_service_name.trim()) return "客服名称不能为空";
    if (!/^#[0-9A-Fa-f]{6}$/.test(form.brand_color.trim())) return "品牌主色必须是合法 Hex 颜色，例如 #2563EB";
    return "";
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");
    try {
      const saved = await api.updateCompanySettings({
        ...form,
        company_short_name: form.company_short_name.trim() || form.company_name.trim(),
      });
      setForm(toForm(saved));
      setMessage("企业设置已保存，官网和公开咨询页会使用最新配置。");
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存企业设置失败");
    } finally {
      setSaving(false);
    }
  };

  const copyEmbedCode = async () => {
    setCopyMessage("");
    setError("");
    try {
      await navigator.clipboard.writeText(embedCode);
      setCopyMessage("嵌入代码已复制。");
    } catch (err) {
      console.error("Copy embed code failed:", err);
      setError("复制失败，请手动复制嵌入代码。");
    }
  };

  if (loading) {
    return <div className="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">企业设置加载中...</div>;
  }

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-950">企业设置</h2>
          <p className="mt-1 text-sm text-slate-500">配置单企业品牌、AI 客服身份、公开咨询欢迎语和人工联系方式。</p>
        </div>
        <button className="btn-primary" type="submit" disabled={saving}>
          <Save size={16} />
          {saving ? "保存中..." : "保存设置"}
        </button>
      </div>

      {error && <p className="rounded-md bg-red-50 p-3 text-sm text-red-600">{error}</p>}
      {message && <p className="rounded-md bg-emerald-50 p-3 text-sm text-emerald-700">{message}</p>}

      <section className="grid gap-4 lg:grid-cols-4">
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">当前企业</p>
          <p className="mt-2 text-lg font-semibold text-slate-950">{form.company_short_name || form.company_name || "-"}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">当前客服</p>
          <p className="mt-2 text-lg font-semibold text-slate-950">{form.customer_service_name || "-"}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">人工联系方式</p>
          <p className={["mt-2 text-lg font-semibold", contactConfigured ? "text-emerald-700" : "text-amber-700"].join(" ")}>
            {contactConfigured ? "已配置" : "未配置"}
          </p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">知识库文件 / 默认模型</p>
          <p className="mt-2 text-sm font-medium text-slate-950">{documents.length} 份文件</p>
          <p className="mt-1 text-xs text-slate-500">{modelLabel}</p>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
        <div className="space-y-6">
          <section className="rounded-lg border border-slate-200 bg-white p-5">
            <div className="mb-5 flex items-center gap-2">
              <Building2 size={18} className="text-brand-600" />
              <h3 className="font-semibold text-slate-950">基础品牌信息</h3>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">企业名称</span>
                <input className="field" value={form.company_name} onChange={(event) => setField("company_name", event.target.value)} />
              </label>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">企业简称</span>
                <input className="field" value={form.company_short_name} onChange={(event) => setField("company_short_name", event.target.value)} />
              </label>
              <label className="block md:col-span-2">
                <span className="mb-1 block text-sm font-medium text-slate-700">企业简介</span>
                <textarea className="field min-h-24" value={form.company_intro} onChange={(event) => setField("company_intro", event.target.value)} />
              </label>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">品牌主色</span>
                <div className="flex gap-2">
                  <input className="field" value={form.brand_color} onChange={(event) => setField("brand_color", event.target.value)} placeholder="#2563EB" />
                  <span className="h-10 w-12 rounded-md border border-slate-200" style={{ backgroundColor: brandColor }} />
                </div>
              </label>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">Logo URL</span>
                <input className="field" value={form.company_logo_url} onChange={(event) => { setLogoError(false); setField("company_logo_url", event.target.value); }} placeholder="https://example.com/logo.png" />
              </label>
            </div>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-5">
            <div className="mb-5 flex items-center gap-2">
              <UserRound size={18} className="text-brand-600" />
              <h3 className="font-semibold text-slate-950">AI 客服身份</h3>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">客服名称</span>
                <input className="field" value={form.customer_service_name} onChange={(event) => setField("customer_service_name", event.target.value)} />
              </label>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">客服头像 URL</span>
                <input className="field" value={form.customer_service_avatar_url} onChange={(event) => setField("customer_service_avatar_url", event.target.value)} />
              </label>
              <label className="block md:col-span-2">
                <span className="mb-1 block text-sm font-medium text-slate-700">欢迎语</span>
                <textarea className="field min-h-24" value={form.welcome_message} onChange={(event) => setField("welcome_message", event.target.value)} />
              </label>
              <label className="block md:col-span-2">
                <span className="mb-1 block text-sm font-medium text-slate-700">业务范围</span>
                <textarea className="field min-h-24" value={form.business_scope} onChange={(event) => setField("business_scope", event.target.value)} />
              </label>
              <label className="block md:col-span-2">
                <span className="mb-1 block text-sm font-medium text-slate-700">禁止回答内容</span>
                <textarea className="field min-h-20" value={form.forbidden_topics} onChange={(event) => setField("forbidden_topics", event.target.value)} placeholder="例如：合同法律条款、最终大货报价、赔偿承诺" />
              </label>
            </div>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-5">
            <div className="mb-5 flex items-center gap-2">
              <CheckCircle2 size={18} className="text-brand-600" />
              <h3 className="font-semibold text-slate-950">人工联系方式</h3>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">人工客服电话</span>
                <input className="field" value={form.human_contact_phone} onChange={(event) => setField("human_contact_phone", event.target.value)} />
              </label>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">人工客服微信</span>
                <input className="field" value={form.human_contact_wechat} onChange={(event) => setField("human_contact_wechat", event.target.value)} />
              </label>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">人工客服邮箱</span>
                <input className="field" value={form.human_contact_email} onChange={(event) => setField("human_contact_email", event.target.value)} />
              </label>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">工作时间</span>
                <input className="field" value={form.business_hours} onChange={(event) => setField("business_hours", event.target.value)} />
              </label>
              <label className="block md:col-span-2">
                <span className="mb-1 block text-sm font-medium text-slate-700">人工转接提示语</span>
                <textarea className="field min-h-20" value={form.handoff_message} onChange={(event) => setField("handoff_message", event.target.value)} />
              </label>
            </div>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-5">
            <div className="mb-5 flex items-center gap-2">
              <Code2 size={18} className="text-brand-600" />
              <h3 className="font-semibold text-slate-950">官网嵌入客服</h3>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block md:col-span-2">
                <span className="mb-1 block text-sm font-medium text-slate-700">允许嵌入域名</span>
                <textarea
                  className="field min-h-20"
                  value={form.allowed_embed_domains}
                  onChange={(event) => setField("allowed_embed_domains", event.target.value)}
                  placeholder="example.com, www.example.com, localhost, 127.0.0.1"
                />
                <span className="mt-1 block text-xs text-slate-500">保存时会自动清洗协议、路径、端口和重复域名。留空时为 Demo 模式，不限制嵌入域名。</span>
              </label>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">悬浮位置</span>
                <select
                  className="field"
                  value={form.widget_position}
                  onChange={(event) => setField("widget_position", event.target.value === "left" ? "left" : "right")}
                >
                  <option value="right">右下角</option>
                  <option value="left">左下角</option>
                </select>
              </label>
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">部署地址</span>
                <input
                  className="field"
                  value={embedBaseUrl}
                  onChange={(event) => setEmbedBaseUrl(event.target.value)}
                  placeholder="https://your-domain.com"
                />
              </label>
              {!embedDomains && (
                <p className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800 md:col-span-2">
                  当前为 Demo 模式，未限制嵌入域名。正式展示前建议填写企业官网域名。
                </p>
              )}
              <label className="block md:col-span-2">
                <span className="mb-1 block text-sm font-medium text-slate-700">嵌入代码</span>
                <textarea className="field min-h-36 font-mono text-xs" value={embedCode} readOnly />
                <span className="mt-1 block text-xs text-slate-500">将代码粘贴到企业官网 &lt;/body&gt; 标签前。</span>
              </label>
              <div className="flex flex-wrap gap-2 md:col-span-2">
                <button className="btn-secondary" type="button" onClick={copyEmbedCode}>
                  <Copy size={16} />
                  复制代码
                </button>
                <button className="btn-secondary" type="button" onClick={() => window.open("/embed/chat", "_blank", "noopener,noreferrer")}>
                  <ExternalLink size={16} />
                  打开预览
                </button>
                {copyMessage && <span className="inline-flex items-center text-sm text-emerald-700">{copyMessage}</span>}
              </div>
            </div>
          </section>
        </div>

        <aside className="space-y-5">
          <section className="rounded-lg border border-slate-200 bg-white p-5">
            <div className="mb-4 flex items-center gap-2">
              <Palette size={18} className="text-brand-600" />
              <h3 className="font-semibold text-slate-950">品牌预览</h3>
            </div>
            <div className="rounded-xl border border-slate-200 p-4">
              <div className="flex items-center gap-3">
                {form.company_logo_url && !logoError ? (
                  <img
                    className="h-11 w-11 rounded-lg border border-slate-200 object-cover"
                    src={form.company_logo_url}
                    alt={form.company_short_name || form.company_name}
                    onError={() => setLogoError(true)}
                  />
                ) : (
                  <span className="flex h-11 w-11 items-center justify-center rounded-lg text-sm font-semibold text-white" style={{ backgroundColor: brandColor }}>
                    {(form.company_short_name || form.company_name || "S").slice(0, 1)}
                  </span>
                )}
                <div>
                  <p className="font-semibold text-slate-950">{form.company_short_name || form.company_name || "未命名企业"}</p>
                  <p className="text-xs text-slate-500">{form.customer_service_name || "AI 客服"}</p>
                </div>
              </div>
              <p className="mt-4 rounded-lg bg-slate-50 p-3 text-sm leading-6 text-slate-600">
                {form.welcome_message || "欢迎语未配置"}
              </p>
              <button className="mt-4 inline-flex w-full items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-white" type="button" style={{ backgroundColor: brandColor }}>
                公开咨询主按钮
              </button>
            </div>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-5 text-sm text-slate-600">
            <h3 className="font-semibold text-slate-950">配置状态</h3>
            <div className="mt-4 space-y-3">
              <p>公开咨询页：已应用</p>
              <p>人工联系方式：{contactConfigured ? "已配置" : "未配置"}</p>
              <p>知识库文件：{documents.length} 份</p>
              <p>当前默认模型：{modelLabel}</p>
            </div>
          </section>
        </aside>
      </div>
    </form>
  );
}
