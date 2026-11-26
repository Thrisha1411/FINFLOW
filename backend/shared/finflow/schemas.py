from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from .models import TransactionStatus


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12)
    full_name: str
    organization_id: str = "demo-org"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: str | None = None


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    requires_mfa: bool = False


class TransactionCreate(BaseModel):
    merchant: str
    amount: float = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    category: str | None = None
    metadata: dict = Field(default_factory=dict)


class TransactionRead(BaseModel):
    id: UUID
    merchant: str
    amount: float
    currency: str
    category: str | None
    status: TransactionStatus
    risk_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class StatusUpdate(BaseModel):
    status: TransactionStatus
    reason: str | None = None


class FraudSignal(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    merchant: str
    category: str | None = None
    prior_24h_count: int = 0
    prior_24h_amount: float = 0


class FraudDecision(BaseModel):
    risk_score: float
    fraud_reason: str
    recommendation: str


class AssistantQuestion(BaseModel):
    question: str
    organization_id: str = "demo-org"


class AssistantAnswer(BaseModel):
    answer: str
    sources: list[str] = []

class ReceiptExtraction(BaseModel):
    merchant: str
    amount: float
    tax: float
    category: str
    date: str
