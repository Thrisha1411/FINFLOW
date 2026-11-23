from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

class TransactionCreate(BaseModel):
    amount: Decimal
    merchant_name: str
    currency: str = "USD"
    description: Optional[str] = None
    category_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    payment_method: str = "CORPORATE_CARD"

class TransactionEventResponse(BaseModel):
    id: str
    from_status: Optional[str]
    to_status: str
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionResponse(BaseModel):
    id: str
    organization_id: str
    reference_id: str
    amount: float
    currency: str
    merchant_name: str
    description: Optional[str]
    category_id: Optional[str]
    status: str
    risk_score: float
    risk_level: str
    payment_method: str
    created_at: datetime
    events: List[TransactionEventResponse] = []

    class Config:
        from_attributes = True

class RefundCreate(BaseModel):
    transaction_id: str
    amount: Decimal
    reason: str

class RefundResponse(BaseModel):
    id: str
    transaction_id: str
    amount: float
    currency: str
    reason: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
