from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from backend.app.core.database import get_db
from backend.app.core.totp import TOTPManager
from backend.app.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse, TOTPSetupResponse, TOTPVerifyRequest
from backend.app.services.auth_service import auth_service
from backend.app.api.deps import get_current_user, CurrentUserContext
from backend.app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=Dict[str, Any])
def register(data: UserRegister, db: Session = Depends(get_db)):
    try:
        user, org = auth_service.register_user(
            db=db,
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            org_name=data.org_name
        )
        return {
            "message": "User and organization successfully registered.",
            "user_id": user.id,
            "organization_id": org.id,
            "organization_name": org.name
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Dict[str, Any])
def login(data: UserLogin, request: Request = None, db: Session = Depends(get_db)):
    ip = request.client.host if (request and request.client) else "127.0.0.1"
    ua = request.headers.get("user-agent", "Unknown") if (request and request.headers) else "Unknown"
    try:
        result = auth_service.authenticate_user(
            db=db,
            email=data.email,
            password=data.password,
            ip_address=ip,
            user_agent=ua,
            totp_code=data.totp_code
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me", response_model=Dict[str, Any])
def get_me(ctx: CurrentUserContext = Depends(get_current_user)):
    return {
        "id": ctx.user.id,
        "email": ctx.user.email,
        "full_name": ctx.user.full_name,
        "is_totp_enabled": ctx.user.is_totp_enabled,
        "role": ctx.role,
        "organization_id": ctx.organization_id
    }

@router.post("/2fa/setup", response_model=TOTPSetupResponse)
def setup_2fa(ctx: CurrentUserContext = Depends(get_current_user), db: Session = Depends(get_db)):
    secret = TOTPManager.generate_secret()
    ctx.user.totp_secret = secret
    db.commit()
    uri = TOTPManager.get_provisioning_uri(secret, ctx.user.email, settings.TOTP_ISSUER)
    recovery_codes = TOTPManager.generate_recovery_codes()
    return TOTPSetupResponse(secret=secret, provisioning_uri=uri, recovery_codes=recovery_codes)

@router.post("/2fa/enable")
def enable_2fa(data: TOTPVerifyRequest, ctx: CurrentUserContext = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        auth_service.enable_totp(db=db, user=ctx.user, code=data.code)
        return {"message": "Two-factor authentication successfully enabled."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
