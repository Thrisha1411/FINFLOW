from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, CurrentUserContext
from backend.app.services.budget_service import budget_service

router = APIRouter()

@router.get("/50-30-20", response_model=Dict[str, Any])
def get_50_30_20(
    month: Optional[str] = None,
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_month = month or datetime.now(timezone.utc).strftime("%Y-%m")
    return budget_service.get_50_30_20_analysis(db, ctx.organization_id, target_month)

@router.get("/health-score", response_model=Dict[str, Any])
def get_health_score(
    month: Optional[str] = None,
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_month = month or datetime.now(timezone.utc).strftime("%Y-%m")
    return budget_service.calculate_health_score(db, ctx.organization_id, target_month)

@router.get("/next-month-plan", response_model=Dict[str, Any])
def get_next_month_plan(
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return budget_service.generate_next_month_plan(db, ctx.organization_id)
