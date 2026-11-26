from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from finflow.app import create_service_app
from finflow.database import get_db
from finflow.repositories import UserRepository
from finflow.domain_services import AuthService
from finflow.schemas import RegisterRequest, LoginRequest, AuthToken
from finflow.security import request_fingerprint, new_mfa_secret

app = create_service_app("auth-service")


@app.post("/auth/register", response_model=AuthToken, tags=["auth"])
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = AuthService(UserRepository(db)).register(payload.email, payload.password, payload.full_name, payload.organization_id)
        token = AuthService(UserRepository(db)).login(payload.email, payload.password, None)
        return AuthToken(access_token=token)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/auth/login", response_model=AuthToken, tags=["auth"])
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    fingerprint = request_fingerprint(request)
    try:
        token = AuthService(UserRepository(db)).login(payload.email, payload.password, payload.mfa_code)
        return AuthToken(access_token=token)
    except PermissionError as exc:
        return AuthToken(access_token="", requires_mfa=True)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc), headers={"x-login-ip": fingerprint.get("ip") or ""}) from exc


@app.post("/auth/mfa/setup", tags=["auth"])
def setup_mfa():
    secret = new_mfa_secret()
    return {"secret": secret, "otpauth_hint": "Store this in an authenticator app, then verify with /auth/login."}

