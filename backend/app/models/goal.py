import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class FinancialGoal(Base):
    __tablename__ = "financial_goals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    target_amount = Column(Numeric(18, 4), nullable=False)
    current_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    target_date = Column(DateTime, nullable=False)
    category = Column(String(50), default="SAVINGS", nullable=False)  # EMERGENCY_FUND, RETIREMENT, ASSET, DEBT_PAYOFF
    status = Column(String(20), default="IN_PROGRESS", nullable=False)  # IN_PROGRESS, REACHED, PAUSED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
