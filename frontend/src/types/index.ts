export interface LoginResponse {
  token: string;
  username: string;
  role: string;
}

export interface KnowledgeItem {
  id: number;
  title: string;
  category: string;
  content: string;
  keywords: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: number;
  customer_name: string;
  customer_contact: string;
  question: string;
  answer: string;
  intent_type: IntentType;
  intent_level: IntentLevel;
  source: string;
  created_at: string;
}

export interface Lead {
  id: number;
  customer_name: string;
  customer_contact: string;
  requirement: string;
  intent_level: IntentLevel;
  status: string;
  remark: string;
  created_at: string;
  updated_at: string;
}

export type IntentType =
  | "pricing"
  | "cooperation"
  | "product"
  | "delivery"
  | "after_sales"
  | "greeting"
  | "irrelevant";

export type IntentLevel = "high" | "medium" | "low";

export interface DashboardSummary {
  knowledge_count: number;
  today_conversations: number;
  high_intent_leads: number;
  total_leads: number;
  recent_conversations: Conversation[];
}

export interface ChatResponse {
  answer: string;
  intent_type: IntentType;
  intent_level: IntentLevel;
  matched_knowledge: KnowledgeItem[];
}

export type AIProvider = "deepseek" | "openai" | "qwen" | "zhipu" | "ollama" | "custom";

export interface AIModelConfig {
  id: number;
  provider: AIProvider;
  name: string;
  base_url: string;
  model: string;
  enabled: boolean;
  is_default: boolean;
  api_key_masked: boolean;
  api_key_preview: string;
  created_at: string;
  updated_at: string;
}

export interface AIModelConfigPayload {
  provider: AIProvider;
  name: string;
  base_url: string;
  model: string;
  api_key?: string;
  clear_api_key?: boolean;
  enabled: boolean;
  is_default: boolean;
}

export interface AIModelConfigTestResult {
  success: boolean;
  message: string;
  provider?: string;
  model?: string;
}
