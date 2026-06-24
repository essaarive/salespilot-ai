import { Edit3, Eye, FileUp, Plus, Trash2 } from "lucide-react";
import { ChangeEvent, FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { api } from "../api/client";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";
import type { DocumentDetail, DocumentRecord, KnowledgeItem } from "../types";
import {
  cleanDocumentSourceText,
  formatDateTime,
  formatDocumentStatus,
  formatFileSize,
  formatStatus,
  shortText,
} from "./helpers";

type KnowledgeForm = Omit<
  KnowledgeItem,
  "id" | "created_at" | "updated_at" | "source_type" | "source_document_id" | "source_file_name" | "chunk_index"
>;
type TabKey = "manual" | "documents";

const emptyForm: KnowledgeForm = {
  title: "",
  category: "价格",
  content: "",
  keywords: "",
  status: "active",
};

function documentStatusClass(status: string) {
  if (status === "success") return "bg-emerald-50 text-emerald-700";
  if (status === "failed") return "bg-red-50 text-red-700";
  if (status === "parsing") return "bg-amber-50 text-amber-700";
  return "bg-slate-100 text-slate-600";
}

export default function Knowledge() {
  const [activeTab, setActiveTab] = useState<TabKey>("manual");
  const [allItems, setAllItems] = useState<KnowledgeItem[]>([]);
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState<KnowledgeItem | null>(null);
  const [form, setForm] = useState<KnowledgeForm>(emptyForm);
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [documentStatus, setDocumentStatus] = useState("");
  const [documentKeyword, setDocumentKeyword] = useState("");
  const [documentsLoading, setDocumentsLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [documentError, setDocumentError] = useState("");
  const [documentDeletingId, setDocumentDeletingId] = useState<number | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<DocumentDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const manualItems = useMemo(
    () => allItems.filter((item) => (item.source_type ?? "manual") !== "document"),
    [allItems],
  );

  const categories = useMemo(
    () => Array.from(new Set(manualItems.map((item) => item.category))).filter(Boolean),
    [manualItems],
  );

  const filteredItems = useMemo(() => {
    const keyword = search.trim().toLowerCase();
    return manualItems.filter((item) => {
      const categoryMatched = !category || item.category === category;
      const keywordMatched =
        !keyword ||
        [item.title, item.category, item.keywords, item.content].some((value) =>
          value.toLowerCase().includes(keyword),
        );
      return categoryMatched && keywordMatched;
    });
  }, [manualItems, category, search]);

  const loadData = async () => {
    setError("");
    try {
      setAllItems(await api.listKnowledge());
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setInitialLoading(false);
    }
  };

  const loadDocuments = async () => {
    setDocumentError("");
    try {
      setDocuments(await api.listDocuments({ status: documentStatus, keyword: documentKeyword.trim() }));
    } catch (err) {
      setDocumentError(err instanceof Error ? err.message : "加载文件失败");
    } finally {
      setDocumentsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [documentStatus]);

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

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;

    setUploading(true);
    setDocumentError("");
    try {
      await api.uploadDocument(file);
      await Promise.all([loadDocuments(), loadData()]);
    } catch (err) {
      setDocumentError(err instanceof Error ? err.message : "上传失败");
    } finally {
      setUploading(false);
    }
  };

  const handleViewDocument = async (document: DocumentRecord) => {
    setDetailLoading(true);
    setDocumentError("");
    try {
      setSelectedDocument(await api.getDocument(document.id));
    } catch (err) {
      setDocumentError(err instanceof Error ? err.message : "加载详情失败");
    } finally {
      setDetailLoading(false);
    }
  };

  const handleDeleteDocument = async (document: DocumentRecord) => {
    if (!window.confirm(`确认删除「${document.original_filename}」及其知识片段吗？`)) return;
    setDocumentError("");
    setDocumentDeletingId(document.id);
    try {
      await api.deleteDocument(document.id);
      await Promise.all([loadDocuments(), loadData()]);
    } catch (err) {
      setDocumentError(err instanceof Error ? err.message : "删除文件失败");
    } finally {
      setDocumentDeletingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-950">知识库管理</h2>
          <p className="mt-1 text-sm text-slate-500">维护销售客服回复可引用的业务资料。</p>
        </div>
        {activeTab === "manual" ? (
          <button className="btn-primary" type="button" onClick={openCreate}>
            <Plus size={16} />
            新增知识
          </button>
        ) : (
          <button className="btn-primary" type="button" onClick={handleUploadClick} disabled={uploading}>
            <FileUp size={16} />
            {uploading ? "上传解析中..." : "上传文件"}
          </button>
        )}
      </div>

      <div className="inline-flex rounded-lg border border-slate-200 bg-white p-1">
        <button
          className={[
            "rounded-md px-4 py-2 text-sm font-medium",
            activeTab === "manual" ? "bg-brand-600 text-white" : "text-slate-600 hover:bg-slate-50",
          ].join(" ")}
          type="button"
          onClick={() => setActiveTab("manual")}
        >
          手动知识库
        </button>
        <button
          className={[
            "rounded-md px-4 py-2 text-sm font-medium",
            activeTab === "documents" ? "bg-brand-600 text-white" : "text-slate-600 hover:bg-slate-50",
          ].join(" ")}
          type="button"
          onClick={() => setActiveTab("documents")}
        >
          文件知识库
        </button>
      </div>

      {activeTab === "manual" ? (
        <>
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
        </>
      ) : (
        <>
          <input
            ref={fileInputRef}
            className="hidden"
            type="file"
            accept=".pdf,.docx,.xlsx,.txt,.md"
            onChange={handleFileChange}
          />
          <div className="rounded-lg border border-brand-100 bg-brand-50 p-4 text-sm leading-6 text-brand-700">
            支持单个 PDF、DOCX、XLSX、TXT、Markdown 文件，最大 10 MB。系统会自动提取文本并写入知识库；扫描版 PDF 暂不支持 OCR。
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <input
              className="field max-w-sm"
              value={documentKeyword}
              onChange={(event) => setDocumentKeyword(event.target.value)}
              placeholder="搜索文件名"
              onKeyDown={(event) => {
                if (event.key === "Enter") loadDocuments();
              }}
            />
            <select
              className="field max-w-xs"
              value={documentStatus}
              onChange={(event) => setDocumentStatus(event.target.value)}
            >
              <option value="">全部状态</option>
              <option value="pending">pending</option>
              <option value="parsing">parsing</option>
              <option value="success">success</option>
              <option value="failed">failed</option>
            </select>
            <button className="btn-secondary" type="button" onClick={loadDocuments} disabled={documentsLoading}>
              查询
            </button>
            {documentError && <p className="text-sm text-red-600">{documentError}</p>}
          </div>

          {documentsLoading ? (
            <div className="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
              文件知识库加载中...
            </div>
          ) : (
            <DataTable
              data={documents}
              emptyText="暂无上传文件，可先上传一份企业资料"
              columns={[
                { key: "name", title: "文件名", render: (row) => <span className="font-medium text-slate-950">{row.original_filename}</span> },
                { key: "type", title: "类型", render: (row) => row.file_extension.replace(".", "").toUpperCase() },
                {
                  key: "status",
                  title: "状态",
                  render: (row) => (
                    <span className={["rounded px-2 py-1 text-xs", documentStatusClass(row.parse_status)].join(" ")}>
                      {formatDocumentStatus(row.parse_status)}
                    </span>
                  ),
                },
                { key: "length", title: "文本长度", render: (row) => row.extracted_text_length || "-" },
                { key: "chunks", title: "知识片段", render: (row) => row.chunk_count || "-" },
                { key: "created", title: "上传时间", render: (row) => formatDateTime(row.created_at) },
                {
                  key: "actions",
                  title: "操作",
                  render: (row) => (
                    <div className="flex gap-2">
                      <button className="btn-secondary px-2" type="button" onClick={() => handleViewDocument(row)} title="查看详情">
                        <Eye size={15} />
                      </button>
                      <button
                        className="btn-danger px-2"
                        type="button"
                        onClick={() => handleDeleteDocument(row)}
                        disabled={documentDeletingId === row.id}
                        title="删除"
                      >
                        {documentDeletingId === row.id ? "删除中" : <Trash2 size={15} />}
                      </button>
                    </div>
                  ),
                },
              ]}
            />
          )}
        </>
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

      <Modal title="文件详情" open={Boolean(selectedDocument) || detailLoading} onClose={() => setSelectedDocument(null)}>
        {detailLoading && <p className="text-sm text-slate-500">文件详情加载中...</p>}
        {selectedDocument && (
          <div className="space-y-5 text-sm">
            <div className="grid gap-3 sm:grid-cols-2">
              <p><span className="text-slate-500">原始文件名：</span>{selectedDocument.original_filename}</p>
              <p><span className="text-slate-500">文件类型：</span>{selectedDocument.file_extension.replace(".", "").toUpperCase()}</p>
              <p><span className="text-slate-500">文件大小：</span>{formatFileSize(selectedDocument.file_size)}</p>
              <p><span className="text-slate-500">上传时间：</span>{formatDateTime(selectedDocument.created_at)}</p>
              <p>
                <span className="text-slate-500">解析状态：</span>
                <span className={["rounded px-2 py-1 text-xs", documentStatusClass(selectedDocument.parse_status)].join(" ")}>
                  {formatDocumentStatus(selectedDocument.parse_status)}
                </span>
              </p>
              <p><span className="text-slate-500">知识片段：</span>{selectedDocument.chunk_count}</p>
            </div>
            {selectedDocument.parse_error && (
              <p className="rounded-md bg-red-50 px-3 py-2 text-red-600">错误原因：{selectedDocument.parse_error}</p>
            )}
            <div>
              <p className="mb-2 font-medium text-slate-700">提取文本预览</p>
              <div className="max-h-64 overflow-y-auto whitespace-pre-line rounded-md bg-slate-50 p-4 leading-7 text-slate-700">
                {cleanDocumentSourceText(selectedDocument.text_preview) || "-"}
              </div>
            </div>
            <div>
              <p className="mb-2 font-medium text-slate-700">知识片段预览</p>
              <div className="space-y-3">
                {selectedDocument.knowledge_preview.length === 0 ? (
                  <p className="rounded-md bg-slate-50 px-4 py-3 text-slate-500">暂无知识片段</p>
                ) : (
                  selectedDocument.knowledge_preview.slice(0, 5).map((item) => (
                    <article key={item.id} className="rounded-md border border-slate-200 p-4">
                      <div className="mb-2 flex flex-wrap items-center gap-2">
                        <span className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-600">片段 {item.chunk_index}</span>
                        <span className="text-xs text-slate-500">{item.title}</span>
                      </div>
                      <p className="whitespace-pre-line leading-6 text-slate-600">{shortText(cleanDocumentSourceText(item.content), 260)}</p>
                    </article>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
