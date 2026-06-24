import type {
  ChatResponse,
  AIModelConfig,
  AIModelConfigPayload,
  AIModelConfigTestResult,
  Conversation,
  DashboardSummary,
  DocumentDetail,
  DocumentRecord,
  KnowledgeItem,
  Lead,
  LoginResponse,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";
const TOKEN_KEY = "salespilot_token";
const BACKEND_CONNECTION_ERROR = "无法连接后端服务，请确认前端代理配置和后端服务是否已启动。";

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

  const response = await fetchWithConnectionHint(`${API_BASE_URL}${path}`, {
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
    throw new Error(await readErrorMessage(response));
  }

  return response.json() as Promise<T>;
}

async function publicRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetchWithConnectionHint(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  return response.json() as Promise<T>;
}

async function uploadRequest<T>(path: string, formData: FormData): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {};

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetchWithConnectionHint(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!response.ok) {
    if (response.status === 401) {
      clearToken();
      if (window.location.pathname !== "/login") {
        window.location.assign("/login");
      }
    }
    throw new Error(await readErrorMessage(response));
  }

  return response.json() as Promise<T>;
}

async function fetchWithConnectionHint(input: RequestInfo | URL, init?: RequestInit) {
  try {
    return await fetch(input, init);
  } catch (error) {
    console.error("API request failed before receiving a response:", error);
    throw new Error(BACKEND_CONNECTION_ERROR);
  }
}

async function readErrorMessage(response: Response) {
  const detail = await response.json().catch(() => ({}));
  if (typeof detail.detail === "string" && detail.detail) {
    return detail.detail;
  }
  if (response.status >= 500) {
    return BACKEND_CONNECTION_ERROR;
  }
  return "请求失败";
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
  listDocuments: (params?: { status?: string; keyword?: string }) => {
    const search = new URLSearchParams();
    if (params?.status) search.set("status", params.status);
    if (params?.keyword) search.set("keyword", params.keyword);
    const query = search.toString();
    return request<DocumentRecord[]>(`/api/documents${query ? `?${query}` : ""}`);
  },
  uploadDocument: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return uploadRequest<DocumentDetail>("/api/documents/upload", formData);
  },
  getDocument: (id: number) => request<DocumentDetail>(`/api/documents/${id}`),
  deleteDocument: (id: number) => request<{ message: string }>(`/api/documents/${id}`, { method: "DELETE" }),
  chat: (payload: { customer_name: string; customer_contact: string; question: string }) =>
    request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  publicChat: (payload: { customer_name: string; customer_contact: string; question: string }) =>
    publicRequest<ChatResponse>("/api/public/chat", {
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
  getAIConfigs: () => request<AIModelConfig[]>("/api/ai-settings/configs"),
  getCurrentAIConfig: () => request<AIModelConfig>("/api/ai-settings/current"),
  createAIConfig: (payload: AIModelConfigPayload) =>
    request<AIModelConfig>("/api/ai-settings/configs", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateAIConfig: (id: number, payload: Partial<AIModelConfigPayload>) =>
    request<AIModelConfig>(`/api/ai-settings/configs/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  setDefaultAIConfig: (id: number) =>
    request<AIModelConfig>(`/api/ai-settings/configs/${id}/set-default`, { method: "POST" }),
  testAIConfig: (id: number) =>
    request<AIModelConfigTestResult>(`/api/ai-settings/configs/${id}/test`, { method: "POST" }),
  deleteAIConfig: (id: number) =>
    request<{ message: string }>(`/api/ai-settings/configs/${id}`, { method: "DELETE" }),
};
