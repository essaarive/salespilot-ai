import { Eye, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "../api/client";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";
import type { Conversation } from "../types";
import { cleanAIText, formatDateTime, formatIntentLevel, formatIntentType, shortText } from "./helpers";

export default function Conversations() {
  const [items, setItems] = useState<Conversation[]>([]);
  const [levelFilter, setLevelFilter] = useState("");
  const [selected, setSelected] = useState<Conversation | null>(null);
  const [initialLoading, setInitialLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const loadData = async () => {
    try {
      setItems(await api.listConversations());
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setInitialLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDelete = async (item: Conversation) => {
    if (!window.confirm(`确认删除 ${item.customer_name} 的对话吗？`)) return;
    setError("");
    setDeletingId(item.id);
    try {
      await api.deleteConversation(item.id);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "删除失败");
    } finally {
      setDeletingId(null);
    }
  };

  const filteredItems = items.filter((item) => !levelFilter || item.intent_level === levelFilter);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-950">对话记录</h2>
        <p className="mt-1 text-sm text-slate-500">查看客户咨询、AI 回复和意向识别结果。</p>
      </div>
      {error && <p className="rounded-md bg-red-50 p-3 text-sm text-red-600">{error}</p>}

      <div className="flex flex-wrap gap-3">
        <select className="field max-w-xs" value={levelFilter} onChange={(event) => setLevelFilter(event.target.value)}>
          <option value="">全部意向</option>
          <option value="high">high</option>
          <option value="medium">medium</option>
          <option value="low">low</option>
        </select>
      </div>

      {initialLoading ? (
        <div className="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
          对话记录加载中...
        </div>
      ) : (
        <DataTable
        data={filteredItems}
        emptyText="暂无对话记录，可先在 AI 对话测试页生成一次咨询"
        columns={[
          { key: "customer", title: "客户", render: (row) => <span className="font-medium text-slate-950">{row.customer_name}</span> },
          { key: "contact", title: "联系方式", render: (row) => row.customer_contact || "-" },
          { key: "question", title: "问题", render: (row) => shortText(row.question, 52) },
          { key: "answer", title: "回复摘要", render: (row) => <span className="text-slate-600">{shortText(cleanAIText(row.answer), 70)}</span> },
          { key: "intent", title: "意向类型", render: (row) => formatIntentType(row.intent_type) },
          {
            key: "level",
            title: "意向等级",
            render: (row) => (
              <span className="rounded bg-brand-50 px-2 py-1 text-xs text-brand-700">{formatIntentLevel(row.intent_level)}</span>
            ),
          },
          { key: "created", title: "创建时间", render: (row) => formatDateTime(row.created_at) },
          {
            key: "actions",
            title: "操作",
            render: (row) => (
              <div className="flex gap-2">
                <button className="btn-secondary px-2" type="button" onClick={() => setSelected(row)} title="查看详情">
                  <Eye size={15} />
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

      <Modal title="对话详情" open={Boolean(selected)} onClose={() => setSelected(null)}>
        {selected && (
          <div className="space-y-4 text-sm">
            <div className="grid gap-3 sm:grid-cols-2">
              <p><span className="text-slate-500">客户：</span>{selected.customer_name}</p>
              <p><span className="text-slate-500">联系方式：</span>{selected.customer_contact || "-"}</p>
              <p><span className="text-slate-500">意向类型：</span>{formatIntentType(selected.intent_type)}</p>
              <p><span className="text-slate-500">意向等级：</span>{formatIntentLevel(selected.intent_level)}</p>
            </div>
            <div>
              <p className="mb-2 font-medium text-slate-700">客户问题</p>
              <div className="rounded-md bg-slate-50 p-4 leading-7 text-slate-700">{selected.question}</div>
            </div>
            <div>
              <p className="mb-2 font-medium text-slate-700">AI 回复</p>
              <div className="whitespace-pre-line rounded-md bg-slate-50 p-4 leading-7 text-slate-700">{cleanAIText(selected.answer)}</div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
