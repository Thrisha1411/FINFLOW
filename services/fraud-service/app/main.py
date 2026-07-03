from fastapi import Depends
from sqlalchemy.orm import Session
from finflow.app import create_service_app
from finflow.database import get_db
from finflow.domain_services import FraudEngine
from finflow.repositories import FraudRepository
from finflow.schemas import FraudDecision, FraudSignal
from finflow.security import TokenPrincipal, current_principal

app = create_service_app("fraud-service")


@app.post("/fraud/score", response_model=FraudDecision, tags=["fraud"])
def score(payload: FraudSignal):
    return FraudEngine().score(payload)


@app.get("/fraud/cases", tags=["fraud"])
def cases(principal: TokenPrincipal = Depends(current_principal), db: Session = Depends(get_db)):
    return FraudRepository(db).list_cases(principal.organization_id or "demo-org")

@app.post("/fraud/investigations/{case_id}/decision", tags=["fraud"])
def decision(case_id: str, action: str):
    return {"case_id": case_id, "action": action, "status": "recorded"}

