from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import pyotp

from .config import get_settings


class Role(StrEnum):
    admin = "Admin"
    analyst = "Analyst"
    finance_manager = "Finance Manager"
    auditor = "Auditor"
    customer = "Customer"


class TokenPrincipal(BaseModel):
    sub: str
    email: str
    roles: list[str]
    organization_id: str | None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(subject: str, email: str, roles: list[str], organization_id: str | None = None) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "email": email,
        "roles": roles,
        "organization_id": organization_id,
        "iss": settings.jwt_issuer,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> TokenPrincipal:
    try:
        payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"], issuer=get_settings().jwt_issuer)
        return TokenPrincipal(
            sub=payload["sub"],
            email=payload["email"],
            roles=list(payload.get("roles", [])),
            organization_id=payload.get("organization_id"),
        )
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc


def current_principal(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> TokenPrincipal:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return decode_token(credentials.credentials)


def require_roles(*roles: Role):
    accepted = {role.value for role in roles}

    def dependency(principal: TokenPrincipal = Depends(current_principal)) -> TokenPrincipal:
        if not accepted.intersection(set(principal.roles)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return principal

    return dependency


def new_mfa_secret() -> str:
    return pyotp.random_base32()


def verify_mfa(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code, valid_window=1)


def request_fingerprint(request: Request) -> dict[str, str | None]:
    return {
        "ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "device_id": request.headers.get("x-device-id"),
    }

