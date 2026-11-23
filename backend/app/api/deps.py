from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.app.core.database import get_db
from backend.app.core.security import decode_token
from backend.app.models.user import User
from backend.app.models.organization import OrganizationMember

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class CurrentUserContext:
    def __init__(self, user: User, organization_id: str, role: str):
        self.user = user
        self.user_id = user.id
        self.email = user.email
        self.organization_id = organization_id
        self.role = role

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> CurrentUserContext:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    org_id = payload.get("org_id")
    role = payload.get("role")

    # If org_id not in token claims, retrieve from membership
    if not org_id:
        membership = db.query(OrganizationMember).filter(OrganizationMember.user_id == user.id).first()
        if membership:
            org_id = membership.organization_id
            role = membership.role

    return CurrentUserContext(user=user, organization_id=org_id, role=role or "CUSTOMER")

def require_role(allowed_roles: List[str]):
    def role_checker(ctx: CurrentUserContext = Depends(get_current_user)) -> CurrentUserContext:
        if ctx.user.is_superuser:
            return ctx
        if ctx.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {', '.join(allowed_roles)}."
            )
        return ctx
    return role_checker
