import { BookOpenText, MessageCircle, Star, UsersRound } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "../api/client";
import StatCard from "../components/StatCard";
import type { DashboardSummary } from "../types";
import { formatDateTime, formatIntentLevel, formatIntentType } from "./helpers";

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.dashboard().then(setSummary).catch((err) => setError(err.message));
  }, []);

  if (error) return <p className="rounded-md bg-red-50 p-4 text-sm text-red-600">仪表盘加载失败：{error}</p>;
  if (!summary) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-slate-950">仪表盘</h2>
          <p className="mt-1 text-sm text-slate-500">加载核心业务数据中...</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[1, 2, 3, 4].map((item) => (
            <div key={item} className="h-28 animate-pulse rounded-lg border border-slate-200 bg-white p-5">
              <div className="h-4 w-24 rounded bg-slate-100" />
              <div className="mt-5 h-8 w-16 rounded bg-slate-100" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-950">仪表盘</h2>
        <p className="mt-1 text-sm text-slate-500">查看知识库、咨询和销售线索的核心数据。</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="知识库数量" value={summary.knowledge_count} icon={BookOpenText} />
        <StatCard label="今日咨询数" value={summary.today_conversations} icon={MessageCircle} />
        <StatCard label="高意向线索数" value={summary.high_intent_leads} icon={Star} />
        <StatCard label="总线索数" value={summary.total_leads} icon={UsersRound} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <section className="rounded-lg border border-slate-200 bg-white">
          <div className="border-b border-slate-100 px-5 py-4">
            <h3 className="font-semibold text-slate-950">最近咨询</h3>
            <p className="mt-1 text-sm text-slate-500">最近 5 条客户问答记录。</p>
          </div>
          <div className="divide-y divide-slate-100">
            {summary.recent_conversations.length === 0 ? (
              <p className="p-5 text-sm text-slate-500">暂无咨询记录，去 AI 对话测试页生成一条演示数据。</p>
            ) : (
              summary.recent_conversations.map((item) => (
                <div key={item.id} className="grid gap-3 p-5 lg:grid-cols-[1fr_180px]">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="font-medium text-slate-950">{item.customer_name}</p>
                      <span className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-600">
                        {formatIntentType(item.intent_type)}
                      </span>
                      <span className="rounded bg-brand-50 px-2 py-1 text-xs text-brand-700">
                        {formatIntentLevel(item.intent_level)}
                      </span>
                    </div>
                    <p className="mt-2 line-clamp-2 text-sm text-slate-600">{item.question}</p>
                  </div>
                  <p className="text-sm text-slate-500 lg:text-right">{formatDateTime(item.created_at)}</p>
                </div>
              ))
            )}
          </div>
        </section>

        <div className="space-y-6">
          <section className="rounded-lg border border-amber-200 bg-amber-50 p-5">
            <p className="text-sm font-medium text-amber-800">高意向线索提醒</p>
            <p className="mt-3 text-3xl font-semibold text-amber-950">{summary.high_intent_leads}</p>
            <p className="mt-2 text-sm leading-6 text-amber-800">
              high 级别线索建议优先跟进，可在客户线索页查看需求和联系方式。
            </p>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-5">
            <h3 className="font-semibold text-slate-950">意向等级说明</h3>
            <div className="mt-4 space-y-3 text-sm">
              <p><span className="font-medium text-emerald-700">high：</span>报价、合作、购买、上线等强需求</p>
              <p><span className="font-medium text-sky-700">medium：</span>售后、交付、产品细节咨询</p>
              <p><span className="font-medium text-slate-600">low：</span>无关问题或弱需求</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
