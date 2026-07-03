from datetime import datetime, timedelta, timezone
from finflow.app import create_service_app

app = create_service_app("subscription-service")


@app.get("/subscriptions", tags=["subscriptions"])
def list_subscriptions():
    return [
        {"merchant": "Notion", "amount": 8000, "currency": "INR", "cadence": "monthly", "next_renewal_at": (datetime.now(timezone.utc) + timedelta(days=12)).isoformat(), "risk": "unused"},
        {"merchant": "AWS India", "amount": 153000, "currency": "INR", "cadence": "monthly", "next_renewal_at": (datetime.now(timezone.utc) + timedelta(days=4)).isoformat(), "risk": "price_increase"},
    ]


@app.post("/subscriptions/detect", tags=["subscriptions"])
def detect_recurring():
    return {"detected": 14, "renewal_alerts": 3, "price_increase_alerts": 2}
