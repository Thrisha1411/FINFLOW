from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Dict, Any
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, CurrentUserContext
from backend.app.models.category import Category, UserCategoryCorrection
from backend.app.ml.categorizer import categorizer

router = APIRouter()

class CorrectionRequest(BaseModel):
    merchant_name: str
    category_id: str

@router.get("", response_model=List[Dict[str, Any]])
def list_categories(
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cats = db.query(Category).filter(
        or_(Category.organization_id == ctx.organization_id, Category.is_system == True)
    ).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "budget_group": c.budget_group,
            "icon": c.icon,
            "color": c.color,
            "is_system": c.is_system
        }
        for c in cats
    ]

@router.post("/correction")
def register_category_correction(
    data: CorrectionRequest,
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cat = db.query(Category).filter(Category.id == data.category_id).first()
    if not cat:
        return {"error": "Category not found"}

    # Update ML feedback loop in memory
    categorizer.register_correction(data.merchant_name, cat.name)

    # Persist correction in DB
    corr = UserCategoryCorrection(
        organization_id=ctx.organization_id,
        user_id=ctx.user_id,
        merchant_name=data.merchant_name,
        category_id=cat.id
    )
    db.add(corr)
    db.commit()
    return {"message": f"Successfully learned categorization preference for '{data.merchant_name}'."}
