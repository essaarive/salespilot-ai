import type { AnswerBasis, DocumentParseStatus, HandoffReason, IntentLevel, IntentType, RetrievalConfidence, ScopeType } from "../types";

export const intentTypeLabel: Record<IntentType, string> = {
  pricing: "询价",
  cooperation: "合作咨询",
  product: "产品咨询",
  delivery: "交付周期",
  after_sales: "售后问题",
  greeting: "问候",
  irrelevant: "无关问题",
};

export const intentLevelLabel: Record<IntentLevel, string> = {
  high: "高意向",
  medium: "中意向",
  low: "低意向",
};

export const leadStatusLabel: Record<string, string> = {
  new: "new",
  contacted: "contacted",
  following: "following",
  qualified: "qualified",
  closed: "closed",
  invalid: "invalid",
};

export const scopeTypeLabel: Record<ScopeType, string> = {
  business_related: "业务相关",
  sales_adjacent: "销售相关",
  general_chat: "闲聊/通用问题",
  out_of_scope: "无关问题",
  unsafe: "风险问题",
};

export const documentStatusLabel: Record<DocumentParseStatus, string> = {
  pending: "等待解析",
  parsing: "正在解析",
  success: "解析成功",
  failed: "解析失败",
};

export const retrievalConfidenceLabel: Record<RetrievalConfidence, string> = {
  high: "高",
  medium: "中",
  low: "低",
  none: "无",
};

export const answerBasisLabel: Record<AnswerBasis, string> = {
  knowledge: "企业知识库",
  general_guidance: "通用业务引导",
  fallback: "人工兜底",
};

export const handoffReasonLabel: Record<HandoffReason, string> = {
  customer_requested_human: "客户要求人工",
  knowledge_not_found: "资料未找到可靠答案",
  special_quote: "特殊报价",
  custom_requirement: "复杂定制需求",
  complaint_or_risk: "投诉或售后风险",
};

export function formatIntentType(value: string) {
  return intentTypeLabel[value as IntentType] ?? (value || "未知");
}

export function formatIntentLevel(value: string) {
  return intentLevelLabel[value as IntentLevel] ?? (value || "未知");
}

export function formatStatus(value: string) {
  return leadStatusLabel[value] ?? (value || "未知");
}

export function formatScopeType(value?: string) {
  return value ? scopeTypeLabel[value as ScopeType] ?? value : "未知";
}

export function formatDocumentStatus(value: string) {
  return documentStatusLabel[value as DocumentParseStatus] ?? (value || "未知");
}

export function formatRetrievalConfidence(value?: string) {
  return value ? retrievalConfidenceLabel[value as RetrievalConfidence] ?? value : "未知";
}

export function formatAnswerBasis(value?: string) {
  return value ? answerBasisLabel[value as AnswerBasis] ?? value : "未知";
}

export function formatHandoffReason(value?: string | null) {
  return value ? handoffReasonLabel[value as HandoffReason] ?? value : "需人工确认";
}

export function formatFileSize(size: number) {
  if (!Number.isFinite(size) || size <= 0) return "-";
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

export function cleanDocumentSourceText(value: string) {
  return value
    .replace(/^来源文件：.*$/gm, "")
    .replace(/^片段：.*$/gm, "")
    .replace(/^页码：.*$/gm, "")
    .replace(/^Sheet：.*$/gm, "")
    .replace(/^表格：.*$/gm, "")
    .replace(/^正文：/gm, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

const APP_DISPLAY_TIME_ZONE = "Asia/Shanghai";

function parseDateTime(value?: string | null) {
  if (!value) return null;

  const normalized = String(value).trim();
  if (!normalized) return null;

  const hasTimezone = /(?:z|[+-]\d{2}:?\d{2})$/i.test(normalized);
  const isoLike = /^\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}/.test(normalized);
  const date = new Date(hasTimezone || !isoLike ? normalized : `${normalized.replace(" ", "T")}Z`);

  return Number.isNaN(date.getTime()) ? null : date;
}

export function formatDateTime(value?: string | null) {
  const date = parseDateTime(value);
  if (!date) return value || "-";

  const parts = new Intl.DateTimeFormat("zh-CN", {
    timeZone: APP_DISPLAY_TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).formatToParts(date);

  const partMap = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return `${partMap.year}-${partMap.month}-${partMap.day} ${partMap.hour}:${partMap.minute}`;
}

export function cleanAIText(value: string) {
  return value
    .replace(/```([\s\S]*?)```/g, "$1")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/__(.*?)__/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/^\s{0,3}#{1,6}\s*/gm, "")
    .replace(/\*\*/g, "")
    .replace(/```/g, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

export function shortText(value: string, length = 80) {
  return value.length > length ? `${value.slice(0, length)}...` : value;
}
