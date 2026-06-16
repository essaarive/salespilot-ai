import { Edit3, Plus, Trash2 } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { api } from "../api/client";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";
import type { KnowledgeItem } from "../types";
import { formatDateTime, formatStatus, shortText } from "./helpers";

type KnowledgeForm = Omit<KnowledgeItem, "id" | "created_at" | "updated_at">;

const emptyForm: KnowledgeForm = {
  title: "",
  category: "价格",
  content: "",
  keywords: "",
  status: "active",
};

export default function Knowledge() {
  const [allItems, setAllItems] = useState<KnowledgeItem[]>([]);
  const [items, setItems] = useState<KnowledgeItem[]>([]);
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState<KnowledgeItem | null>(null);
  const [form, setForm] = useState<KnowledgeForm>(emptyForm);
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const categories = useMemo(
    () => Array.from(new Set(allItems.map((item) => item.category))).filter(Boolean),
    [allItems],
  );

  const filteredItems = useMemo(() => {
    const keyword = search.trim().toLowerCase();
    return allItems.filter((item) => {
      const categoryMatched = !category || item.category === category;
      const keywordMatched =
        !keyword ||
        [item.title, item.category, item.keywords, item.content].some((value) =>
          value.toLowerCase().includes(keyword),
        );
      return categoryMatched && keywordMatched;
    });
  }, [allItems, category, search]);

  const loadData = async () => {
    setError("");
    try {
      const result = await api.listKnowledge();
      setAllItems(result);
      setItems(result);
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
    setForm(emptyForm);
    setModalOpen(true);
  };

  const openEdit = (item: KnowledgeItem) => {
    setEditing(item);
    setForm({
      title: item.title,
      category: item.category,
      content: item.content,
      keywords: item.keywords,
      status: item.status,
    });
    setModalOpen(true);
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      if (editing) {
        await api.updateKnowledge(editing.id, form);
      } else {
        await api.createKnowledge(form);
      }
      setModalOpen(false);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存失败");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (item: KnowledgeItem) => {
    if (!window.confirm(`确认删除「${item.title}」吗？`)) return;
    setError("");
    setDeletingId(item.id);
    try {
      await api.deleteKnowledge(item.id);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "删除失败");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-950">知识库管理</h2>
          <p className="mt-1 text-sm text-slate-500">维护销售客服回复可引用的业务资料。</p>
        </div>
        <button className="btn-primary" type="button" onClick={openCreate}>
          <Plus size={16} />
          新增知识
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <input
          className="field max-w-sm"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="搜索标题、分类、关键词或内容"
        />
        <select className="field max-w-xs" value={category} onChange={(event) => setCategory(event.target.value)}>
          <option value="">全部分类</option>
          {categories.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
        {error && <p className="text-sm text-red-600">{error}</p>}
      </div>

      {initialLoading ? (
        <div className="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
          知识库加载中...
        </div>
      ) : (
        <DataTable
        data={filteredItems}
        emptyText="暂无知识库内容，请先新增一条企业资料"
        columns={[
          { key: "title", title: "标题", render: (row) => <span className="font-medium text-slate-950">{row.title}</span> },
          {
            key: "category",
            title: "分类",
            render: (row) => <span className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-600">{row.category}</span>,
          },
          {
            key: "content",
            title: "内容",
            render: (row) => <span className="text-slate-600">{shortText(row.content, 72)}</span>,
          },
          { key: "keywords", title: "关键词", render: (row) => row.keywords },
          {
            key: "status",
            title: "状态",
            render: (row) => (
              <span
                className={[
                  "rounded px-2 py-1 text-xs",
                  row.status === "active" ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-600",
                ].join(" ")}
              >
                {formatStatus(row.status)}
              </span>
            ),
          },
          { key: "updated", title: "更新时间", render: (row) => formatDateTime(row.updated_at) },
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

      <Modal title={editing ? "编辑知识" : "新增知识"} open={modalOpen} onClose={() => setModalOpen(false)}>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">标题</span>
              <input className="field" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required />
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">分类</span>
              <input className="field" value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })} required />
            </label>
          </div>
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-slate-700">内容</span>
            <textarea
              className="field min-h-32"
              value={form.content}
              onChange={(event) => setForm({ ...form, content: event.target.value })}
              required
            />
          </label>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">关键词</span>
              <input className="field" value={form.keywords} onChange={(event) => setForm({ ...form, keywords: event.target.value })} />
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">状态</span>
              <select className="field" value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })}>
                <option value="active">active</option>
                <option value="inactive">inactive</option>
              </select>
            </label>
          </div>
          <div className="flex justify-end gap-3">
            <button className="btn-secondary" type="button" onClick={() => setModalOpen(false)}>
              取消
            </button>
            <button className="btn-primary" type="submit" disabled={loading}>
              {loading ? "保存中..." : "保存"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
