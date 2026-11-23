from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, CurrentUserContext
from backend.app.services.simulator_service import simulator_service

router = APIRouter()

class SimulationInput(BaseModel):
    shopping_reduction_pct: float = 0.0
    dining_reduction_pct: float = 0.0
    income_delta: float = 0.0
    subscriptions_to_cancel: List[str] = []
    additional_monthly_savings: float = 0.0

@router.post("/simulate", response_model=Dict[str, Any])
def simulate(
    data: SimulationInput,
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return simulator_service.run_simulation(
        db=db,
        organization_id=ctx.organization_id,
        shopping_reduction_pct=data.shopping_reduction_pct,
        dining_reduction_pct=data.dining_reduction_pct,
        income_delta=data.income_delta,
        subscriptions_to_cancel=data.subscriptions_to_cancel,
        additional_monthly_savings=data.additional_monthly_savings
    )
