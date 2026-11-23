from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ReceiptLineItemResponse(BaseModel):
    id: str
    description: str
    quantity: int
    unit_price: float
    total_price: float

    class Config:
        from_attributes = True

class ReceiptResponse(BaseModel):
    id: str
    file_name: str
    merchant_name: Optional[str]
    total_amount: Optional[float]
    currency: str
    tax_amount: Optional[float]
    invoice_number: Optional[str]
    status: str
    created_at: datetime
    line_items: List[ReceiptLineItemResponse] = []

    class Config:
        from_attributes = True

class ReceiptConfirmRequest(BaseModel):
    receipt_id: str
    merchant_name: str
    total_amount: float
    category_id: Optional[str] = None
