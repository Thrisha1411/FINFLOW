from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from decimal import Decimal
from pydantic import BaseModel
from datetime import datetime
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, CurrentUserContext
from backend.app.services.subscription_service import subscription_service

router = APIRouter()

class SubscriptionCreate(BaseModel):
    merchant_name: str
    amount: Decimal
    billing_cycle: str = "MONTHLY"
    category_id: Optional[str] = None

@router.get("", response_model=List[Dict[str, Any]])
def list_subs(
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subs = subscription_service.list_subscriptions(db, ctx.organization_id)
    return [
        {
            "id": s.id,
            "merchant_name": s.merchant_name,
            "amount": float(s.amount),
            "currency": s.currency,
            "billing_cycle": s.billing_cycle,
            "next_renewal_date": s.next_renewal_date.isoformat(),
            "status": s.status,
            "is_auto_detected": s.is_auto_detected
        }
        for s in subs
    ]

@router.post("")
def create_sub(
    data: SubscriptionCreate,
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sub = subscription_service.create_subscription(
        db=db,
        organization_id=ctx.organization_id,
        user_id=ctx.user_id,
        merchant_name=data.merchant_name,
        amount=data.amount,
        billing_cycle=data.billing_cycle,
        category_id=data.category_id
    )
    return {"message": "Subscription created", "id": sub.id}

@router.get("/analytics", response_model=Dict[str, Any])
def get_analytics(
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return subscription_service.get_subscription_analytics(db, ctx.organization_id)

@router.get("/detected", response_model=List[Dict[str, Any]])
def get_detected(
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return subscription_service.detect_recurring_transactions(db, ctx.organization_id)
