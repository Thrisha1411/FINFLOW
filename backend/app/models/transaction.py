import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Float, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reference_id = Column(String(64), unique=True, nullable=False, index=True)
    idempotency_key = Column(String(128), unique=True, nullable=True, index=True)
    
    # Financial precision: 18 digits total, 4 decimal places
    amount = Column(Numeric(18, 4), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    merchant_name = Column(String(255), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Lifecycle: INITIATED, VALIDATING, RISK_ANALYSIS, PENDING_APPROVAL, PROCESSING, SUCCESS, FAILED, FLAGGED, REFUNDED
    status = Column(String(50), default="INITIATED", nullable=False, index=True)
    
    # AI Risk Score (0-100)
    risk_score = Column(Float, default=0.0, nullable=False)
    risk_level = Column(String(20), default="LOW", nullable=False)
    
    payment_method = Column(String(50), default="CARD_SIMULATION", nullable=False)
    ip_address = Column(String(45), nullable=True)
    device_id = Column(String(128), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    category = relationship("Category", back_populates="transactions")
    events = relationship("TransactionEvent", back_populates="transaction", cascade="all, delete-orphan", order_by="TransactionEvent.created_at")
    fraud_case = relationship("FraudCase", back_populates="transaction", uselist=False, cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="transaction", cascade="all, delete-orphan")


class TransactionEvent(Base):
    __tablename__ = "transaction_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    transaction_id = Column(String(36), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status = Column(String(50), nullable=True)
    to_status = Column(String(50), nullable=False)
    reason = Column(String(255), nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    transaction = relationship("Transaction", back_populates="events")


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(18, 4), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    reason = Column(String(255), nullable=False)
    status = Column(String(50), default="COMPLETED", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    transaction = relationship("Transaction", back_populates="refunds")
