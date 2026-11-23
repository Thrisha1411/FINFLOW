import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
from backend.app.main import app
from backend.app.core.database import Base, engine
from backend.app.db.init_db import init_db

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    init_db()

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["service"] == "FinFlow AI"

def test_auth_login_admin():
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@finflow.ai",
        "password": "Admin123!@#"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@finflow.ai"
    assert data["user"]["role"] == "ORG_ADMIN"

def test_dashboard_overview():
    # Login
    auth_res = client.post("/api/v1/auth/login", json={
        "email": "admin@finflow.ai",
        "password": "Admin123!@#"
    }).json()
    token = auth_res["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/dashboard/overview", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert data["metrics"]["total_income"] > 0
    assert data["metrics"]["financial_health_score"] > 0
    assert len(data["recent_transactions"]) > 0

def test_create_normal_transaction():
    auth_res = client.post("/api/v1/auth/login", json={
        "email": "admin@finflow.ai",
        "password": "Admin123!@#"
    }).json()
    headers = {"Authorization": f"Bearer {auth_res['access_token']}"}

    tx_payload = {
        "amount": 75.50,
        "merchant_name": "Starbucks Reserve Roastery",
        "currency": "USD",
        "description": "Executive team meeting coffee",
        "payment_method": "CORPORATE_CARD"
    }
    response = client.post("/api/v1/transactions", json=tx_payload, headers=headers)
    assert response.status_code == 200
    tx = response.json()
    assert tx["status"] == "SUCCESS"
    assert tx["risk_level"] == "LOW"
    assert tx["risk_score"] < 50.0

def test_create_fraud_flagged_transaction():
    auth_res = client.post("/api/v1/auth/login", json={
        "email": "admin@finflow.ai",
        "password": "Admin123!@#"
    }).json()
    headers = {"Authorization": f"Bearer {auth_res['access_token']}"}

    # Outlier amount with suspicious merchant descriptor
    fraud_payload = {
        "amount": 19500.00,
        "merchant_name": "Unknown Offshore Casino Wire",
        "currency": "USD",
        "description": "Rapid untrusted transfer",
        "payment_method": "WIRE_TRANSFER"
    }
    response = client.post("/api/v1/transactions", json=fraud_payload, headers=headers)
    assert response.status_code == 200
    tx = response.json()
    assert tx["status"] in ("FLAGGED", "PENDING_APPROVAL")
    assert tx["risk_score"] >= 40.0
    assert tx["risk_level"] in ("MEDIUM", "HIGH", "CRITICAL")

def test_budget_50_30_20():
    auth_res = client.post("/api/v1/auth/login", json={
        "email": "admin@finflow.ai",
        "password": "Admin123!@#"
    }).json()
    headers = {"Authorization": f"Bearer {auth_res['access_token']}"}

    response = client.get("/api/v1/budgets/50-30-20", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "needs" in data and "wants" in data and "savings" in data
    assert data["needs"]["target_percentage"] == 50.0
    assert len(data["recommendations"]) > 0

def test_budget_health_score():
    auth_res = client.post("/api/v1/auth/login", json={
        "email": "admin@finflow.ai",
        "password": "Admin123!@#"
    }).json()
    headers = {"Authorization": f"Bearer {auth_res['access_token']}"}

    response = client.get("/api/v1/budgets/health-score", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["health_score"] <= 100
    assert "pillars" in data
    assert "savings_rate" in data["pillars"]

def test_subscriptions_analytics():
    auth_res = client.post("/api/v1/auth/login", json={
        "email": "admin@finflow.ai",
        "password": "Admin123!@#"
    }).json()
    headers = {"Authorization": f"Bearer {auth_res['access_token']}"}

    response = client.get("/api/v1/subscriptions/analytics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["active_subscriptions_count"] > 0
    assert data["monthly_recurring_spend"] > 0

def test_ai_assistant_chat():
    auth_res = client.post("/api/v1/auth/login", json={
        "email": "admin@finflow.ai",
        "password": "Admin123!@#"
    }).json()
    headers = {"Authorization": f"Bearer {auth_res['access_token']}"}

    # Ask about spending
    res = client.post("/api/v1/assistant/chat", json={
        "query": "How much did I spend this month and what is my top category?"
    }, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "SPENDING_ANALYSIS"
    assert "total_spend" in data["grounding_data"]
    assert len(data["answer"]) > 20

    # Ask about fraud
    res2 = client.post("/api/v1/assistant/chat", json={
        "query": "Why was a transaction flagged for high risk?"
    }, headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["intent"] == "FRAUD_INVESTIGATION"
    assert "flagged" in data2["answer"].lower()

def test_simulator():
    auth_res = client.post("/api/v1/auth/login", json={
        "email": "admin@finflow.ai",
        "password": "Admin123!@#"
    }).json()
    headers = {"Authorization": f"Bearer {auth_res['access_token']}"}

    payload = {
        "shopping_reduction_pct": 20.0,
        "dining_reduction_pct": 15.0,
        "income_delta": 2500.0
    }
    response = client.post("/api/v1/simulator/simulate", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_hypothetical_projection"] is True
    assert data["simulated"]["monthly_income"] > data["baseline"]["monthly_income"]

def test_root_cause_analysis():
    auth_res = client.post("/api/v1/auth/login", json={
        "email": "admin@finflow.ai",
        "password": "Admin123!@#"
    }).json()
    headers = {"Authorization": f"Bearer {auth_res['access_token']}"}

    response = client.get("/api/v1/root-cause/analyze", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "actionable_findings" in data

def test_audit_logs():
    auth_res = client.post("/api/v1/auth/login", json={
        "email": "admin@finflow.ai",
        "password": "Admin123!@#"
    }).json()
    headers = {"Authorization": f"Bearer {auth_res['access_token']}"}

    response = client.get("/api/v1/audit", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert len(data["items"]) > 0
