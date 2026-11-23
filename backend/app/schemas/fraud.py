from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class FraudSignalResponse(BaseModel):
    id: str
    rule_code: str
    signal_name: str
    description: str
    severity: str
    weight: float

    class Config:
        from_attributes = True

class FraudCaseResponse(BaseModel):
    id: str
    transaction_id: str
    risk_score: float
    risk_level: str
    recommendation: str
    status: str
    investigator_notes: Optional[str]
    created_at: datetime
    signals: List[FraudSignalResponse] = []

    class Config:
        from_attributes = True

class FraudReviewRequest(BaseModel):
    status: str  # RESOLVED_BENIGN, CONFIRMED_FRAUD, UNDER_REVIEW
    notes: Optional[str] = None
