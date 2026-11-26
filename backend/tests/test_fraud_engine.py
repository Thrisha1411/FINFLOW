from decimal import Decimal
from datetime import datetime, timezone
from backend.app.ml.fraud_model import fraud_engine
from backend.app.ml.categorizer import categorizer


def test_fraud_engine_flags_high_velocity_payment():
    decision = fraud_engine.evaluate_transaction(
        amount=Decimal("12000.00"),
        merchant_name="International Wire Express",
        historical_txs=[
            {"amount": Decimal("150.00"), "created_at": datetime.now(timezone.utc)},
            {"amount": Decimal("200.00"), "created_at": datetime.now(timezone.utc)},
        ],
        current_time=datetime.now(timezone.utc),
        device_is_new=True,
        failed_attempts_count=3
    )

    assert decision["risk_score"] >= 65
    assert decision["risk_level"] in ["HIGH", "CRITICAL"]
    assert decision["recommendation"] in ["STEP_UP_AUTH", "BLOCK", "MANUAL_REVIEW"]


def test_auto_categorization_uses_rules():
    res1 = categorizer.classify("United Airlines flight booking")
    assert res1["category"] in ["Travel", "Transportation"]
    res2 = categorizer.classify("City Electric power utility bill")
    assert res2["category"] == "Utilities"
