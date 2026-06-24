import { Edit3, Plus, Trash2 } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import { api } from "../api/client";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";
import type { Lead } from "../types";
import { formatDateTime, formatHandoffReason, formatIntentLevel, formatStatus, shortText } from "./helpers";

type LeadForm = Omit<Lead, "id" | "created_at" | "updated_at">;

const emptyLead: LeadForm = {
  customer_name: "",
  customer_contact: "",
  requirement: "",
  intent_level: "high",
  status: "new",
  remark: "",
  requires_handoff: false,
  handoff_reason: null,
};

export default function Leads() {
  const [items, setItems] = useState<Lead[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [levelFilter, setLevelFilter] = useState("");
  const [editing, setEditing] = useState<Lead | null>(null);
  const [form, setForm] = useState<LeadForm>(emptyLead);
  const [modalOpen, setModalOpen] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const loadData = async () => {
    try {
      setItems(await api.listLeads());
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setInitialLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyLead);
    setModalOpen(true);
  };

  const openEdit = (lead: Lead) => {
    setEditing(lead);
    setForm({
      customer_name: lead.customer_name,
      customer_contact: lead.customer_contact,
      requirement: lead.requirement,
      intent_level: lead.intent_level,
      status: lead.status,
      remark: lead.remark,
      requires_handoff: Boolean(lead.requires_handoff),
      handoff_reason: lead.handoff_reason ?? null,
    });
    setModalOpen(true);
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      if (editing) {
        await api.updateLead(editing.id, form);
      } else {
        await api.createLead(form);
      }
      setModalOpen(false);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存失败");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (lead: Lead) => {
    if (!window.confirm(`确认删除 ${lead.customer_name} 的线索吗？`)) return;
    setError("");
    setDeletingId(lead.id);
    try {
      await api.deleteLead(lead.id);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "删除失败");
    } finally {
      setDeletingId(null);
    }
  };

  const filteredItems = items.filter((item) => {
    const statusMatched = !statusFilter || item.status === statusFilter;
    const levelMatched = !levelFilter || item.intent_level === levelFilter;
    return statusMatched && levelMatched;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-950">客户线索</h2>
          <p className="mt-1 text-sm text-slate-500">管理高意向客户需求、状态和跟进备注。</p>
        </div>
        <button className="btn-primary" type="button" onClick={openCreate}>
          <Plus size={16} />
          新增线索
        </button>
      </div>
      {error && <p className="rounded-md bg-red-50 p-3 text-sm text-red-600">{error}</p>}

      <div className="flex flex-wrap gap-3">
        <select className="field max-w-xs" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
          <option value="">全部状态</option>
          <option value="new">new</option>
          <option value="contacted">contacted</option>
          <option value="following">following</option>
          <option value="closed">closed</option>
          <option value="invalid">invalid</option>
        </select>
        <select className="field max-w-xs" value={levelFilter} onChange={(event) => setLevelFilter(event.target.value)}>
          <option value="">全部意向</option>
          <option value="high">high</option>
          <option value="medium">medium</option>
          <option value="low">low</option>
        </select>
      </div>

      {initialLoading ? (
        <div className="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
          客户线索加载中...
        </div>
      ) : (
        <DataTable
        data={filteredItems}
        emptyText="暂无客户线索，可先通过 AI 对话测试生成一条高意向线索"
        columns={[
          { key: "customer", title: "客户", render: (row) => <span className="font-medium text-slate-950">{row.customer_name}</span> },
          { key: "contact", title: "联系方式", render: (row) => row.customer_contact || "-" },
          { key: "requirement", title: "需求", render: (row) => shortText(row.requirement, 70) },
          {
            key: "level",
            title: "意向等级",
            render: (row) => (
              <span
                className={[
                  "rounded px-2 py-1 text-xs font-medium",
                  row.intent_level === "high"
                    ? "bg-amber-50 text-amber-700 ring-1 ring-amber-200"
                    : "bg-brand-50 text-brand-700",
                ].join(" ")}
              >
                {formatIntentLevel(row.intent_level)}
              </span>
            ),
          },
          { key: "status", title: "状态", render: (row) => <span className="rounded bg-slate-100 px-2 py-1 text-xs">{formatStatus(row.status)}</span> },
          {
            key: "handoff",
            title: "人工跟进",
            render: (row) =>
              row.requires_handoff ? (
                <span className="rounded bg-orange-50 px-2 py-1 text-xs font-medium text-orange-700">
                  需人工：{formatHandoffReason(row.handoff_reason)}
                </span>
              ) : (
                <span className="text-slate-400">-</span>
              ),
          },
          { key: "remark", title: "备注", render: (row) => shortText(row.remark || "-", 42) },
          { key: "created", title: "创建时间", render: (row) => formatDateTime(row.created_at) },
          {
            key: "actions",
            title: "操作",
            render: (row) => (
              <div className="flex gap-2">
                <button className="btn-secondary px-2" type="button" onClick={() => openEdit(row)} title="编辑">
                  <Edit3 size={15} />
                </button>
                <button
                  className="btn-danger px-2"
                  type="button"
                  onClick={() => handleDelete(row)}
                  title="删除"
                  disabled={deletingId === row.id}
                >
                  {deletingId === row.id ? "删除中" : <Trash2 size={15} />}
                </button>
              </div>
            ),
          },
        ]}
      />
      )}

      <Modal title={editing ? "编辑线索" : "新增线索"} open={modalOpen} onClose={() => setModalOpen(false)}>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">客户姓名</span>
              <input className="field" value={form.customer_name} onChange={(event) => setForm({ ...form, customer_name: event.target.value })} required />
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">联系方式</span>
              <input className="field" value={form.customer_contact} onChange={(event) => setForm({ ...form, customer_contact: event.target.value })} />
            </label>
          </div>
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-slate-700">需求</span>
            <textarea className="field min-h-28" value={form.requirement} onChange={(event) => setForm({ ...form, requirement: event.target.value })} required />
          </label>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">意向等级</span>
              <select className="field" value={form.intent_level} onChange={(event) => setForm({ ...form, intent_level: event.target.value as Lead["intent_level"] })}>
                <option value="high">高意向</option>
                <option value="medium">中意向</option>
                <option value="low">低意向</option>
              </select>
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">状态</span>
              <select className="field" value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })}>
                <option value="new">new</option>
                <option value="contacted">contacted</option>
                <option value="following">following</option>
                <option value="closed">closed</option>
                <option value="invalid">invalid</option>
              </select>
            </label>
          </div>
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-slate-700">备注</span>
            <textarea className="field min-h-24" value={form.remark} onChange={(event) => setForm({ ...form, remark: event.target.value })} />
          </label>
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
