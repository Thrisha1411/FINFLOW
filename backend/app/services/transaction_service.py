from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
import json
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from backend.app.models.transaction import Transaction, TransactionEvent, Refund
from backend.app.models.fraud import FraudCase, FraudSignal
from backend.app.models.notification import Notification
from backend.app.ml.fraud_model import fraud_engine
from backend.app.ml.categorizer import categorizer
from backend.app.models.category import Category
from backend.app.services.audit_service import audit_service
from backend.app.core.events import event_bus

class TransactionService:
    @staticmethod
    def create_transaction(
        db: Session,
        organization_id: str,
        user_id: str,
        amount: Decimal,
        merchant_name: str,
        currency: str = "USD",
        description: Optional[str] = None,
        category_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        payment_method: str = "CORPORATE_CARD",
        ip_address: Optional[str] = None,
        device_id: Optional[str] = None,
        actor_email: Optional[str] = None
    ) -> Transaction:
        # 1. Idempotency Check
        if idempotency_key:
            existing_tx = db.query(Transaction).filter(
                Transaction.organization_id == organization_id,
                Transaction.idempotency_key == idempotency_key
            ).first()
            if existing_tx:
                return existing_tx

        now = datetime.now(timezone.utc)
        ref_id = f"TXN-{now.strftime('%Y%m%d%H%M')}-{uuid.uuid4().hex[:6].upper()}"

        # 2. Auto-categorize if category_id missing
        if not category_id:
            cat_result = categorizer.classify(merchant_name, description)
            matched_cat = db.query(Category).filter(
                or_(Category.organization_id == organization_id, Category.is_system == True),
                Category.name == cat_result["category"]
            ).first()
            if matched_cat:
                category_id = matched_cat.id

        # 3. State: INITIATED
        tx = Transaction(
            organization_id=organization_id,
            user_id=user_id,
            reference_id=ref_id,
            idempotency_key=idempotency_key,
            amount=amount,
            currency=currency.upper(),
            merchant_name=merchant_name,
            description=description,
            category_id=category_id,
            status="INITIATED",
            risk_score=0.0,
            risk_level="LOW",
            payment_method=payment_method,
            ip_address=ip_address,
            device_id=device_id,
            created_at=now,
            updated_at=now
        )
        db.add(tx)
        db.flush()

        db.add(TransactionEvent(
            transaction_id=tx.id,
            from_status=None,
            to_status="INITIATED",
            reason="Transaction request accepted for validation"
        ))

        # 4. State: VALIDATING
        tx.status = "VALIDATING"
        db.add(TransactionEvent(
            transaction_id=tx.id,
            from_status="INITIATED",
            to_status="VALIDATING",
            reason="Validated amount, currency, and account constraints"
        ))

        # 5. State: RISK_ANALYSIS
        # Fetch historical transactions for behavioral analysis
        history_records = db.query(Transaction).filter(
            Transaction.organization_id == organization_id,
            Transaction.id != tx.id
        ).order_by(Transaction.created_at.desc()).limit(100).all()
        
        hist_data = [
            {"amount": float(h.amount), "created_at": h.created_at, "device_id": h.device_id}
            for h in history_records
        ]
        
        device_is_new = bool(device_id and not any(h.device_id == device_id for h in history_records if h.device_id))
        failed_count = sum(1 for h in history_records[:5] if h.status == "FAILED")

        fraud_eval = fraud_engine.evaluate_transaction(
            amount=amount,
            merchant_name=merchant_name,
            historical_txs=hist_data,
            current_time=now,
            device_is_new=device_is_new,
            failed_attempts_count=failed_count
        )

        tx.risk_score = fraud_eval["risk_score"]
        tx.risk_level = fraud_eval["risk_level"]

        db.add(TransactionEvent(
            transaction_id=tx.id,
            from_status="VALIDATING",
            to_status="RISK_ANALYSIS",
            reason=f"Risk analysis complete: score={tx.risk_score}, level={tx.risk_level}",
            metadata_json=json.dumps(fraud_eval)
        ))

        # 6. Branch according to risk assessment and recommendation
        if fraud_eval["recommendation"] in ("BLOCK", "MANUAL_REVIEW", "STEP_UP_AUTH") or fraud_eval["risk_level"] in ("HIGH", "CRITICAL"):
            if fraud_eval["recommendation"] == "BLOCK":
                tx.status = "FLAGGED"
                reason_msg = "Blocked by automated fraud intelligence engine"
            else:
                tx.status = "PENDING_APPROVAL"
                reason_msg = "Held for manual financial review due to elevated risk evaluation"

            db.add(TransactionEvent(
                transaction_id=tx.id,
                from_status="RISK_ANALYSIS",
                to_status=tx.status,
                reason=reason_msg
            ))

            # Create Fraud Case
            fraud_case = FraudCase(
                organization_id=organization_id,
                transaction_id=tx.id,
                risk_score=fraud_eval["risk_score"],
                risk_level=fraud_eval["risk_level"],
                recommendation=fraud_eval["recommendation"],
                status="OPEN",
                investigator_notes="; ".join(fraud_eval["supporting_evidence"]),
                created_at=now
            )
            db.add(fraud_case)
            db.flush()

            for trig in fraud_eval["triggered_rules"]:
                db.add(FraudSignal(
                    fraud_case_id=fraud_case.id,
                    rule_code=trig["rule_code"],
                    signal_name=trig["signal_name"],
                    description=trig["description"],
                    severity=trig["severity"],
                    weight=trig["weight"]
                ))

            # Dispatch notification
            db.add(Notification(
                organization_id=organization_id,
                user_id=user_id,
                type="FRAUD_ALERT",
                title=f"Transaction {tx.status}: {merchant_name}",
                message=f"Transaction of ${abs(amount):,.2f} at {merchant_name} has a risk score of {tx.risk_score}/100.",
                data_json=json.dumps({"transaction_id": tx.id, "risk_score": tx.risk_score})
            ))
            event_bus.publish("fraud.detected", {"transaction_id": tx.id, "risk_score": tx.risk_score}, organization_id, user_id)

        else:
            # 7. Low/Medium Risk -> PROCESSING -> SUCCESS
            tx.status = "PROCESSING"
            db.add(TransactionEvent(
                transaction_id=tx.id,
                from_status="RISK_ANALYSIS",
                to_status="PROCESSING",
                reason="Dispatched to simulated payment processor"
            ))

            tx.status = "SUCCESS"
            db.add(TransactionEvent(
                transaction_id=tx.id,
                from_status="PROCESSING",
                to_status="SUCCESS",
                reason="Payment successfully authorized and captured"
            ))
            event_bus.publish("transaction.completed", {"transaction_id": tx.id, "amount": float(amount)}, organization_id, user_id)

        # 8. Audit logging
        audit_service.log_action(
            db=db,
            organization_id=organization_id,
            actor_id=user_id,
            actor_email=actor_email,
            action=f"TRANSACTION_{tx.status}",
            resource_type="TRANSACTION",
            resource_id=tx.id,
            ip_address=ip_address,
            metadata={"amount": float(amount), "merchant": merchant_name, "status": tx.status, "risk_score": tx.risk_score}
        )

        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def approve_transaction(db: Session, transaction_id: str, approver_id: str, approver_email: str) -> Transaction:
        tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not tx:
            raise ValueError("Transaction not found.")
        if tx.status not in ("PENDING_APPROVAL", "FLAGGED"):
            raise ValueError(f"Cannot approve transaction with status {tx.status}.")

        old_status = tx.status
        tx.status = "SUCCESS"
        tx.updated_at = datetime.now(timezone.utc)

        db.add(TransactionEvent(
            transaction_id=tx.id,
            from_status=old_status,
            to_status="SUCCESS",
            reason=f"Approved manually by financial manager {approver_email}"
        ))

        # Update fraud case if present
        if tx.fraud_case:
            tx.fraud_case.status = "RESOLVED_BENIGN"
            tx.fraud_case.resolved_by = approver_id
            tx.fraud_case.resolved_at = datetime.now(timezone.utc)
            tx.fraud_case.investigator_notes = (tx.fraud_case.investigator_notes or "") + f"\nApproved manually by {approver_email}."

        audit_service.log_action(
            db=db,
            organization_id=tx.organization_id,
            actor_id=approver_id,
            actor_email=approver_email,
            action="TRANSACTION_MANUALLY_APPROVED",
            resource_type="TRANSACTION",
            resource_id=tx.id,
            metadata={"old_status": old_status, "new_status": "SUCCESS"}
        )

        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def process_refund(db: Session, transaction_id: str, amount: Decimal, reason: str, actor_id: str, actor_email: str) -> Refund:
        tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not tx:
            raise ValueError("Transaction not found.")
        if tx.status != "SUCCESS":
            raise ValueError("Only successful transactions can be refunded.")
        if amount > tx.amount:
            raise ValueError(f"Refund amount (${amount}) exceeds original transaction amount (${tx.amount}).")

        refund = Refund(
            organization_id=tx.organization_id,
            transaction_id=tx.id,
            amount=amount,
            currency=tx.currency,
            reason=reason,
            status="COMPLETED"
        )
        db.add(refund)

        # If full refund, update status
        if amount == tx.amount:
            tx.status = "REFUNDED"
            db.add(TransactionEvent(
                transaction_id=tx.id,
                from_status="SUCCESS",
                to_status="REFUNDED",
                reason=f"Full refund issued: {reason}"
            ))

        audit_service.log_action(
            db=db,
            organization_id=tx.organization_id,
            actor_id=actor_id,
            actor_email=actor_email,
            action="REFUND_ISSUED",
            resource_type="REFUND",
            resource_id=refund.id,
            metadata={"transaction_id": tx.id, "amount": float(amount), "reason": reason}
        )

        db.commit()
        db.refresh(refund)
        return refund

transaction_service = TransactionService()
