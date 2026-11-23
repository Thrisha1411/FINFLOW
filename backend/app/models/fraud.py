import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class FraudCase(Base):
    __tablename__ = "fraud_cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # 0 - 100 risk score
    risk_score = Column(Float, nullable=False, index=True)
    # LOW, MEDIUM, HIGH, CRITICAL
    risk_level = Column(String(20), nullable=False, index=True)
    # APPROVE, MANUAL_REVIEW, STEP_UP_AUTH, BLOCK
    recommendation = Column(String(50), nullable=False)
    
    # OPEN, UNDER_REVIEW, RESOLVED_BENIGN, CONFIRMED_FRAUD
    status = Column(String(50), default="OPEN", nullable=False, index=True)
    investigator_notes = Column(Text, nullable=True)
    resolved_by = Column(String(36), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    transaction = relationship("Transaction", back_populates="fraud_case")
    signals = relationship("FraudSignal", back_populates="fraud_case", cascade="all, delete-orphan")


class FraudSignal(Base):
    __tablename__ = "fraud_signals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    fraud_case_id = Column(String(36), ForeignKey("fraud_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_code = Column(String(50), nullable=False)
    signal_name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    severity = Column(String(20), default="MEDIUM", nullable=False)
    weight = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    fraud_case = relationship("FraudCase", back_populates="signals")
