from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, model_validator

IntentType = Literal["pricing", "cooperation", "product", "delivery", "after_sales", "greeting", "irrelevant"]
IntentLevel = Literal["high", "medium", "low"]
KnowledgeStatus = Literal["active", "inactive"]
LeadStatus = Literal["new", "contacted", "following", "qualified", "closed", "invalid"]
AIProvider = Literal["deepseek", "openai", "qwen", "zhipu", "ollama", "custom"]


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


class KnowledgeOut(KnowledgeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
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


class ConversationOut(BaseModel):
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


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    requirement: Optional[str] = None
    intent_level: Optional[IntentLevel] = None
    status: Optional[LeadStatus] = None
    remark: Optional[str] = None

    @model_validator(mode="after")
    def reject_explicit_nulls(self) -> "LeadUpdate":
        for field_name in self.model_fields_set:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self


class LeadOut(LeadBase):
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


class AIModelConfigOut(AIModelConfigBase):
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
