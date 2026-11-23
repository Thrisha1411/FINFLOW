from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, CurrentUserContext
from backend.app.services.assistant_service import assistant_service

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None

@router.post("/chat", response_model=Dict[str, Any])
def chat(
    data: ChatRequest,
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return assistant_service.ask(
        db=db,
        organization_id=ctx.organization_id,
        user_id=ctx.user_id,
        query=data.query,
        conversation_id=data.conversation_id
    )
