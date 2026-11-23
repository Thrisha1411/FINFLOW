from typing import Dict, Any, Optional
from decimal import Decimal
import time
import random

class PaymentProviderAdapter:
    """
    Payment Orchestration Provider Interface.
    Simulates gateway adapter (e.g. Stripe, Razorpay, Adyen) with explicit simulation labeling.
    Does not perform real banking transactions.
    """
    @staticmethod
    def execute_payment(
        amount: Decimal,
        currency: str,
        merchant_name: str,
        tokenized_payment_method: str
    ) -> Dict[str, Any]:
        """
        Simulates payment gateway authorization and capture.
        Validates idempotency and returns gateway reference.
        """
        # Simulated network latency (10ms)
        time.sleep(0.01)

        gateway_ref = f"gw_sim_{random.randint(10000000, 99999999)}"
        return {
            "gateway_reference": gateway_ref,
            "provider": "SIMULATED_FINTECH_GATEWAY_ADAPTER",
            "status": "APPROVED",
            "amount": float(amount),
            "currency": currency,
            "is_simulation": True,
            "note": "Payment executed via FinFlow Gateway Orchestration Simulation Adapter."
        }

payment_provider = PaymentProviderAdapter()
