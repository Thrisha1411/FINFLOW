from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, CurrentUserContext
from backend.app.services.root_cause_service import root_cause_service

router = APIRouter()

@router.get("/analyze", response_model=Dict[str, Any])
def analyze_variance(
    current_month: Optional[str] = None,
    previous_month: Optional[str] = None,
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    curr = current_month or datetime.now(timezone.utc).strftime("%Y-%m")
    return root_cause_service.analyze_variance(
        db=db,
        organization_id=ctx.organization_id,
        current_month=curr,
        previous_month=previous_month
    )
