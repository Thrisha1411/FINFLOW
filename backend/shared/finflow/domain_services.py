from datetime import datetime, timezone
from uuid import uuid4
import hashlib
import secrets
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

from . import models
from .repositories import UserRepository, TransactionRepository, FraudRepository
from .schemas import FraudDecision, FraudSignal, TransactionCreate
from .security import create_access_token, hash_password, verify_password, verify_mfa


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def register(self, email: str, password: str, full_name: str, organization_id: str) -> models.User:
        existing = self.repo.get_by_email(email)
        if existing:
            raise ValueError("Email is already registered")
        user = models.User(email=email, password_hash=hash_password(password), full_name=full_name, organization_id=organization_id)
        return self.repo.add(user)

    def login(self, email: str, password: str, mfa_code: str | None) -> str:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        if user.mfa_secret and not (mfa_code and verify_mfa(user.mfa_secret, mfa_code)):
            raise PermissionError("MFA required")
        roles = [role.name for role in user.roles] or ["Admin"]
        return create_access_token(str(user.id), user.email, roles, user.organization_id)

    @staticmethod
    def refresh_token() -> tuple[str, str]:
        raw = secrets.token_urlsafe(48)
        return raw, hashlib.sha256(raw.encode()).hexdigest()


class FraudEngine:
    categories = {"Food", "Travel", "Healthcare", "Utilities", "Shopping", "Investments", "Salary"}

    def score(self, signal: FraudSignal) -> FraudDecision:
        frame = pd.DataFrame(
            [
                {"amount": signal.amount, "count": signal.prior_24h_count, "velocity": signal.prior_24h_amount},
                {"amount": 45, "count": 1, "velocity": 45},
                {"amount": 120, "count": 2, "velocity": 240},
                {"amount": 900, "count": 3, "velocity": 1350},
                {"amount": 35, "count": 1, "velocity": 35},
            ]
        )
        model = IsolationForest(contamination=0.2, random_state=42)
        model.fit(frame)
        anomaly = model.decision_function(frame.iloc[[0]])[0]
        velocity_risk = min(40, signal.prior_24h_count * 7 + signal.prior_24h_amount / 250)
        amount_risk = min(35, signal.amount / 100)
        model_risk = float(np.clip((0.15 - anomaly) * 100, 0, 25))
        risk_score = round(min(99, velocity_risk + amount_risk + model_risk), 2)
        if risk_score >= 75:
            recommendation = "Hold for manual approval and request secondary verification."
        elif risk_score >= 45:
            recommendation = "Route to analyst queue before processing."
        else:
            recommendation = "Approve automatically and continue monitoring."
        reason = f"Velocity={signal.prior_24h_count} tx/day, amount=INR {signal.amount:.2f}, anomaly={anomaly:.3f}"
        return FraudDecision(risk_score=risk_score, fraud_reason=reason, recommendation=recommendation)

    def categorize(self, merchant: str, memo: str = "") -> str:
        text = f"{merchant} {memo}".lower()
        rules = {
            "Travel": ["air", "hotel", "uber", "lyft", "rail"],
            "Food": ["restaurant", "cafe", "coffee", "doordash"],
            "Utilities": ["electric", "water", "internet", "telecom"],
            "Healthcare": ["pharmacy", "clinic", "hospital"],
            "Investments": ["broker", "fund", "dividend"],
            "Salary": ["payroll", "salary"],
        }
        for category, words in rules.items():
            if any(word in text for word in words):
                return category
        return "Shopping"


class PaymentWorkflowService:
    def __init__(self, repo: TransactionRepository, fraud_engine: FraudEngine):
        self.repo = repo
        self.fraud_engine = fraud_engine

    def create(self, principal_id: str, organization_id: str, payload: TransactionCreate) -> models.Transaction:
        category = payload.category or self.fraud_engine.categorize(payload.merchant)
        transaction = models.Transaction(
            organization_id=organization_id,
            user_id=principal_id,
            merchant=payload.merchant,
            amount=payload.amount,
            currency=payload.currency,
            category=category,
            status=models.TransactionStatus.initiated,
            metadata_json=payload.metadata,
        )
        transaction = self.repo.add(transaction)
        signal = FraudSignal(
            transaction_id=str(transaction.id),
            user_id=principal_id,
            amount=float(transaction.amount),
            merchant=transaction.merchant,
            category=transaction.category,
        )
        decision = self.fraud_engine.score(signal)
        next_status = models.TransactionStatus.flagged if decision.risk_score >= 75 else models.TransactionStatus.approval
        transaction.risk_score = decision.risk_score
        return self.repo.update_status(transaction, next_status, principal_id, decision.fraud_reason)


class ForecastService:
    def spend_projection(self, amounts: list[float]) -> dict:
        if not amounts:
            return {"future_spending": 0, "cash_flow_projection": 0, "budget_risk": "low"}
        series = np.array(amounts, dtype=float)
        future = round(float(series.mean() * 1.08), 2)
        risk = "high" if future > np.percentile(series, 80) else "medium"
        return {"future_spending": future, "cash_flow_projection": round(future * -1, 2), "budget_risk": risk}


class BudgetIntelligenceService:
    profile_rules = {
        "Student": {"Needs": 60, "Wants": 20, "Savings": 20},
        "Working Professional": {"Needs": 50, "Wants": 30, "Savings": 20},
        "Freelancer": {"Needs": 45, "Wants": 25, "Savings": 30},
        "Family": {"Needs": 55, "Wants": 25, "Savings": 20},
        "Business Owner": {"Needs": 40, "Wants": 30, "Savings": 30},
        "High Income User": {"Needs": 40, "Wants": 30, "Savings": 30},
    }
    category_groups = {
        "Needs": ["Rent", "Mortgage", "Utilities", "Groceries", "Insurance", "Transportation", "Essential Bills"],
        "Wants": ["Dining", "Entertainment", "Shopping", "Travel", "Subscriptions", "Lifestyle Expenses"],
        "Savings": ["Savings", "Emergency Fund", "Mutual Funds", "Stocks", "Retirement Investments"],
    }

    def analyze(self, income: float, profile: str, spending: dict[str, float], subscriptions: list[dict] | None = None) -> dict:
        subscriptions = subscriptions or []
        target = self.profile_rules.get(profile, self.profile_rules["Working Professional"])
        grouped = {group: 0.0 for group in ["Needs", "Wants", "Savings"]}
        for category, amount in spending.items():
            grouped[self.group_for_category(category)] += float(amount)
        actual_percent = {group: round((amount / income) * 100, 1) if income else 0 for group, amount in grouped.items()}
        deviation = {group: round(actual_percent[group] - target[group], 1) for group in target}
        score = self.health_score(actual_percent, deviation, subscriptions)
        return {
            "income": income,
            "profile": profile,
            "recommended_allocation": target,
            "current_allocation": actual_percent,
            "deviation": deviation,
            "forecast": self.next_month_forecast(income, target, spending, subscriptions),
            "health": score,
            "recommendations": self.recommendations(grouped, deviation, subscriptions),
            "alerts": self.alerts(deviation, spending, subscriptions),
        }

    def group_for_category(self, category: str) -> str:
        normalized = category.lower()
        for group, categories in self.category_groups.items():
            if any(item.lower() in normalized for item in categories):
                return group
        if any(word in normalized for word in ["fund", "stock", "saving", "investment"]):
            return "Savings"
        if any(word in normalized for word in ["dining", "shopping", "travel", "subscription"]):
            return "Wants"
        return "Needs"

    def next_month_forecast(self, income: float, target: dict[str, int], spending: dict[str, float], subscriptions: list[dict]) -> dict:
        dining = spending.get("Dining", 0)
        travel = spending.get("Travel", 0)
        subscription_total = sum(float(item.get("amount", 0)) for item in subscriptions)
        return {
            "needs": round(income * target["Needs"] / 100),
            "wants": round(income * target["Wants"] / 100),
            "savings": round(income * target["Savings"] / 100),
            "category_forecasts": {
                "Dining": round(dining * 1.15),
                "Travel": round(travel * 1.08),
                "Subscriptions": round(subscription_total),
            },
            "renewals": [item.get("merchant") for item in subscriptions],
            "risk": "Food & Dining +15%" if dining else "Subscriptions renewal cluster",
        }

    def health_score(self, actual: dict[str, float], deviation: dict[str, float], subscriptions: list[dict]) -> dict:
        savings_rate = actual.get("Savings", 0)
        adherence_penalty = sum(abs(value) for value in deviation.values()) * 0.6
        subscription_penalty = min(8, len([item for item in subscriptions if item.get("risk") != "Healthy"]) * 4)
        score = int(max(0, min(100, 82 + (savings_rate - 20) * 1.2 - adherence_penalty - subscription_penalty)))
        label = "Excellent" if score >= 90 else "Good" if score >= 75 else "Average" if score >= 60 else "Needs Improvement"
        return {
            "score": score,
            "label": label,
            "savings_rate": savings_rate,
            "budget_adherence": max(0, round(100 - adherence_penalty, 1)),
            "subscription_efficiency": max(0, 100 - subscription_penalty * 8),
            "explanation": "Savings rate and budget adherence are the largest drivers of this score.",
        }

    def recommendations(self, grouped: dict[str, float], deviation: dict[str, float], subscriptions: list[dict]) -> list[str]:
        recs = []
        if deviation["Needs"] > 5:
            recs.append("Essential expenses exceed the target. Review utilities, transportation, and insurance renewals.")
        if deviation["Wants"] > 5:
            recs.append("Wants are above plan. Reduce dining and discretionary shopping before the next billing cycle.")
        if deviation["Savings"] < -3:
            recs.append("Increase automated savings transfers to restore the monthly savings target.")
        unused = [item["merchant"] for item in subscriptions if item.get("risk") == "Unused"]
        if unused:
            recs.append(f"Cancel or downgrade unused subscriptions: {', '.join(unused)}.")
        recs.append("Maintain an emergency fund target of at least three months of essential expenses.")
        return recs

    def alerts(self, deviation: dict[str, float], spending: dict[str, float], subscriptions: list[dict]) -> list[dict]:
        alerts = []
        if deviation["Needs"] > 10:
            alerts.append({"severity": "high", "message": "Needs allocation is materially above the recommended profile."})
        if spending.get("Dining", 0) > 12000:
            alerts.append({"severity": "medium", "message": "Dining budget may be exceeded within 10 days."})
        for item in subscriptions:
            if item.get("risk") == "Price increase":
                alerts.append({"severity": "medium", "message": f"Subscription increase detected for {item['merchant']}."})
            if item.get("risk") == "Unused":
                alerts.append({"severity": "low", "message": f"Unused subscription detected: {item['merchant']}."})
        return alerts


class AssistantService:
    def answer(self, question: str) -> str:
        q = question.lower()
        if "flagged" in q:
            return "Flagged transactions are scored from velocity, amount outliers, device/IP risk, and merchant history. Open Fraud Center for the case trail and recommendation."
        if "failed" in q:
            return "Failed payments are available in Transactions with status FAILED. Retry candidates are those without hard processor declines."
        if "predict" in q or "forecast" in q:
            return "Based on current trend, next month spending should be forecast from category run-rate, recurring subscriptions, and recent anomalies."
        return "I can explain payment status, fraud reasons, spending trends, subscriptions, budgets, and audit activity using your organization context."

    def extract_receipt(self, text: str) -> dict:
        return {"merchant": "Detected Merchant", "amount": 0.0, "tax": 0.0, "category": "Shopping", "date": datetime.now(timezone.utc).date().isoformat()}


def new_id() -> str:
    return str(uuid4())
