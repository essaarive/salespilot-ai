import type { IntentLevel, IntentType } from "../types";

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

export function formatIntentType(value: string) {
  return intentTypeLabel[value as IntentType] ?? (value || "未知");
}

export function formatIntentLevel(value: string) {
  return intentLevelLabel[value as IntentLevel] ?? (value || "未知");
}

export function formatStatus(value: string) {
  return leadStatusLabel[value] ?? (value || "未知");
}

export function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function shortText(value: string, length = 80) {
  return value.length > length ? `${value.slice(0, length)}...` : value;
}
