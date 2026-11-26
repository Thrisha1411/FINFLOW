from fastapi import Depends
from sqlalchemy.orm import Session
from finflow.app import create_service_app
from finflow.database import get_db
from finflow.repositories import AuditRepository
from finflow.security import TokenPrincipal, current_principal

app = create_service_app("audit-service")


@app.get("/audit/logs", tags=["audit"])
def logs(q: str | None = None, principal: TokenPrincipal = Depends(current_principal), db: Session = Depends(get_db)):
    return AuditRepository(db).search(principal.organization_id, q)

@app.post("/audit/logs", tags=["audit"])
def create_log(action: str, resource_type: str, resource_id: str | None = None):
    return {"action": action, "resource_type": resource_type, "resource_id": resource_id, "status": "accepted"}

