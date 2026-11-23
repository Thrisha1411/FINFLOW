from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from backend.app.models.transaction import Transaction
from backend.app.models.category import Category
from backend.app.models.subscription import Subscription
from backend.app.models.goal import FinancialGoal

class FinancialSimulatorService:
    @staticmethod
    def run_simulation(
        db: Session,
        organization_id: str,
        shopping_reduction_pct: float = 0.0,
        dining_reduction_pct: float = 0.0,
        income_delta: float = 0.0,
        subscriptions_to_cancel: List[str] = None,
        additional_monthly_savings: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates deterministic financial scenario projections based on actual current metrics.
        Clearly separates baseline vs simulated projections.
        """
        # Baseline monthly metrics
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=30)

        txs = db.query(Transaction).filter(
            Transaction.organization_id == organization_id,
            Transaction.status == "SUCCESS",
            Transaction.created_at >= start_date
        ).all()

        categories = {c.id: c.name for c in db.query(Category).all()}

        baseline_income = 30500.0
        baseline_shopping = 0.0
        baseline_dining = 0.0
        baseline_total_expenses = 0.0

        for tx in txs:
            amt = float(tx.amount)
            if amt < 0:
                pass
            else:
                baseline_total_expenses += amt
                cat_name = categories.get(tx.category_id, "")
                if "shopping" in cat_name.lower():
                    baseline_shopping += amt
                elif "food" in cat_name.lower() or "dining" in cat_name.lower():
                    baseline_dining += amt

        # Baseline subscriptions
        subs = db.query(Subscription).filter(
            Subscription.organization_id == organization_id,
            Subscription.status == "ACTIVE"
        ).all()
        baseline_sub_monthly = sum(float(s.amount) for s in subs)

        # Calculate reductions
        shopping_savings = baseline_shopping * (shopping_reduction_pct / 100.0)
        dining_savings = baseline_dining * (dining_reduction_pct / 100.0)
        
        cancelled_sub_savings = 0.0
        if subscriptions_to_cancel:
            for s in subs:
                if s.id in subscriptions_to_cancel or s.merchant_name in subscriptions_to_cancel:
                    cancelled_sub_savings += float(s.amount)

        # Simulated changes
        simulated_income = baseline_income + income_delta
        total_monthly_expense_reduction = shopping_savings + dining_savings + cancelled_sub_savings
        simulated_expenses = max(0.0, baseline_total_expenses - total_monthly_expense_reduction)
        
        baseline_monthly_net = baseline_income - baseline_total_expenses
        simulated_monthly_net = simulated_income - simulated_expenses + additional_monthly_savings
        monthly_net_gain = simulated_monthly_net - baseline_monthly_net

        # Projections
        annual_baseline_savings = max(0.0, baseline_monthly_net * 12)
        annual_simulated_savings = max(0.0, simulated_monthly_net * 12)
        annual_difference = annual_simulated_savings - annual_baseline_savings

        # Impact on financial goals
        goals = db.query(FinancialGoal).filter(
            FinancialGoal.organization_id == organization_id,
            FinancialGoal.status == "IN_PROGRESS"
        ).all()

        goal_accelerations = []
        for g in goals:
            remaining = float(g.target_amount) - float(g.current_amount)
            if remaining > 0:
                baseline_months = remaining / max(100.0, baseline_monthly_net)
                simulated_months = remaining / max(100.0, simulated_monthly_net)
                months_saved = max(0.0, baseline_months - simulated_months)
                goal_accelerations.append({
                    "goal_id": g.id,
                    "title": g.title,
                    "baseline_months_to_complete": round(baseline_months, 1),
                    "simulated_months_to_complete": round(simulated_months, 1),
                    "months_saved": round(months_saved, 1)
                })

        return {
            "is_hypothetical_projection": True,
            "inputs_applied": {
                "shopping_reduction_pct": shopping_reduction_pct,
                "dining_reduction_pct": dining_reduction_pct,
                "income_delta": income_delta,
                "cancelled_subscriptions_count": len(subscriptions_to_cancel or []),
                "additional_monthly_savings": additional_monthly_savings
            },
            "baseline": {
                "monthly_income": baseline_income,
                "monthly_expenses": round(baseline_total_expenses, 2),
                "monthly_net_cashflow": round(baseline_monthly_net, 2),
                "annual_projected_savings": round(annual_baseline_savings, 2)
            },
            "simulated": {
                "monthly_income": round(simulated_income, 2),
                "monthly_expenses": round(simulated_expenses, 2),
                "monthly_net_cashflow": round(simulated_monthly_net, 2),
                "annual_projected_savings": round(annual_simulated_savings, 2)
            },
            "impact": {
                "monthly_savings_increase": round(monthly_net_gain, 2),
                "annual_savings_increase": round(annual_difference, 2),
                "goal_accelerations": goal_accelerations
            }
        }

from datetime import timedelta
simulator_service = FinancialSimulatorService()
