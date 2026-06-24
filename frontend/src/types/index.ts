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
  source_type?: "manual" | "document";
  source_document_id?: number | null;
  source_file_name?: string | null;
  chunk_index?: number | null;
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
  requires_handoff?: boolean;
  handoff_reason?: HandoffReason | null;
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
export type ScopeType = "business_related" | "sales_adjacent" | "general_chat" | "out_of_scope" | "unsafe";
export type RetrievalConfidence = "high" | "medium" | "low" | "none";
export type AnswerBasis = "knowledge" | "general_guidance" | "fallback";
export type HandoffReason =
  | "customer_requested_human"
  | "knowledge_not_found"
  | "special_quote"
  | "custom_requirement"
  | "complaint_or_risk";

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
  ai_source?: "model" | "mock";
  provider?: string;
  model?: string;
  scope_type?: ScopeType;
  retrieval_confidence?: RetrievalConfidence;
  answer_basis?: AnswerBasis;
  requires_handoff?: boolean;
  handoff_reason?: HandoffReason | null;
}

export type AIProvider = "deepseek" | "openai" | "qwen" | "zhipu" | "ollama" | "volcengine_ark" | "custom";

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

export type DocumentParseStatus = "pending" | "parsing" | "success" | "failed";

export interface DocumentRecord {
  id: number;
  original_filename: string;
  stored_filename: string;
  file_extension: string;
  mime_type: string;
  file_size: number;
  parse_status: DocumentParseStatus;
  parse_error: string;
  extracted_text_length: number;
  chunk_count: number;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface DocumentDetail extends DocumentRecord {
  text_preview: string;
  knowledge_preview: KnowledgeItem[];
}

export interface PublicCompanySettings {
  company_name: string;
  company_short_name: string;
  company_logo_url: string;
  company_intro: string;
  customer_service_name: string;
  customer_service_avatar_url: string;
  welcome_message: string;
  brand_color: string;
  business_scope: string;
  human_contact_phone: string;
  human_contact_wechat: string;
  human_contact_email: string;
  business_hours: string;
  handoff_message: string;
}

export interface CompanySettings extends PublicCompanySettings {
  id: number;
  forbidden_topics: string;
  created_at: string;
  updated_at: string;
}

export type CompanySettingsPayload = Omit<CompanySettings, "id" | "created_at" | "updated_at">;
