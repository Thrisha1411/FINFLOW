import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    merchant_name = Column(String(255), nullable=False, index=True)
    amount = Column(Numeric(18, 4), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Billing cycle: MONTHLY, ANNUAL, WEEKLY
    billing_cycle = Column(String(20), default="MONTHLY", nullable=False)
    next_renewal_date = Column(DateTime, nullable=False, index=True)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    
    # ACTIVE, CANCELLED, PAUSED
    status = Column(String(20), default="ACTIVE", nullable=False)
    is_auto_detected = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    price_history = relationship("SubscriptionPriceHistory", back_populates="subscription", cascade="all, delete-orphan", order_by="SubscriptionPriceHistory.changed_at.desc()")


class SubscriptionPriceHistory(Base):
    __tablename__ = "subscription_price_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    subscription_id = Column(String(36), ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    old_amount = Column(Numeric(18, 4), nullable=False)
    new_amount = Column(Numeric(18, 4), nullable=False)
    changed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    subscription = relationship("Subscription", back_populates="price_history")
