from fastapi import Depends
from sqlalchemy.orm import Session
from finflow.app import create_service_app
from finflow.database import get_db
from finflow.domain_services import BudgetIntelligenceService, ForecastService
from finflow.repositories import TransactionRepository
from finflow.security import TokenPrincipal, current_principal

app = create_service_app("analytics-service")


@app.get("/analytics/dashboard", tags=["analytics"])
def dashboard(principal: TokenPrincipal = Depends(current_principal), db: Session = Depends(get_db)):
    transactions = TransactionRepository(db).list(principal.organization_id or "demo-org", limit=500)
    amounts = [float(t.amount) for t in transactions]
    return {
        "revenue": 10680000,
        "expenses": round(sum(amounts), 2),
        "fraud_events": len([t for t in transactions if t.status.value == "FLAGGED"]),
        "risk_distribution": [{"name": "low", "value": 63}, {"name": "medium", "value": 24}, {"name": "high", "value": 13}],
        "forecast": ForecastService().spend_projection(amounts),
        "budget_performance": [{"category": "Travel", "used": 72}, {"category": "SaaS", "used": 54}, {"category": "Utilities", "used": 41}],
    }

@app.post("/analytics/forecast", tags=["analytics"])
def forecast(amounts: list[float]):
    return ForecastService().spend_projection(amounts)


@app.get("/analytics/budget-intelligence", tags=["analytics"])
def budget_intelligence(profile: str = "Working Professional", income: float = 60000):
    spending = {
        "Rent": 18000,
        "Utilities": 5200,
        "Groceries": 7800,
        "Transportation": 6800,
        "Dining": 9200,
        "Entertainment": 4200,
        "Shopping": 6100,
        "Travel": 4800,
        "Mutual Funds": 7000,
        "Emergency Fund": 2200,
    }
    subscriptions = [
        {"merchant": "Netflix", "amount": 649, "risk": "Healthy"},
        {"merchant": "Spotify", "amount": 119, "risk": "Healthy"},
        {"merchant": "Notion", "amount": 8000, "risk": "Unused"},
    ]
    return BudgetIntelligenceService().analyze(income, profile, spending, subscriptions)
