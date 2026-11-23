from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
import json
import uuid
from sqlalchemy.orm import Session
from backend.app.models.subscription import Subscription, SubscriptionPriceHistory
from backend.app.models.transaction import Transaction
from backend.app.services.audit_service import audit_service

class SubscriptionService:
    @staticmethod
    def list_subscriptions(db: Session, organization_id: str) -> List[Subscription]:
        return db.query(Subscription).filter(
            Subscription.organization_id == organization_id
        ).order_by(Subscription.next_renewal_date.asc()).all()

    @staticmethod
    def create_subscription(
        db: Session,
        organization_id: str,
        user_id: str,
        merchant_name: str,
        amount: Decimal,
        billing_cycle: str = "MONTHLY",
        next_renewal_date: datetime = None,
        category_id: Optional[str] = None
    ) -> Subscription:
        if next_renewal_date is None:
            next_renewal_date = datetime.now(timezone.utc) + timedelta(days=30)

        sub = Subscription(
            organization_id=organization_id,
            user_id=user_id,
            merchant_name=merchant_name,
            amount=amount,
            currency="USD",
            billing_cycle=billing_cycle,
            next_renewal_date=next_renewal_date,
            category_id=category_id,
            status="ACTIVE",
            is_auto_detected=False
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return sub

    @staticmethod
    def detect_recurring_transactions(db: Session, organization_id: str) -> List[Dict[str, Any]]:
        """
        Scans transaction history to identify recurring payments (same merchant, recurring monthly cadence).
        """
        txs = db.query(Transaction).filter(
            Transaction.organization_id == organization_id,
            Transaction.status == "SUCCESS"
        ).order_by(Transaction.created_at.desc()).all()

        merchant_txs: Dict[str, List[Transaction]] = {}
        for tx in txs:
            merchant_txs.setdefault(tx.merchant_name, []).append(tx)

        detected = []
        for merchant, items in merchant_txs.items():
            if len(items) >= 2:
                # Check interval
                d1 = items[0].created_at
                d2 = items[1].created_at
                interval_days = abs((d1 - d2).days)
                if 25 <= interval_days <= 35:
                    detected.append({
                        "merchant_name": merchant,
                        "amount": float(items[0].amount),
                        "frequency": "MONTHLY",
                        "detected_instances": len(items),
                        "last_billed": items[0].created_at.isoformat(),
                        "estimated_next_bill": (items[0].created_at + timedelta(days=30)).isoformat()
                    })

        return detected

    @staticmethod
    def get_subscription_analytics(db: Session, organization_id: str) -> Dict[str, Any]:
        subs = db.query(Subscription).filter(
            Subscription.organization_id == organization_id,
            Subscription.status == "ACTIVE"
        ).all()

        monthly_total = Decimal("0.00")
        annual_total = Decimal("0.00")
        for s in subs:
            if s.billing_cycle == "ANNUAL":
                annual_total += s.amount
                monthly_total += (s.amount / 12)
            else:
                monthly_total += s.amount
                annual_total += (s.amount * 12)

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        upcoming_renewals = []
        for s in subs:
            r_date = s.next_renewal_date
            if r_date and r_date.tzinfo is not None:
                r_date = r_date.replace(tzinfo=None)
            if r_date and r_date >= now and (r_date - now).days <= 30:
                upcoming_renewals.append({
                    "id": s.id,
                    "merchant_name": s.merchant_name,
                    "amount": float(s.amount),
                    "next_renewal_date": s.next_renewal_date.isoformat(),
                    "days_until_renewal": max(0, (r_date - now).days)
                })
        upcoming_renewals.sort(key=lambda x: x["days_until_renewal"])

        return {
            "active_subscriptions_count": len(subs),
            "monthly_recurring_spend": float(round(monthly_total, 2)),
            "annual_projected_spend": float(round(annual_total, 2)),
            "upcoming_renewals_30d": upcoming_renewals
        }

subscription_service = SubscriptionService()
