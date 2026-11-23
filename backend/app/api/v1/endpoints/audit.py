from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, CurrentUserContext
from backend.app.services.audit_service import audit_service

router = APIRouter()

@router.get("", response_model=Dict[str, Any])
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logs, total = audit_service.get_logs(
        db=db,
        organization_id=ctx.organization_id,
        skip=skip,
        limit=limit,
        action=action,
        resource_type=resource_type
    )
    return {
        "total": total,
        "items": [
            {
                "id": l.id,
                "actor_id": l.actor_id,
                "actor_email": l.actor_email,
                "action": l.action,
                "resource_type": l.resource_type,
                "resource_id": l.resource_id,
                "ip_address": l.ip_address,
                "request_id": l.request_id,
                "created_at": l.created_at.isoformat()
            }
            for l in logs
        ]
    }
