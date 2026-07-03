from finflow.domain_services import FraudEngine
from finflow.schemas import FraudSignal


def test_fraud_engine_flags_high_velocity_payment():
    decision = FraudEngine().score(
        FraudSignal(
            transaction_id="t1",
            user_id="u1",
            amount=12000,
            merchant="International Wire",
            prior_24h_count=7,
            prior_24h_amount=22000,
        )
    )

    assert decision.risk_score >= 75
    assert "manual approval" in decision.recommendation.lower()


def test_auto_categorization_uses_rules():
    assert FraudEngine().categorize("United Air") == "Travel"
    assert FraudEngine().categorize("City Electric") == "Utilities"

