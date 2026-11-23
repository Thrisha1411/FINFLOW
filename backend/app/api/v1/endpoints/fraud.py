from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, CurrentUserContext, require_role
from backend.app.models.fraud import FraudCase
from backend.app.schemas.fraud import FraudCaseResponse, FraudReviewRequest
from datetime import datetime, timezone

router = APIRouter()

@router.get("/cases", response_model=List[FraudCaseResponse])
def list_fraud_cases(
    status: Optional[str] = None,
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(FraudCase).filter(FraudCase.organization_id == ctx.organization_id)
    if status:
        q = q.filter(FraudCase.status == status)
    return q.order_by(FraudCase.created_at.desc()).all()

@router.get("/cases/{id}", response_model=FraudCaseResponse)
def get_fraud_case(
    id: str,
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fc = db.query(FraudCase).filter(
        FraudCase.id == id,
        FraudCase.organization_id == ctx.organization_id
    ).first()
    if not fc:
        raise HTTPException(status_code=404, detail="Fraud case not found.")
    return fc

@router.patch("/cases/{id}", response_model=FraudCaseResponse)
def update_fraud_case(
    id: str,
    data: FraudReviewRequest,
    ctx: CurrentUserContext = Depends(require_role(["ORG_ADMIN", "FINANCIAL_ANALYST", "FINANCE_MANAGER"])),
    db: Session = Depends(get_db)
):
    fc = db.query(FraudCase).filter(
        FraudCase.id == id,
        FraudCase.organization_id == ctx.organization_id
    ).first()
    if not fc:
        raise HTTPException(status_code=404, detail="Fraud case not found.")

    fc.status = data.status
    if data.notes:
        fc.investigator_notes = ((fc.investigator_notes or "") + f"\n[{ctx.email}]: {data.notes}").strip()
    fc.resolved_by = ctx.user_id
    fc.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(fc)
    return fc
