import type {
  ChatResponse,
  Conversation,
  DashboardSummary,
  KnowledgeItem,
  Lead,
  LoginResponse,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const TOKEN_KEY = "salespilot_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      clearToken();
      if (window.location.pathname !== "/login") {
        window.location.assign("/login");
      }
    }
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail ?? "请求失败");
  }

  return response.json() as Promise<T>;
}

export const api = {
  login: (username: string, password: string) =>
    request<LoginResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  dashboard: () => request<DashboardSummary>("/api/dashboard/summary"),
  listKnowledge: (category?: string) =>
    request<KnowledgeItem[]>(`/api/knowledge${category ? `?category=${encodeURIComponent(category)}` : ""}`),
  createKnowledge: (payload: Omit<KnowledgeItem, "id" | "created_at" | "updated_at">) =>
    request<KnowledgeItem>("/api/knowledge", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateKnowledge: (id: number, payload: Omit<KnowledgeItem, "id" | "created_at" | "updated_at">) =>
    request<KnowledgeItem>(`/api/knowledge/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteKnowledge: (id: number) => request<{ message: string }>(`/api/knowledge/${id}`, { method: "DELETE" }),
  chat: (payload: { customer_name: string; customer_contact: string; question: string }) =>
    request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  listConversations: () => request<Conversation[]>("/api/conversations"),
  deleteConversation: (id: number) =>
    request<{ message: string }>(`/api/conversations/${id}`, { method: "DELETE" }),
  listLeads: () => request<Lead[]>("/api/leads"),
  createLead: (payload: Omit<Lead, "id" | "created_at" | "updated_at">) =>
    request<Lead>("/api/leads", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateLead: (id: number, payload: Partial<Omit<Lead, "id" | "created_at" | "updated_at">>) =>
    request<Lead>(`/api/leads/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteLead: (id: number) => request<{ message: string }>(`/api/leads/${id}`, { method: "DELETE" }),
};
