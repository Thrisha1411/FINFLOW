"""budget intelligence tables"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260620_0002"
down_revision = "20260619_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("budgets", sa.Column("actual_amount", sa.Numeric(14, 2), server_default="0", nullable=False))
    op.add_column("budgets", sa.Column("forecast_amount", sa.Numeric(14, 2), server_default="0", nullable=False))
    op.add_column("budgets", sa.Column("savings_target", sa.Numeric(14, 2), server_default="0", nullable=False))
    op.create_table(
        "budget_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", sa.String(80), index=True, nullable=False),
        sa.Column("name", sa.String(120), index=True, nullable=False),
        sa.Column("group_name", sa.String(40), index=True, nullable=False),
        sa.Column("recommended_percent", sa.Integer(), nullable=False),
        sa.Column("actual_percent", sa.Integer(), server_default="0", nullable=False),
        sa.Column("actual_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "budget_forecasts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", sa.String(80), index=True, nullable=False),
        sa.Column("month", sa.String(20), index=True, nullable=False),
        sa.Column("income", sa.Numeric(14, 2), nullable=False),
        sa.Column("needs_limit", sa.Numeric(14, 2), nullable=False),
        sa.Column("wants_limit", sa.Numeric(14, 2), nullable=False),
        sa.Column("savings_target", sa.Numeric(14, 2), nullable=False),
        sa.Column("risk_predictions", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "budget_health_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", sa.String(80), index=True, nullable=False),
        sa.Column("month", sa.String(20), index=True, nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(40), nullable=False),
        sa.Column("savings_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("debt_ratio", sa.Numeric(5, 2), server_default="0", nullable=False),
        sa.Column("budget_adherence", sa.Numeric(5, 2), nullable=False),
        sa.Column("subscription_efficiency", sa.Numeric(5, 2), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "financial_goals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", sa.String(80), index=True, nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("target_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("current_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("target_date", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(40), index=True, server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("financial_goals")
    op.drop_table("budget_health_scores")
    op.drop_table("budget_forecasts")
    op.drop_table("budget_categories")
    op.drop_column("budgets", "savings_target")
    op.drop_column("budgets", "forecast_amount")
    op.drop_column("budgets", "actual_amount")
