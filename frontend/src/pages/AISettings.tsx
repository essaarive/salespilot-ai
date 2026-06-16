import { CheckCircle2, Edit3, Plus, RefreshCw, Trash2, Zap } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import { api } from "../api/client";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";
import type { AIModelConfig, AIModelConfigPayload, AIProvider } from "../types";

const providerDefaults: Record<AIProvider, { base_url: string; model: string; name: string }> = {
  deepseek: {
    name: "DeepSeek 默认配置",
    base_url: "https://api.deepseek.com",
    model: "deepseek-chat",
  },
  openai: {
    name: "OpenAI 默认配置",
    base_url: "https://api.openai.com/v1",
    model: "gpt-4o-mini",
  },
  qwen: {
    name: "通义千问兼容模式",
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1",
    model: "qwen-plus",
  },
  zhipu: {
    name: "智谱 GLM 默认配置",
    base_url: "https://open.bigmodel.cn/api/paas/v4",
    model: "glm-4-flash",
  },
  ollama: {
    name: "Ollama 本地模型",
    base_url: "http://localhost:11434/v1",
    model: "qwen2.5:7b",
  },
  custom: {
    name: "自定义兼容模型",
    base_url: "",
    model: "",
  },
};

type AIConfigForm = AIModelConfigPayload;

const emptyForm: AIConfigForm = {
  provider: "deepseek",
  name: providerDefaults.deepseek.name,
  base_url: providerDefaults.deepseek.base_url,
  model: providerDefaults.deepseek.model,
  api_key: "",
  clear_api_key: false,
  enabled: true,
  is_default: false,
};

const providerLabels: Record<AIProvider, string> = {
  deepseek: "DeepSeek",
  openai: "OpenAI",
  qwen: "通义千问",
  zhipu: "智谱 GLM",
  ollama: "Ollama",
  custom: "Custom",
};

export default function AISettings() {
  const [configs, setConfigs] = useState<AIModelConfig[]>([]);
  const [current, setCurrent] = useState<AIModelConfig | null>(null);
  const [form, setForm] = useState<AIConfigForm>(emptyForm);
  const [editing, setEditing] = useState<AIModelConfig | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [actingId, setActingId] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadData = async () => {
    setError("");
    try {
      const [configList, currentConfig] = await Promise.all([
        api.getAIConfigs(),
        api.getCurrentAIConfig().catch(() => null),
      ]);
      setConfigs(configList);
      setCurrent(currentConfig);
    } catch (err) {
      setError(err instanceof Error ? err.message : "模型配置加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleProviderChange = (provider: AIProvider) => {
    const defaults = providerDefaults[provider];
    setForm({
      ...form,
      provider,
      name: editing ? form.name : defaults.name,
      base_url: defaults.base_url || form.base_url,
      model: defaults.model || form.model,
    });
  };

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setMessage("");
    setError("");
    setModalOpen(true);
  };

  const openEdit = (config: AIModelConfig) => {
    setEditing(config);
    setForm({
      provider: config.provider,
      name: config.name,
      base_url: config.base_url,
      model: config.model,
      api_key: "",
      clear_api_key: false,
      enabled: config.enabled,
      is_default: config.is_default,
    });
    setMessage("");
    setError("");
    setModalOpen(true);
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");

    const payload: AIConfigForm = { ...form };
    if (editing && !payload.api_key) {
      delete payload.api_key;
    }

    try {
      if (editing) {
        await api.updateAIConfig(editing.id, payload);
      } else {
        await api.createAIConfig(payload);
      }
      setModalOpen(false);
      setMessage("模型配置已保存");
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存失败");
    } finally {
      setSaving(false);
    }
  };

  const handleSetDefault = async (config: AIModelConfig) => {
    setActingId(config.id);
    setError("");
    setMessage("");
    try {
      await api.setDefaultAIConfig(config.id);
      setMessage(`已将「${config.name}」设为默认模型`);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "设置默认失败");
    } finally {
      setActingId(null);
    }
  };

  const handleTest = async (config: AIModelConfig) => {
    setActingId(config.id);
    setError("");
    setMessage("");
    try {
      const result = await api.testAIConfig(config.id);
      if (result.success) {
        setMessage(`测试成功：${result.message}`);
      } else {
        setError(`测试失败：${result.message}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "测试失败");
    } finally {
      setActingId(null);
    }
  };

  const handleDelete = async (config: AIModelConfig) => {
    if (config.is_default || !window.confirm(`确认删除「${config.name}」吗？`)) return;
    setActingId(config.id);
    setError("");
    setMessage("");
    try {
      await api.deleteAIConfig(config.id);
      setMessage("模型配置已删除");
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "删除失败");
    } finally {
      setActingId(null);
    }
  };

  const isEditingDefault = Boolean(editing?.is_default);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-950">模型设置</h2>
          <p className="mt-1 text-sm text-slate-500">配置 DeepSeek、OpenAI、通义千问、智谱、Ollama 或自定义兼容 API。</p>
        </div>
        <button className="btn-primary" type="button" onClick={openCreate}>
          <Plus size={16} />
          新增配置
        </button>
      </div>

      {error && <p className="rounded-md bg-red-50 p-3 text-sm text-red-600">{error}</p>}
      {message && <p className="rounded-md bg-emerald-50 p-3 text-sm text-emerald-700">{message}</p>}

      <section className="rounded-lg border border-slate-200 bg-white p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-slate-500">当前默认模型</p>
            <h3 className="mt-2 text-lg font-semibold text-slate-950">
              {current ? current.name : "暂无默认配置"}
            </h3>
            {current && (
              <div className="mt-3 grid gap-2 text-sm text-slate-600 md:grid-cols-2">
                <p>Provider：{providerLabels[current.provider]}</p>
                <p>Model：{current.model}</p>
                <p className="md:col-span-2">Base URL：{current.base_url}</p>
                <p>API Key：{current.api_key_masked ? `已配置 ${current.api_key_preview}` : "未配置"}</p>
                <p>状态：{current.enabled ? "已启用" : "未启用"}</p>
              </div>
            )}
          </div>
          <div className="rounded-md bg-brand-50 p-3 text-brand-700">
            <Zap size={22} />
          </div>
        </div>
      </section>

      {loading ? (
        <div className="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
          模型配置加载中...
        </div>
      ) : (
        <DataTable
          data={configs}
          emptyText="暂无模型配置，请新增一个 OpenAI-Compatible API 配置"
          columns={[
            { key: "name", title: "名称", render: (row) => <span className="font-medium text-slate-950">{row.name}</span> },
            { key: "provider", title: "Provider", render: (row) => providerLabels[row.provider] },
            { key: "model", title: "模型", render: (row) => row.model },
            { key: "base_url", title: "Base URL", render: (row) => <span className="text-slate-600">{row.base_url}</span> },
            {
              key: "api_key",
              title: "API Key",
              render: (row) => row.api_key_masked ? `已配置 ${row.api_key_preview}` : "未配置",
            },
            {
              key: "status",
              title: "状态",
              render: (row) => (
                <div className="flex flex-wrap gap-2">
                  {row.is_default && <span className="rounded bg-amber-50 px-2 py-1 text-xs text-amber-700">默认</span>}
                  <span className={["rounded px-2 py-1 text-xs", row.enabled ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500"].join(" ")}>
                    {row.enabled ? "启用" : "停用"}
                  </span>
                </div>
              ),
            },
            {
              key: "actions",
              title: "操作",
              render: (row) => (
                <div className="flex flex-wrap gap-2">
                  <button className="btn-secondary px-2" type="button" onClick={() => openEdit(row)} title="编辑">
                    <Edit3 size={15} />
                  </button>
                  <button
                    className="btn-secondary px-2"
                    type="button"
                    onClick={() => handleSetDefault(row)}
                    disabled={row.is_default || !row.enabled || actingId === row.id}
                    title="设为默认"
                  >
                    <CheckCircle2 size={15} />
                  </button>
                  <button
                    className="btn-secondary px-2"
                    type="button"
                    onClick={() => handleTest(row)}
                    disabled={actingId === row.id}
                    title="测试连接"
                  >
                    {actingId === row.id ? "测试中" : <RefreshCw size={15} />}
                  </button>
                  <button
                    className="btn-danger px-2"
                    type="button"
                    onClick={() => handleDelete(row)}
                    disabled={row.is_default || actingId === row.id}
                    title={row.is_default ? "默认配置不允许删除" : "删除"}
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              ),
            },
          ]}
        />
      )}

      <Modal title={editing ? "编辑模型配置" : "新增模型配置"} open={modalOpen} onClose={() => setModalOpen(false)}>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Provider</span>
              <select className="field" value={form.provider} onChange={(event) => handleProviderChange(event.target.value as AIProvider)}>
                {Object.entries(providerLabels).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">名称</span>
              <input className="field" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
            </label>
          </div>

          <label className="block">
            <span className="mb-1 block text-sm font-medium text-slate-700">Base URL</span>
            <input className="field" value={form.base_url} onChange={(event) => setForm({ ...form, base_url: event.target.value })} required />
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Model</span>
              <input className="field" value={form.model} onChange={(event) => setForm({ ...form, model: event.target.value })} required />
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">API Key</span>
              <input
                className="field"
                type="password"
                value={form.api_key ?? ""}
                onChange={(event) => setForm({ ...form, api_key: event.target.value })}
                placeholder={editing ? "留空表示不修改原 Key" : "Ollama 可留空"}
              />
            </label>
          </div>

          {editing && (
            <label className="flex items-center gap-2 text-sm text-slate-700">
              <input
                type="checkbox"
                checked={Boolean(form.clear_api_key)}
                onChange={(event) => setForm({ ...form, clear_api_key: event.target.checked })}
              />
              清空 API Key
            </label>
          )}

          <div className="flex flex-wrap gap-4">
            <label className="flex items-center gap-2 text-sm text-slate-700">
              <input
                type="checkbox"
                checked={form.enabled}
                disabled={isEditingDefault}
                onChange={(event) => setForm({ ...form, enabled: event.target.checked })}
              />
              启用
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-700">
              <input
                type="checkbox"
                checked={form.is_default}
                disabled={isEditingDefault}
                onChange={(event) => setForm({ ...form, is_default: event.target.checked })}
              />
              设为默认
            </label>
          </div>

          <div className="rounded-md bg-slate-50 px-3 py-2 text-xs leading-5 text-slate-500">
            API Key 不会在前端回显；编辑时留空表示保留原 Key。Ollama 本地模型可不填写 API Key。
            {isEditingDefault && " 当前默认模型必须保持启用和默认状态，如需更换请先将其他启用配置设为默认。"}
          </div>

          <div className="flex justify-end gap-3">
            <button className="btn-secondary" type="button" onClick={() => setModalOpen(false)}>
              取消
            </button>
            <button className="btn-primary" type="submit" disabled={saving}>
              {saving ? "保存中..." : "保存"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
