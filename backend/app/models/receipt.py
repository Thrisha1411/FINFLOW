import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Integer, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True, index=True)
    
    file_name = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)  # SHA-256 for duplicate detection
    
    # Extracted fields
    merchant_name = Column(String(255), nullable=True)
    total_amount = Column(Numeric(18, 4), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    tax_amount = Column(Numeric(18, 4), nullable=True)
    invoice_number = Column(String(100), nullable=True)
    receipt_date = Column(DateTime, nullable=True)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    
    # UPLOADED, OCR_PROCESSED, VERIFIED, REJECTED
    status = Column(String(50), default="UPLOADED", nullable=False)
    raw_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    line_items = relationship("ReceiptLineItem", back_populates="receipt", cascade="all, delete-orphan")


class ReceiptLineItem(Base):
    __tablename__ = "receipt_line_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    receipt_id = Column(String(36), ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(18, 4), nullable=False)
    total_price = Column(Numeric(18, 4), nullable=False)

    receipt = relationship("Receipt", back_populates="line_items")
