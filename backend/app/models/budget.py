import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    month = Column(String(7), nullable=False, index=True)  # YYYY-MM
    
    total_income = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_allocated = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    # 50/30/20 target breakdown
    needs_target_pct = Column(Numeric(5, 2), default=50.0, nullable=False)
    wants_target_pct = Column(Numeric(5, 2), default=30.0, nullable=False)
    savings_target_pct = Column(Numeric(5, 2), default=20.0, nullable=False)
    
    # Strategy: STANDARD_50_30_20, CUSTOM, ADAPTIVE
    strategy = Column(String(50), default="STANDARD_50_30_20", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    categories = relationship("BudgetCategory", back_populates="budget", cascade="all, delete-orphan")


class BudgetCategory(Base):
    __tablename__ = "budget_categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    budget_id = Column(String(36), ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    allocated_amount = Column(Numeric(18, 4), nullable=False)

    budget = relationship("Budget", back_populates="categories")
    category = relationship("Category")


class BudgetAlert(Base):
    __tablename__ = "budget_alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    alert_type = Column(String(50), nullable=False)  # THRESHOLD_80, EXCEEDED_100, OVERSPENT
    message = Column(String(255), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
