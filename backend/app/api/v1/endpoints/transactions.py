from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from decimal import Decimal
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, CurrentUserContext, require_role
from backend.app.models.transaction import Transaction
from backend.app.schemas.transaction import TransactionCreate, TransactionResponse, RefundCreate, RefundResponse
from backend.app.services.transaction_service import transaction_service

router = APIRouter()

@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    status: Optional[str] = None,
    category_id: Optional[str] = None,
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Transaction).filter(Transaction.organization_id == ctx.organization_id)
    if search:
        q = q.filter(Transaction.merchant_name.ilike(f"%{search}%") | Transaction.reference_id.ilike(f"%{search}%"))
    if status:
        q = q.filter(Transaction.status == status)
    if category_id:
        q = q.filter(Transaction.category_id == category_id)

    txs = q.order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()
    return txs

@router.post("", response_model=TransactionResponse)
def create_transaction(
    data: TransactionCreate,
    request: Request = None,
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip = request.client.host if (request and request.client) else "127.0.0.1"
    tx = transaction_service.create_transaction(
        db=db,
        organization_id=ctx.organization_id,
        user_id=ctx.user_id,
        amount=data.amount,
        merchant_name=data.merchant_name,
        currency=data.currency,
        description=data.description,
        category_id=data.category_id,
        idempotency_key=data.idempotency_key,
        payment_method=data.payment_method,
        ip_address=ip,
        actor_email=ctx.email
    )
    return tx

@router.get("/{id}", response_model=TransactionResponse)
def get_transaction(
    id: str,
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx = db.query(Transaction).filter(
        Transaction.id == id,
        Transaction.organization_id == ctx.organization_id
    ).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    return tx

@router.post("/{id}/approve", response_model=TransactionResponse)
def approve_transaction(
    id: str,
    ctx: CurrentUserContext = Depends(require_role(["ORG_ADMIN", "FINANCE_MANAGER", "SUPER_ADMIN"])),
    db: Session = Depends(get_db)
):
    try:
        tx = transaction_service.approve_transaction(
            db=db,
            transaction_id=id,
            approver_id=ctx.user_id,
            approver_email=ctx.email
        )
        return tx
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{id}/refund", response_model=RefundResponse)
def refund_transaction(
    id: str,
    data: RefundCreate,
    ctx: CurrentUserContext = Depends(require_role(["ORG_ADMIN", "FINANCE_MANAGER", "SUPER_ADMIN"])),
    db: Session = Depends(get_db)
):
    try:
        refund = transaction_service.process_refund(
            db=db,
            transaction_id=id,
            amount=data.amount,
            reason=data.reason,
            actor_id=ctx.user_id,
            actor_email=ctx.email
        )
        return refund
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
