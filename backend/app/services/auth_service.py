from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
import json
import uuid
from sqlalchemy.orm import Session
from backend.app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from backend.app.core.totp import TOTPManager
from backend.app.models.user import User, UserSession, LoginHistory
from backend.app.models.organization import Organization, OrganizationMember, RoleEnum
from backend.app.models.audit import AuditLog

class AuthService:
    @staticmethod
    def register_user(
        db: Session,
        email: str,
        password: str,
        full_name: str,
        org_name: Optional[str] = None
    ) -> Tuple[User, Organization]:
        existing = db.query(User).filter(User.email == email.lower()).first()
        if existing:
            raise ValueError("An account with this email address already exists.")

        # Create user
        totp_secret = TOTPManager.generate_secret()
        recovery_codes = TOTPManager.generate_recovery_codes()
        user = User(
            email=email.lower(),
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_superuser=False,
            totp_secret=totp_secret,
            is_totp_enabled=False,
            recovery_codes=json.dumps(recovery_codes)
        )
        db.add(user)
        db.flush()

        # Create Organization
        slug = f"org-{uuid.uuid4().hex[:8]}"
        org = Organization(
            name=org_name or f"{full_name}'s Organization",
            slug=slug,
            currency="USD",
            is_active=True
        )
        db.add(org)
        db.flush()

        # Add member as ORG_ADMIN
        member = OrganizationMember(
            organization_id=org.id,
            user_id=user.id,
            role=RoleEnum.ORG_ADMIN
        )
        db.add(member)

        # Audit log
        audit = AuditLog(
            organization_id=org.id,
            actor_id=user.id,
            actor_email=user.email,
            action="USER_REGISTERED",
            resource_type="USER",
            resource_id=user.id,
            metadata_json=json.dumps({"org_id": org.id, "email": user.email})
        )
        db.add(audit)
        db.commit()
        db.refresh(user)
        db.refresh(org)
        return user, org

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        totp_code: Optional[str] = None
    ) -> Dict[str, Any]:
        user = db.query(User).filter(User.email == email.lower()).first()
        if not user:
            raise ValueError("Invalid email or password.")

        now = datetime.now(timezone.utc)
        if user.locked_until and user.locked_until > now:
            minutes_left = int((user.locked_until - now).total_seconds() / 60) + 1
            raise ValueError(f"Account temporarily locked due to excessive failed attempts. Please retry in {minutes_left} minutes.")

        if not verify_password(password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = now + timedelta(minutes=15)
                is_suspicious = True
                reason = "Excessive failed password attempts. Account locked for 15 mins."
            else:
                is_suspicious = False
                reason = "Failed password attempt"

            login_hist = LoginHistory(
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                is_suspicious=is_suspicious,
                reason=reason
            )
            db.add(login_hist)
            db.commit()
            raise ValueError("Invalid email or password.")

        # Check 2FA if enabled
        if user.is_totp_enabled:
            if not totp_code:
                return {
                    "mfa_required": True,
                    "user_id": user.id,
                    "message": "Two-factor authentication code required."
                }
            
            # Check TOTP or backup recovery code
            is_valid_totp = TOTPManager.verify_totp(user.totp_secret, totp_code)
            is_valid_recovery = False
            if not is_valid_totp and user.recovery_codes:
                try:
                    codes = json.loads(user.recovery_codes)
                    if totp_code.upper() in codes:
                        is_valid_recovery = True
                        codes.remove(totp_code.upper())
                        user.recovery_codes = json.dumps(codes)
                except Exception:
                    pass

            if not is_valid_totp and not is_valid_recovery:
                raise ValueError("Invalid two-factor authentication code.")

        # Reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None

        # Check for suspicious device / IP
        last_logins = db.query(LoginHistory).filter(LoginHistory.user_id == user.id).order_by(LoginHistory.created_at.desc()).limit(10).all()
        known_ips = {h.ip_address for h in last_logins if h.ip_address}
        is_suspicious_login = bool(ip_address and known_ips and ip_address not in known_ips)

        login_hist = LoginHistory(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            is_suspicious=is_suspicious_login,
            reason="Unrecognized IP address" if is_suspicious_login else "Successful login"
        )
        db.add(login_hist)

        # Get user primary organization & role
        membership = db.query(OrganizationMember).filter(OrganizationMember.user_id == user.id).first()
        org_id = membership.organization_id if membership else None
        role = membership.role if membership else RoleEnum.CUSTOMER

        # Generate tokens
        session_id = str(uuid.uuid4())
        claims = {
            "org_id": org_id,
            "role": role,
            "email": user.email,
            "full_name": user.full_name,
            "session_id": session_id
        }
        access_token = create_access_token(user.id, claims=claims)
        refresh_token = create_refresh_token(user.id, claims={"session_id": session_id})

        # Persist session
        session_token = f"sess_{uuid.uuid4().hex}"
        session = UserSession(
            id=session_id,
            user_id=user.id,
            session_token=session_token,
            ip_address=ip_address,
            user_agent=user_agent,
            device_name=user_agent[:40] if user_agent else "Browser Session",
            is_active=True,
            expires_at=now + timedelta(days=30)
        )
        db.add(session)
        db.commit()

        return {
            "mfa_required": False,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_totp_enabled": user.is_totp_enabled,
                "role": role,
                "organization_id": org_id
            }
        }

    @staticmethod
    def enable_totp(db: Session, user: User, code: str) -> bool:
        if not user.totp_secret:
            user.totp_secret = TOTPManager.generate_secret()
            
        if not TOTPManager.verify_totp(user.totp_secret, code):
            raise ValueError("Invalid verification code. Please scan the QR code and try again.")
            
        user.is_totp_enabled = True
        if not user.recovery_codes:
            codes = TOTPManager.generate_recovery_codes()
            user.recovery_codes = json.dumps(codes)
        db.commit()
        return True

    @staticmethod
    def disable_totp(db: Session, user: User, password: str) -> bool:
        if not verify_password(password, user.hashed_password):
            raise ValueError("Incorrect password.")
        user.is_totp_enabled = False
        db.commit()
        return True

auth_service = AuthService()
