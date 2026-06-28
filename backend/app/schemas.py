import re
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator, model_validator

from app.core.timezone import format_datetime

IntentType = Literal["pricing", "cooperation", "product", "delivery", "after_sales", "greeting", "irrelevant"]
IntentLevel = Literal["high", "medium", "low"]
ScopeType = Literal["business_related", "sales_adjacent", "general_chat", "out_of_scope", "unsafe"]
RetrievalConfidence = Literal["high", "medium", "low", "none"]
AnswerBasis = Literal["knowledge", "general_guidance", "fallback"]
HandoffReason = Literal[
    "customer_requested_human",
    "knowledge_not_found",
    "special_quote",
    "custom_requirement",
    "complaint_or_risk",
]
KnowledgeStatus = Literal["active", "inactive"]
LeadStatus = Literal["new", "contacted", "following", "qualified", "closed", "invalid"]
AIProvider = Literal["deepseek", "openai", "qwen", "zhipu", "ollama", "volcengine_ark", "custom"]
DocumentStatus = Literal["pending", "parsing", "success", "failed"]
KnowledgeSourceType = Literal["manual", "document"]
WidgetPosition = Literal["left", "right"]


class DateTimeSerializedModel(BaseModel):
    @field_serializer("created_at", "updated_at", when_used="json", check_fields=False)
    def serialize_datetime(self, value: datetime) -> str:
        return format_datetime(value)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str
    role: str


class KnowledgeBase(BaseModel):
    title: str
    category: str
    content: str
    keywords: str = ""
    status: KnowledgeStatus = "active"


class KnowledgeCreate(KnowledgeBase):
    pass


class KnowledgeUpdate(KnowledgeBase):
    pass


class KnowledgeOut(DateTimeSerializedModel, KnowledgeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_type: KnowledgeSourceType = "manual"
    source_document_id: Optional[int] = None
    source_file_name: Optional[str] = None
    chunk_index: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class ChatRequest(BaseModel):
    customer_name: str
    customer_contact: str = ""
    question: str


class ChatResponse(BaseModel):
    answer: str
    intent_type: IntentType
    intent_level: IntentLevel
    matched_knowledge: List[KnowledgeOut]
    ai_source: Optional[Literal["model", "mock"]] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    scope_type: Optional[ScopeType] = None
    retrieval_confidence: Optional[RetrievalConfidence] = None
    answer_basis: Optional[AnswerBasis] = None
    requires_handoff: bool = False
    handoff_reason: Optional[HandoffReason] = None


class ConversationOut(DateTimeSerializedModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    customer_contact: str
    question: str
    answer: str
    intent_type: IntentType
    intent_level: IntentLevel
    source: str
    created_at: datetime


class LeadBase(BaseModel):
    customer_name: str
    customer_contact: str = ""
    requirement: str
    intent_level: IntentLevel = "high"
    status: LeadStatus = "new"
    remark: str = ""
    requires_handoff: bool = False
    handoff_reason: Optional[HandoffReason] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    requirement: Optional[str] = None
    intent_level: Optional[IntentLevel] = None
    status: Optional[LeadStatus] = None
    remark: Optional[str] = None
    requires_handoff: Optional[bool] = None
    handoff_reason: Optional[HandoffReason] = None

    @model_validator(mode="after")
    def reject_explicit_nulls(self) -> "LeadUpdate":
        for field_name in self.model_fields_set:
            if field_name == "handoff_reason":
                continue
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self


class LeadOut(DateTimeSerializedModel, LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class DashboardSummary(BaseModel):
    knowledge_count: int
    today_conversations: int
    high_intent_leads: int
    total_leads: int
    recent_conversations: List[ConversationOut]


class MessageResponse(BaseModel):
    message: str


class DocumentOut(DateTimeSerializedModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    stored_filename: str
    file_extension: str
    mime_type: str
    file_size: int
    parse_status: DocumentStatus
    parse_error: str = ""
    extracted_text_length: int
    chunk_count: int
    is_enabled: bool = True
    created_at: datetime
    updated_at: datetime


class DocumentDetail(DocumentOut):
    text_preview: str = ""
    knowledge_preview: List[KnowledgeOut] = []


class DocumentToggleRequest(BaseModel):
    is_enabled: bool


class AIModelConfigBase(BaseModel):
    provider: AIProvider
    name: str
    base_url: str
    model: str
    enabled: bool = True
    is_default: bool = False


class AIModelConfigCreate(AIModelConfigBase):
    api_key: str = ""


class AIModelConfigUpdate(BaseModel):
    provider: Optional[AIProvider] = None
    name: Optional[str] = None
    api_key: Optional[str] = None
    clear_api_key: bool = False
    base_url: Optional[str] = None
    model: Optional[str] = None
    enabled: Optional[bool] = None
    is_default: Optional[bool] = None


class AIModelConfigOut(DateTimeSerializedModel, AIModelConfigBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    api_key_masked: bool
    api_key_preview: str
    created_at: datetime
    updated_at: datetime


class AIModelConfigCurrent(AIModelConfigOut):
    pass


class AIModelConfigTestResult(BaseModel):
    success: bool
    message: str
    provider: Optional[str] = None
    model: Optional[str] = None


class CompanySettingsBase(BaseModel):
    company_name: str
    company_short_name: str = ""
    company_logo_url: str = ""
    company_intro: str = ""
    customer_service_name: str
    customer_service_avatar_url: str = ""
    welcome_message: str = ""
    brand_color: str = "#2563EB"
    business_scope: str = ""
    human_contact_phone: str = ""
    human_contact_wechat: str = ""
    human_contact_email: str = ""
    business_hours: str = ""
    handoff_message: str = ""
    forbidden_topics: str = ""
    allowed_embed_domains: str = ""
    widget_position: WidgetPosition = "right"

    @field_validator(
        "company_name",
        "company_short_name",
        "company_logo_url",
        "company_intro",
        "customer_service_name",
        "customer_service_avatar_url",
        "welcome_message",
        "brand_color",
        "business_scope",
        "human_contact_phone",
        "human_contact_wechat",
        "human_contact_email",
        "business_hours",
        "handoff_message",
        "forbidden_topics",
        "allowed_embed_domains",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @model_validator(mode="after")
    def validate_required_and_color(self) -> "CompanySettingsBase":
        if not self.company_name:
            raise ValueError("企业名称不能为空")
        if not self.customer_service_name:
            raise ValueError("客服名称不能为空")
        if not self.brand_color:
            self.brand_color = "#2563EB"
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", self.brand_color):
            raise ValueError("品牌主色必须是合法 Hex 颜色，例如 #2563EB")
        return self


class CompanySettingsUpdate(CompanySettingsBase):
    pass


class CompanySettingsOut(DateTimeSerializedModel, CompanySettingsBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class PublicCompanySettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_name: str
    company_short_name: str = ""
    company_logo_url: str = ""
    company_intro: str = ""
    customer_service_name: str
    customer_service_avatar_url: str = ""
    welcome_message: str = ""
    brand_color: str = "#2563EB"
    business_scope: str = ""
    human_contact_phone: str = ""
    human_contact_wechat: str = ""
    human_contact_email: str = ""
    business_hours: str = ""
    handoff_message: str = ""
