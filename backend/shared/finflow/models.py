from enum import StrEnum
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base, TimestampMixin, UUIDMixin


class TransactionStatus(StrEnum):
    initiated = "INITIATED"
    validation = "VALIDATION"
    ai_risk_analysis = "AI RISK ANALYSIS"
    approval = "APPROVAL"
    processing = "PROCESSING"
    success = "SUCCESS"
    failed = "FAILED"
    flagged = "FLAGGED"


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    organization_id: Mapped[str | None] = mapped_column(String(80), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    mfa_secret: Mapped[str | None] = mapped_column(String(64))
    roles: Mapped[list["RoleModel"]] = relationship(secondary="user_roles", lazy="selectin")


class RoleModel(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "roles"
    name: Mapped[str] = mapped_column(String(80), unique=True)
    permissions: Mapped[list["Permission"]] = relationship(secondary="role_permissions", lazy="selectin")


class Permission(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "permissions"
    key: Mapped[str] = mapped_column(String(120), unique=True)


class UserRole(Base):
    __tablename__ = "user_roles"
    user_id: Mapped[object] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[object] = mapped_column(ForeignKey("roles.id"), primary_key=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"
    role_id: Mapped[object] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[object] = mapped_column(ForeignKey("permissions.id"), primary_key=True)


class Device(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "devices"
    user_id: Mapped[object] = mapped_column(ForeignKey("users.id"), index=True)
    device_id: Mapped[str] = mapped_column(String(120), index=True)
    user_agent: Mapped[str | None] = mapped_column(Text)
    last_ip: Mapped[str | None] = mapped_column(String(64))
    trusted: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = (UniqueConstraint("user_id", "device_id", name="uq_user_device"),)


class Session(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "sessions"
    user_id: Mapped[object] = mapped_column(ForeignKey("users.id"), index=True)
    refresh_token_hash: Mapped[str] = mapped_column(String(255), index=True)
    ip_address: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[object] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class Transaction(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "transactions"
    organization_id: Mapped[str] = mapped_column(String(80), index=True)
    user_id: Mapped[str] = mapped_column(String(80), index=True)
    merchant: Mapped[str] = mapped_column(String(255), index=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    category: Mapped[str | None] = mapped_column(String(80), index=True)
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus), index=True)
    risk_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class TransactionEvent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "transaction_events"
    transaction_id: Mapped[object] = mapped_column(ForeignKey("transactions.id"), index=True)
    from_status: Mapped[str | None] = mapped_column(String(40))
    to_status: Mapped[str] = mapped_column(String(40))
    actor_id: Mapped[str | None] = mapped_column(String(80))
    reason: Mapped[str | None] = mapped_column(Text)


class FraudCase(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "fraud_cases"
    transaction_id: Mapped[object] = mapped_column(ForeignKey("transactions.id"), index=True)
    organization_id: Mapped[str] = mapped_column(String(80), index=True)
    risk_score: Mapped[float] = mapped_column(Numeric(5, 2))
    fraud_reason: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="open", index=True)


class Budget(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "budgets"
    organization_id: Mapped[str] = mapped_column(String(80), index=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(80), index=True)
    limit_amount: Mapped[float] = mapped_column(Numeric(14, 2))
    actual_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    forecast_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    savings_target: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    period: Mapped[str] = mapped_column(String(20), default="monthly")


class BudgetCategory(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "budget_categories"
    organization_id: Mapped[str] = mapped_column(String(80), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    group_name: Mapped[str] = mapped_column(String(40), index=True)
    recommended_percent: Mapped[int] = mapped_column(Integer)
    actual_percent: Mapped[int] = mapped_column(Integer, default=0)
    actual_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)


class BudgetForecast(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "budget_forecasts"
    organization_id: Mapped[str] = mapped_column(String(80), index=True)
    month: Mapped[str] = mapped_column(String(20), index=True)
    income: Mapped[float] = mapped_column(Numeric(14, 2))
    needs_limit: Mapped[float] = mapped_column(Numeric(14, 2))
    wants_limit: Mapped[float] = mapped_column(Numeric(14, 2))
    savings_target: Mapped[float] = mapped_column(Numeric(14, 2))
    risk_predictions: Mapped[dict] = mapped_column(JSON, default=dict)


class BudgetHealthScore(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "budget_health_scores"
    organization_id: Mapped[str] = mapped_column(String(80), index=True)
    month: Mapped[str] = mapped_column(String(20), index=True)
    score: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(40))
    savings_rate: Mapped[float] = mapped_column(Numeric(5, 2))
    debt_ratio: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    budget_adherence: Mapped[float] = mapped_column(Numeric(5, 2))
    subscription_efficiency: Mapped[float] = mapped_column(Numeric(5, 2))
    explanation: Mapped[str] = mapped_column(Text)


class BudgetAlert(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "budget_alerts"
    budget_id: Mapped[object] = mapped_column(ForeignKey("budgets.id"), index=True)
    severity: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)


class FinancialGoal(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "financial_goals"
    organization_id: Mapped[str] = mapped_column(String(80), index=True)
    name: Mapped[str] = mapped_column(String(120))
    target_amount: Mapped[float] = mapped_column(Numeric(14, 2))
    current_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    target_date: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40), default="active", index=True)


class Subscription(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "subscriptions"
    organization_id: Mapped[str] = mapped_column(String(80), index=True)
    merchant: Mapped[str] = mapped_column(String(255), index=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    cadence: Mapped[str] = mapped_column(String(20), default="monthly")
    next_renewal_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Notification(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "notifications"
    organization_id: Mapped[str] = mapped_column(String(80), index=True)
    user_id: Mapped[str | None] = mapped_column(String(80), index=True)
    channel: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text)
    read: Mapped[bool] = mapped_column(Boolean, default=False)


class AuditLog(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"
    organization_id: Mapped[str | None] = mapped_column(String(80), index=True)
    actor_id: Mapped[str | None] = mapped_column(String(80), index=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    resource_type: Mapped[str] = mapped_column(String(80), index=True)
    resource_id: Mapped[str | None] = mapped_column(String(80), index=True)
    ip_address: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(Text)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
