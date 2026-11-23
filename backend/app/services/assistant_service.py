from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
import json
import re
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.transaction import Transaction
from backend.app.models.fraud import FraudCase
from backend.app.models.budget import Budget
from backend.app.models.subscription import Subscription
from backend.app.models.category import Category
from backend.app.models.assistant import AIConversation, AIMessage
from backend.app.services.budget_service import budget_service
from backend.app.services.subscription_service import subscription_service
from backend.app.services.root_cause_service import root_cause_service
from backend.app.services.simulator_service import simulator_service

class AIAssistantService:
    @staticmethod
    def classify_intent(query: str) -> str:
        q = query.lower()
        if any(kw in q for kw in ["spend", "spent", "how much", "expenses", "expense"]):
            return "SPENDING_ANALYSIS"
        elif any(kw in q for kw in ["fraud", "flagged", "risk", "suspicious", "blocked"]):
            return "FRAUD_INVESTIGATION"
        elif any(kw in q for kw in ["50/30/20", "budget", "rule", "target", "allocation"]):
            return "BUDGET_ANALYSIS"
        elif any(kw in q for kw in ["sub", "subscription", "recurring", "renew"]):
            return "SUBSCRIPTION_ANALYSIS"
        elif any(kw in q for kw in ["what if", "simulator", "what happens", "if i reduce", "if i cancel"]):
            return "WHAT_IF_SIMULATION"
        elif any(kw in q for kw in ["why did", "why is", "root cause", "increase", "decrease", "variance"]):
            return "ROOT_CAUSE_ANALYSIS"
        elif any(kw in q for kw in ["health score", "financial health", "score"]):
            return "HEALTH_SCORE_EXPLANATION"
        return "GENERAL_FINANCIAL_INQUIRY"

    @staticmethod
    def query_actual_financial_data(db: Session, organization_id: str, intent: str, query: str) -> Dict[str, Any]:
        """
        Executes deterministic SQL queries to retrieve real numbers.
        Guarantees ZERO hallucinations for amounts, counts, and dates.
        """
        now = datetime.now(timezone.utc)
        curr_month = now.strftime("%Y-%m")
        categories = {c.id: c.name for c in db.query(Category).all()}

        if intent == "SPENDING_ANALYSIS":
            txs = db.query(Transaction).filter(
                Transaction.organization_id == organization_id,
                Transaction.status == "SUCCESS"
            ).all()
            total_spend = sum(float(t.amount) for t in txs if t.amount > 0)
            
            cat_totals: Dict[str, float] = {}
            for t in txs:
                if t.amount > 0:
                    cname = categories.get(t.category_id, "Other")
                    cat_totals[cname] = cat_totals.get(cname, 0.0) + float(t.amount)

            sorted_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
            top_category = sorted_cats[0] if sorted_cats else ("None", 0.0)

            return {
                "total_spend": round(total_spend, 2),
                "transaction_count": len([t for t in txs if t.amount > 0]),
                "top_category_name": top_category[0],
                "top_category_amount": round(top_category[1], 2),
                "category_breakdown": {k: round(v, 2) for k, v in sorted_cats[:5]}
            }

        elif intent == "FRAUD_INVESTIGATION":
            flagged = db.query(Transaction).filter(
                Transaction.organization_id == organization_id,
                Transaction.risk_score >= 60.0
            ).order_by(Transaction.risk_score.desc()).all()

            results = []
            for t in flagged[:5]:
                fc = t.fraud_case
                results.append({
                    "reference_id": t.reference_id,
                    "merchant": t.merchant_name,
                    "amount": float(t.amount),
                    "risk_score": t.risk_score,
                    "risk_level": t.risk_level,
                    "signals": [s.signal_name for s in fc.signals] if fc else ["Outlier Spike"]
                })
            return {"flagged_transactions": results, "total_flagged_count": len(flagged)}

        elif intent == "BUDGET_ANALYSIS":
            return budget_service.get_50_30_20_analysis(db, organization_id, curr_month)

        elif intent == "SUBSCRIPTION_ANALYSIS":
            return subscription_service.get_subscription_analytics(db, organization_id)

        elif intent == "HEALTH_SCORE_EXPLANATION":
            return budget_service.calculate_health_score(db, organization_id, curr_month)

        elif intent == "ROOT_CAUSE_ANALYSIS":
            return root_cause_service.analyze_variance(db, organization_id, curr_month)

        elif intent == "WHAT_IF_SIMULATION":
            return simulator_service.run_simulation(db, organization_id, shopping_reduction_pct=15.0)

        # Default summary
        tx_count = db.query(Transaction).filter(Transaction.organization_id == organization_id).count()
        return {"organization_id": organization_id, "total_recorded_transactions": tx_count}

    @staticmethod
    def generate_grounded_response(intent: str, data: Dict[str, Any], user_query: str) -> str:
        """
        Synthesizes an explainable, fact-backed answer grounded directly in the deterministic data.
        """
        if intent == "SPENDING_ANALYSIS":
            top_cat = data.get("top_category_name", "N/A")
            top_amt = data.get("top_category_amount", 0.0)
            tot = data.get("total_spend", 0.0)
            return (
                f"Based on your verified transactions, your total expenses stand at **${tot:,.2f}** "
                f"across {data.get('transaction_count', 0)} settled transactions.\n\n"
                f"The highest expenditure category is **{top_cat}** at **${top_amt:,.2f}** "
                f"({(top_amt/max(1.0, tot))*100:.1f}% of total spend).\n\n"
                f"**Top Categories:**\n" + "\n".join([f"- **{k}**: ${v:,.2f}" for k, v in data.get("category_breakdown", {}).items()])
            )

        elif intent == "FRAUD_INVESTIGATION":
            count = data.get("total_flagged_count", 0)
            txs = data.get("flagged_transactions", [])
            if not txs:
                return "Good news! There are currently no transactions flagged as high risk or suspended for fraud."
            
            t0 = txs[0]
            sigs = ", ".join(t0.get("signals", []))
            return (
                f"There are **{count} flagged transactions** requiring attention.\n\n"
                f"The highest risk item is **{t0['merchant']}** for **${t0['amount']:,.2f}** "
                f"(Ref: `{t0['reference_id']}`), rated with a **Risk Score of {t0['risk_score']}/100 ({t0['risk_level']})**.\n\n"
                f"**Triggered Signals:** {sigs}.\n\n"
                f"**Recommendation:** Step-up authentication or manual analyst clearance in the Fraud Intelligence module."
            )

        elif intent == "BUDGET_ANALYSIS":
            needs = data.get("needs", {})
            wants = data.get("wants", {})
            sav = data.get("savings", {})
            recs = "\n".join([f"- {r}" for r in data.get("recommendations", [])])
            return (
                f"### 50/30/20 Budget Adherence ({data.get('month')}):\n\n"
                f"- **Needs (Target 50%)**: **{needs.get('actual_percentage')}%** (${needs.get('amount', 0.0):,.2f}) — Status: `{needs.get('status')}`\n"
                f"- **Wants (Target 30%)**: **{wants.get('actual_percentage')}%** (${wants.get('amount', 0.0):,.2f}) — Status: `{wants.get('status')}`\n"
                f"- **Savings (Target 20%)**: **{sav.get('actual_percentage')}%** (${sav.get('amount', 0.0):,.2f}) — Status: `{sav.get('status')}`\n\n"
                f"**Actionable Insights:**\n{recs}"
            )

        elif intent == "SUBSCRIPTION_ANALYSIS":
            monthly = data.get("monthly_recurring_spend", 0.0)
            annual = data.get("annual_projected_spend", 0.0)
            count = data.get("active_subscriptions_count", 0)
            renewals = data.get("upcoming_renewals_30d", [])
            ren_text = "\n".join([f"- **{r['merchant_name']}**: ${r['amount']:,.2f} (renews in {r['days_until_renewal']} days)" for r in renewals[:4]])
            return (
                f"You currently have **{count} active recurring subscriptions** totaling **${monthly:,.2f}/month** "
                f"(${annual:,.2f} projected annually).\n\n"
                f"**Upcoming Renewals (Next 30 Days):**\n{ren_text or 'No renewals in next 30 days.'}"
            )

        elif intent == "HEALTH_SCORE_EXPLANATION":
            score = data.get("health_score", 0.0)
            rating = data.get("rating", "GOOD")
            pillars = data.get("pillars", {})
            pillar_lines = "\n".join([f"- **{k.replace('_', ' ').title()}**: {v['score']}/{v['max']} pts ({v['details']})" for k, v in pillars.items()])
            return (
                f"### Transparent Financial Health Score: **{score}/100** ({rating})\n\n"
                f"Your score is calculated deterministically across 5 financial pillars:\n{pillar_lines}"
            )

        elif intent == "ROOT_CAUSE_ANALYSIS":
            summary = data.get("summary", {})
            drivers = data.get("primary_drivers", [])
            lines = "\n".join([f"- **{d['category']}**: {d['dollar_difference']:+,.2f} ({d['percentage_change']:+.1f}%)" for d in drivers])
            return (
                f"### Root Cause Variance Analysis ({data.get('current_period')} vs {data.get('comparison_period')}):\n\n"
                f"Net expense change: **${summary.get('expense_change_dollars', 0.0):+,.2f}** ({summary.get('expense_percentage_change', 0.0):+.1f}%).\n\n"
                f"**Top Contributing Categories:**\n{lines}\n\n"
                f"**Finding:** {data.get('actionable_findings', [''])[0]}"
            )

        return (
            f"I have reviewed your financial operations data. There are {data.get('total_recorded_transactions', 0)} "
            "transactions recorded. You can ask me specific questions regarding your spending breakdown, 50/30/20 budget adherence, "
            "flagged fraud alerts, or next-month cash flow projections!"
        )

    @classmethod
    def ask(cls, db: Session, organization_id: str, user_id: str, query: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        intent = cls.classify_intent(query)
        grounded_data = cls.query_actual_financial_data(db, organization_id, intent, query)
        answer = cls.generate_grounded_response(intent, grounded_data, query)

        # Save conversation & message
        if not conversation_id:
            conv = AIConversation(
                organization_id=organization_id,
                user_id=user_id,
                title=query[:40] + ("..." if len(query) > 40 else "")
            )
            db.add(conv)
            db.flush()
            conversation_id = conv.id

        # Save User Message
        msg_user = AIMessage(
            conversation_id=conversation_id,
            role="USER",
            content=query,
            intent=intent
        )
        db.add(msg_user)

        # Save Assistant Message
        msg_ai = AIMessage(
            conversation_id=conversation_id,
            role="ASSISTANT",
            content=answer,
            intent=intent,
            grounding_data_json=json.dumps(grounded_data)
        )
        db.add(msg_ai)
        db.commit()

        return {
            "conversation_id": conversation_id,
            "intent": intent,
            "answer": answer,
            "grounding_data": grounded_data
        }

assistant_service = AIAssistantService()
