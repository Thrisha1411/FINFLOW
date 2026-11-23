from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
import json
import uuid
from sqlalchemy.orm import Session
from backend.app.models.audit import AuditLog

class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        organization_id: str,
        actor_id: str,
        actor_email: Optional[str],
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Appends an immutable audit record. Never modifies existing rows.
        """
        audit = AuditLog(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            actor_id=actor_id,
            actor_email=actor_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            request_id=request_id or f"REQ-{uuid.uuid4().hex[:10]}",
            metadata_json=json.dumps(metadata or {}),
            created_at=datetime.now(timezone.utc)
        )
        db.add(audit)
        db.commit()
        return audit

    @staticmethod
    def get_logs(
        db: Session,
        organization_id: str,
        skip: int = 0,
        limit: int = 100,
        action: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> Tuple[List[AuditLog], int]:
        q = db.query(AuditLog).filter(AuditLog.organization_id == organization_id)
        if action:
            q = q.filter(AuditLog.action.ilike(f"%{action}%"))
        if resource_type:
            q = q.filter(AuditLog.resource_type == resource_type)
        total = q.count()
        logs = q.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
        return logs, total

audit_service = AuditService()
